#!/usr/bin/env python3
"""Render a PM document (project plan, status report, change request...) from JSON
into one self-contained HTML file.

Usage:
    python3 render_report.py input.json output.html

See references/html-report.md for the JSON format. Only the standard library is used.
Warnings (bad dates, unknown block types...) are printed to stderr; the script still
renders what it can so a single typo doesn't block the whole document.
"""
import html
import json
import re
import sys
from datetime import date, datetime, timedelta

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)


# ---------------------------------------------------------------- text helpers

def esc(s):
    return html.escape("" if s is None else str(s))


def inline(s):
    """Escape then apply **bold**, *italic*, `code`."""
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])", r"<em>\1</em>", s)
    return s


def md(text):
    """Tiny markdown: paragraphs, '- ' bullets, '1. ' numbered, '### ' subheads."""
    if text is None:
        return ""
    if isinstance(text, list):
        text = "\n".join(str(t) for t in text)
    out, para, lst, lst_tag = [], [], [], None

    def flush_para():
        if para:
            out.append("<p>" + "<br>".join(inline(p) for p in para) + "</p>")
            para.clear()

    def flush_list():
        nonlocal lst_tag
        if lst:
            out.append(f"<{lst_tag}>" + "".join(f"<li>{inline(i)}</li>" for i in lst) + f"</{lst_tag}>")
            lst.clear()
        lst_tag = None

    for raw in str(text).split("\n"):
        line = raw.strip()
        m_ul = re.match(r"^[-*•]\s+(.*)", line)
        m_ol = re.match(r"^\d+[.)]\s+(.*)", line)
        if not line:
            flush_para(); flush_list()
        elif line.startswith("### "):
            flush_para(); flush_list()
            out.append(f"<h4>{inline(line[4:])}</h4>")
        elif m_ul or m_ol:
            flush_para()
            tag = "ul" if m_ul else "ol"
            if lst_tag and lst_tag != tag:
                flush_list()
            lst_tag = tag
            lst.append((m_ul or m_ol).group(1))
        else:
            flush_list()
            para.append(line)
    flush_para(); flush_list()
    return "\n".join(out)


def parse_date(s, where=""):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(s).strip(), fmt).date()
        except ValueError:
            pass
    warn(f"Ngày không hợp lệ '{s}' {where} (dùng YYYY-MM-DD)")
    return None


def vn_date(d, year=True):
    return d.strftime("%d/%m/%Y" if year else "%d/%m") if d else ""


# ---------------------------------------------------------------- badges

BADGES = {
    "danger": ["cao", "high", "đỏ", "red", "critical", "nghiêm trọng", "trễ", "blocked", "bị chặn", "rất cao", "quá tải"],
    "warn": ["trung bình", "tb", "medium", "vàng", "amber", "yellow", "có nguy cơ", "at risk", "cần theo dõi", "sát"],
    "ok": ["thấp", "low", "xanh", "green", "xong", "done", "hoàn thành", "đúng tiến độ", "on track", "đã duyệt", "đã chốt", "ok"],
    "info": ["đang làm", "in progress", "đang thực hiện", "đang xử lý"],
    "neutral": ["chưa bắt đầu", "to do", "todo", "chưa làm", "mở", "open", "đề xuất", "chờ duyệt", "pending"],
    "must": ["must", "must have"],
    "should": ["should", "should have"],
    "could": ["could", "could have"],
    "wont": ["won't", "wont", "won't have", "won’t"],
}
BADGE_LOOKUP = {v: k for k, vs in BADGES.items() for v in vs}
RAG_NORMAL = {"green": "ok", "xanh": "ok", "amber": "warn", "vàng": "warn", "yellow": "warn", "red": "danger", "đỏ": "danger"}
RAG_LABEL = {"ok": "Xanh", "warn": "Vàng", "danger": "Đỏ"}


def cell(v):
    if v is None:
        return ""
    s = str(v).strip()
    tone = BADGE_LOOKUP.get(s.lower())
    if tone:
        return f'<span class="badge b-{tone}">{esc(s)}</span>'
    return inline(s)


def is_num(v):
    if isinstance(v, (int, float)):
        return True
    return bool(re.fullmatch(r"[+\-−]?[\d.,]+\s*(%|MD|MM|md|ngày|h)?", str(v).strip())) if v not in (None, "") else False


# ---------------------------------------------------------------- blocks

def b_text(b):
    return f'<div class="prose">{md(b.get("content"))}</div>'


def b_list(b):
    tag = "ol" if b.get("ordered") else "ul"
    return f'<{tag} class="plain">' + "".join(f"<li>{inline(i)}</li>" for i in b.get("items", [])) + f"</{tag}>"


def b_checklist(b):
    rows = []
    for it in b.get("items", []):
        if isinstance(it, str):
            it = {"text": it}
        done = bool(it.get("done"))
        rows.append(f'<li class="{"done" if done else ""}"><span class="box">{"✓" if done else ""}</span>'
                    f'<span>{inline(it.get("text"))}</span></li>')
    return '<ul class="checklist">' + "".join(rows) + "</ul>"


def b_callout(b):
    tone = b.get("tone", "info")
    icon = {"info": "ℹ️", "tip": "💡", "warn": "⚠️", "danger": "⛔", "success": "✅"}.get(tone, "ℹ️")
    title = f'<div class="co-title">{inline(b["title"])}</div>' if b.get("title") else ""
    return (f'<div class="callout co-{esc(tone)}"><div class="co-icon">{icon}</div>'
            f'<div class="co-body">{title}{md(b.get("content"))}</div></div>')


def b_kpis(b):
    items = []
    for k in b.get("items", []):
        tone = k.get("tone", "")
        note = f'<div class="kpi-note">{inline(k["note"])}</div>' if k.get("note") else ""
        items.append(f'<div class="kpi kpi-{esc(tone)}"><div class="kpi-label">{inline(k.get("label"))}</div>'
                     f'<div class="kpi-value">{inline(k.get("value"))}</div>{note}</div>')
    return '<div class="kpis">' + "".join(items) + "</div>"


def b_table(b):
    cols = b.get("columns", [])
    rows = b.get("rows", [])
    for i, r in enumerate(rows):
        if len(r) != len(cols):
            warn(f"Bảng '{b.get('caption', cols[:2])}' dòng {i + 1} có {len(r)} ô, cần {len(cols)}")
    numeric = []
    for ci in range(len(cols)):
        vals = [r[ci] for r in rows if ci < len(r) and r[ci] not in (None, "", "–", "-", "—")]
        numeric.append(bool(vals) and all(is_num(v) for v in vals))
    head = "".join(f'<th class="{"num" if numeric[i] else ""}">{inline(c)}</th>' for i, c in enumerate(cols))
    body = []
    last = len(rows) - 1
    for ri, r in enumerate(rows):
        cls = "total" if (b.get("total_row") and ri == last) else ""
        tds = "".join(f'<td class="{"num" if ci < len(numeric) and numeric[ci] else ""}">{cell(v)}</td>'
                      for ci, v in enumerate(r))
        body.append(f'<tr class="{cls}">{tds}</tr>')
    cap = f'<div class="tbl-cap">{inline(b["caption"])}</div>' if b.get("caption") else ""
    note = f'<div class="tbl-note">{inline(b["note"])}</div>' if b.get("note") else ""
    return (f'{cap}<div class="tbl-wrap"><table><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>{note}')


def b_bars(b):
    items = b.get("items", [])
    unit = b.get("unit", "")
    mx = max([float(i.get(k) or 0) for i in items for k in ("value", "max")] + [1])
    rows = []
    for it in items:
        v = float(it.get("value", 0) or 0)
        cap = float(it["max"]) if it.get("max") not in (None, "") else None
        pct = v / mx * 100
        over = cap is not None and v > cap
        cap_mark = f'<span class="bar-cap" style="left:{cap / mx * 100:.2f}%"></span>' if cap else ""
        val_txt = f"{v:g}{(' ' + unit) if unit else ''}" + (f" / {cap:g}" if cap else "")
        note = f'<div class="bar-note">{inline(it["note"])}</div>' if it.get("note") else ""
        rows.append(f'<div class="bar-row"><div class="bar-label">{inline(it.get("label"))}</div>'
                    f'<div class="bar-track"><span class="bar-fill{" over" if over else ""}" style="width:{pct:.2f}%"></span>{cap_mark}</div>'
                    f'<div class="bar-val">{esc(val_txt)}</div>{note}</div>')
    legend = '<div class="bar-legend"><span class="bar-cap-key"></span> năng lực tối đa</div>' if any(
        i.get("max") not in (None, "") for i in items) else ""
    return '<div class="bars">' + "".join(rows) + "</div>" + legend


def b_cards(b):
    out = []
    for c in b.get("items", []):
        tag = f'<span class="badge b-{esc(c.get("tone", "neutral"))}">{inline(c["tag"])}</span>' if c.get("tag") else ""
        out.append(f'<div class="card card-{esc(c.get("tone", ""))}"><div class="card-head">'
                   f'<div class="card-title">{inline(c.get("title"))}</div>{tag}</div>'
                   f'<div class="prose">{md(c.get("content"))}</div></div>')
    return '<div class="cards">' + "".join(out) + "</div>"


def b_rag(b):
    out = []
    for it in b.get("items", []):
        st = str(it.get("status", "")).strip().lower()
        tone = RAG_NORMAL.get(st, BADGE_LOOKUP.get(st, "neutral"))
        label = RAG_LABEL.get(tone, it.get("status", ""))
        out.append(f'<div class="rag-item"><span class="dot d-{tone}"></span><div class="rag-area">{inline(it.get("area"))}</div>'
                   f'<span class="badge b-{tone}">{esc(label)}</span><div class="rag-note">{inline(it.get("note", ""))}</div></div>')
    return '<div class="rag">' + "".join(out) + "</div>"


LEVEL = {"thấp": 0, "low": 0, "trung bình": 1, "tb": 1, "medium": 1, "cao": 2, "high": 2}


def b_risk_matrix(b):
    grid = {}
    for r in b.get("risks", []):
        p = LEVEL.get(str(r.get("probability", "")).strip().lower())
        i = LEVEL.get(str(r.get("impact", "")).strip().lower())
        if p is None or i is None:
            warn(f"Rủi ro {r.get('id')}: xác suất/ảnh hưởng phải là Cao/Trung bình/Thấp")
            continue
        grid.setdefault((p, i), []).append(r.get("id", "?"))
    tone = lambda p, i: "danger" if p + i >= 3 else ("warn" if p + i == 2 else "ok")
    names = ["Thấp", "Trung bình", "Cao"]
    cells = []
    for p in (2, 1, 0):
        cells.append(f'<div class="rm-y">{names[p]}</div>')
        for i in (0, 1, 2):
            ids = "".join(f'<span class="rm-id">{esc(x)}</span>' for x in grid.get((p, i), []))
            cells.append(f'<div class="rm-cell rm-{tone(p, i)}">{ids}</div>')
    cells.append('<div></div>' + "".join(f'<div class="rm-x">{n}</div>' for n in names))
    return ('<div class="rm-wrap"><div class="rm-axis-y">Xác suất ↑</div><div class="rm">' + "".join(cells) +
            '</div><div class="rm-axis-x">Ảnh hưởng →</div></div>')


def b_gantt(b):
    items = b.get("items", [])
    parsed = []
    for idx, it in enumerate(items):
        where = f"(Gantt: '{it.get('name')}')"
        s = parse_date(it.get("start") or it.get("date"), where)
        e = parse_date(it.get("end") or it.get("date") or it.get("start"), where)
        bs = parse_date(it.get("baseline_start"), where)
        be = parse_date(it.get("baseline_end"), where)
        if s and e and e < s:
            warn(f"{where} ngày kết thúc trước ngày bắt đầu")
            s, e = e, s
        if not s:
            continue
        parsed.append((it, s, e, bs, be))
    if not parsed:
        return '<p class="muted">(Không có dữ liệu timeline)</p>'
    all_d = [d for _, s, e, bs, be in parsed for d in (s, e, bs, be) if d]
    today = parse_date(b.get("today"), "(Gantt today)") if b.get("today") else None
    lo = min(all_d)
    hi = max(all_d)
    lo = lo - timedelta(days=lo.weekday())                 # back to Monday
    hi = hi + timedelta(days=6 - hi.weekday())             # forward to Sunday
    total = (hi - lo).days + 1
    pos = lambda d: (d - lo).days / total * 100

    # month header
    months, d = [], date(lo.year, lo.month, 1)
    while d <= hi:
        nxt = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
        a, z = max(d, lo), min(nxt - timedelta(days=1), hi)
        months.append(f'<div class="g-month" style="left:{pos(a):.3f}%;width:{((z - a).days + 1) / total * 100:.3f}%">'
                      f'T{d.month}/{d.year}</div>')
        d = nxt
    weeks = "".join(f'<span class="g-week" style="left:{pos(lo + timedelta(days=w)):.3f}%"></span>'
                    for w in range(0, total, 7))
    today_line = (f'<span class="g-today" style="left:{pos(today):.3f}%" title="Hôm nay {vn_date(today)}"></span>'
                  if today and lo <= today <= hi else "")

    rows, cur_group = [], None
    for it, s, e, bs, be in parsed:
        g = it.get("group")
        if g and g != cur_group:
            rows.append(f'<div class="g-row g-grouprow"><div class="g-label g-group">{inline(g)}</div><div class="g-track">{weeks}</div></div>')
            cur_group = g
        kind = it.get("kind", "task")
        tone = it.get("tone", "")
        tip = f"{it.get('name')}: {vn_date(s)}" + (f" → {vn_date(e)}" if e != s else "")
        if it.get("note"):
            tip += f" — {it['note']}"
        base = ""
        if bs and be:
            base = (f'<span class="g-base" style="left:{pos(bs):.3f}%;width:{((be - bs).days + 1) / total * 100:.3f}%" '
                    f'title="Kế hoạch gốc: {vn_date(bs)} → {vn_date(be)}"></span>')
        if kind == "milestone":
            mark = f'<span class="g-ms {esc(tone)}" style="left:{pos(s) + 0.5 / total * 100:.3f}%" title="{esc(tip)}"></span>'
            dates = vn_date(s, False)
        else:
            mark = (f'<span class="g-bar k-{esc(kind)} {esc(tone)}" style="left:{pos(s):.3f}%;'
                    f'width:{((e - s).days + 1) / total * 100:.3f}%" title="{esc(tip)}"></span>')
            dates = f"{vn_date(s, False)} – {vn_date(e, False)}"
        rows.append(f'<div class="g-row k-row-{esc(kind)}"><div class="g-label"><span class="g-name">{inline(it.get("name"))}</span>'
                    f'<span class="g-dates">{dates}</span></div><div class="g-track">{weeks}{base}{mark}{today_line}</div></div>')

    has_base = any(bs for _, _, _, bs, _ in parsed)
    legend = ['<span><i class="lg k-phase"></i>Giai đoạn</span>', '<span><i class="lg k-sprint"></i>Sprint</span>',
              '<span><i class="lg k-task"></i>Công việc</span>', '<span><i class="lg lg-ms"></i>Milestone</span>']
    if has_base:
        legend.append('<span><i class="lg lg-base"></i>Kế hoạch gốc</span>')
    if today_line:
        legend.append('<span><i class="lg lg-today"></i>Hôm nay</span>')
    return (f'<div class="gantt-scroll"><div class="gantt"><div class="g-row g-head"><div class="g-label"></div>'
            f'<div class="g-track g-months">{"".join(months)}</div></div>{"".join(rows)}</div></div>'
            f'<div class="g-legend">{"".join(legend)}</div>')


BLOCKS = {"text": b_text, "list": b_list, "checklist": b_checklist, "callout": b_callout, "kpis": b_kpis,
          "table": b_table, "bars": b_bars, "cards": b_cards, "rag": b_rag, "risk_matrix": b_risk_matrix,
          "gantt": b_gantt}


def render_block(b):
    t = b.get("type")
    fn = BLOCKS.get(t)
    if not fn:
        warn(f"Loại khối không hỗ trợ: '{t}' — hiển thị dạng văn bản")
        return b_text({"content": b.get("content", json.dumps(b, ensure_ascii=False))})
    # callouts render their own title inside the box
    title = f'<h3>{inline(b["title"])}</h3>' if b.get("title") and t != "callout" else ""
    return f'<div class="block block-{t}">{title}{fn(b)}</div>'


# ---------------------------------------------------------------- page

CSS = r"""
:root{--bg:#f6f7f9;--surface:#fff;--surface2:#f1f3f6;--text:#1c2430;--muted:#5d6b7c;--line:#e2e6ec;
--accent:#2f5bea;--accent2:#8aa6f7;--accent-soft:#e8eefe;--ok:#1f9d55;--ok-soft:#e3f5ea;--warn:#c27c0e;--warn-soft:#fdf2dc;
--danger:#d33a2c;--danger-soft:#fde6e3;--info:#1f7ab8;--info-soft:#e2f0fa;--violet:#7a4fd6;--violet-soft:#efe8fc;
--shadow:0 1px 2px rgba(16,24,40,.06),0 1px 3px rgba(16,24,40,.08)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0f141b;--surface:#161d26;--surface2:#1c2531;--text:#e5eaf1;
--muted:#97a3b3;--line:#283342;--accent:#7d9bff;--accent2:#3d5bb8;--accent-soft:#1d2a4a;--ok:#4cc78a;--ok-soft:#173326;--warn:#f0b54a;
--warn-soft:#3a2d12;--danger:#ff7a6b;--danger-soft:#3d1c19;--info:#5db3ea;--info-soft:#14304a;--violet:#b49aff;--violet-soft:#2a2145;--shadow:none}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 "Be Vietnam Pro",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
.layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:32px;max-width:1240px;margin:0 auto;padding:32px 24px}
nav.toc{position:sticky;top:24px;align-self:start;font-size:14px}
nav.toc .toc-h{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 8px}
nav.toc a{display:block;padding:5px 10px;border-radius:6px;color:var(--muted);text-decoration:none;border-left:2px solid transparent}
nav.toc a:hover{background:var(--surface2);color:var(--text);border-left-color:var(--accent)}
header.doc{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:28px 28px 22px;box-shadow:var(--shadow);margin-bottom:24px}
.eyebrow{color:var(--accent);font-weight:600;font-size:13px;letter-spacing:.06em;text-transform:uppercase}
h1{font-size:28px;line-height:1.25;margin:6px 0 4px}
.subtitle{color:var(--muted);margin:0 0 14px}
.meta{display:flex;flex-wrap:wrap;gap:8px}.meta span{background:var(--surface2);border:1px solid var(--line);border-radius:999px;padding:3px 12px;font-size:13px}
.meta b{color:var(--muted);font-weight:500;margin-right:4px}
.summary{margin-top:18px;padding-top:16px;border-top:1px solid var(--line)}
section.sec{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:24px 28px;margin-bottom:20px;box-shadow:var(--shadow);scroll-margin-top:16px}
section.sec>h2{font-size:20px;margin:0 0 16px;display:flex;align-items:center;gap:10px}
section.sec>h2 .num{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:8px;background:var(--accent-soft);color:var(--accent);font-size:14px}
.block{margin:0 0 20px}.block:last-child{margin-bottom:0}
.block>h3{font-size:16px;margin:0 0 10px}
.prose p{margin:0 0 10px}.prose ul,.prose ol,ul.plain,ol.plain{margin:0 0 10px;padding-left:22px}.prose li{margin:3px 0}
.prose h4{font-size:15px;margin:14px 0 6px}
code{background:var(--surface2);padding:1px 5px;border-radius:4px;font-size:.9em}
.muted{color:var(--muted)}
.tbl-cap{font-weight:600;margin-bottom:8px}.tbl-note{color:var(--muted);font-size:13px;margin-top:6px}
.tbl-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:14px}
th{background:var(--surface2);text-align:left;font-weight:600;color:var(--muted);font-size:13px;white-space:nowrap}
th,td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:0}tbody tr:hover td{background:var(--surface2)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.total td{font-weight:700;background:var(--accent-soft)}
.badge{display:inline-block;padding:1px 9px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap;border:1px solid transparent}
.b-danger{background:var(--danger-soft);color:var(--danger)}.b-warn{background:var(--warn-soft);color:var(--warn)}
.b-ok{background:var(--ok-soft);color:var(--ok)}.b-info{background:var(--info-soft);color:var(--info)}
.b-neutral{background:var(--surface2);color:var(--muted);border-color:var(--line)}
.b-must{background:var(--danger-soft);color:var(--danger)}.b-should{background:var(--warn-soft);color:var(--warn)}
.b-could{background:var(--info-soft);color:var(--info)}.b-wont{background:var(--surface2);color:var(--muted);border-color:var(--line)}
.callout{display:flex;gap:12px;padding:14px 16px;border-radius:10px;border:1px solid var(--line);background:var(--surface2)}
.co-icon{font-size:18px;line-height:1.4}.co-body .prose,.co-body p:last-child{margin-bottom:0}.co-title{font-weight:700;margin-bottom:4px}
.co-info{background:var(--info-soft);border-color:transparent}.co-tip{background:var(--violet-soft);border-color:transparent}
.co-warn{background:var(--warn-soft);border-color:transparent}.co-danger{background:var(--danger-soft);border-color:transparent}
.co-success{background:var(--ok-soft);border-color:transparent}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.kpi{border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:var(--surface)}
.kpi-label{color:var(--muted);font-size:13px}.kpi-value{font-size:24px;font-weight:700;line-height:1.3;margin-top:2px}
.kpi-note{font-size:12px;color:var(--muted);margin-top:2px}
.kpi-ok .kpi-value{color:var(--ok)}.kpi-warn .kpi-value{color:var(--warn)}.kpi-danger .kpi-value{color:var(--danger)}.kpi-accent .kpi-value{color:var(--accent)}
.bars{display:grid;gap:10px}.bar-row{display:grid;grid-template-columns:180px 1fr 120px;gap:12px;align-items:center}
.bar-track{position:relative;height:14px;background:var(--surface2);border-radius:999px}
.bar-fill{position:absolute;left:0;top:0;bottom:0;background:var(--accent);border-radius:999px}.bar-fill.over{background:var(--danger)}
.bar-cap{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--text);opacity:.55}
.bar-val{font-variant-numeric:tabular-nums;font-size:13px;text-align:right}
.bar-note{grid-column:1/-1;margin-top:-6px;font-size:12px;color:var(--muted);padding-left:192px}
.bar-legend{font-size:12px;color:var(--muted);margin-top:8px}.bar-cap-key{display:inline-block;width:2px;height:12px;background:var(--text);opacity:.55;vertical-align:middle;margin-right:4px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}
.card{border:1px solid var(--line);border-radius:12px;padding:16px;background:var(--surface)}
.card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px}.card-title{font-weight:700}
.card-ok{border-color:var(--ok);box-shadow:inset 0 3px 0 var(--ok)}.card-warn{box-shadow:inset 0 3px 0 var(--warn)}
.card-danger{box-shadow:inset 0 3px 0 var(--danger)}.card-info{box-shadow:inset 0 3px 0 var(--info)}
.card .prose p:last-child,.card .prose ul:last-child{margin-bottom:0}
.rag{display:grid;gap:8px}.rag-item{display:grid;grid-template-columns:14px 160px auto 1fr;gap:12px;align-items:center;padding:10px 12px;border:1px solid var(--line);border-radius:10px}
.dot{width:12px;height:12px;border-radius:50%}.d-ok{background:var(--ok)}.d-warn{background:var(--warn)}.d-danger{background:var(--danger)}.d-neutral{background:var(--muted)}
.rag-area{font-weight:600}.rag-note{color:var(--muted);font-size:14px}
.checklist{list-style:none;padding:0;margin:0;display:grid;gap:6px}.checklist li{display:flex;gap:10px;align-items:flex-start}
.checklist .box{flex:none;width:18px;height:18px;border:1.5px solid var(--line);border-radius:5px;display:grid;place-items:center;font-size:12px;margin-top:3px;color:#fff}
.checklist li.done .box{background:var(--ok);border-color:var(--ok)}.checklist li.done>span:last-child{color:var(--muted);text-decoration:line-through}
.rm-wrap{display:grid;grid-template-columns:auto 1fr;grid-template-rows:1fr auto;gap:6px;max-width:460px}
.rm-axis-y{writing-mode:vertical-rl;transform:rotate(180deg);text-align:center;font-size:12px;color:var(--muted)}
.rm-axis-x{grid-column:2;text-align:center;font-size:12px;color:var(--muted)}
.rm{display:grid;grid-template-columns:80px repeat(3,1fr);gap:4px}
.rm-y,.rm-x{font-size:12px;color:var(--muted);display:flex;align-items:center;justify-content:center;text-align:center}
.rm-cell{min-height:64px;border-radius:8px;padding:6px;display:flex;flex-wrap:wrap;gap:4px;align-content:flex-start}
.rm-ok{background:var(--ok-soft)}.rm-warn{background:var(--warn-soft)}.rm-danger{background:var(--danger-soft)}
.rm-id{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:0 6px;font-size:12px;font-weight:600}
.gantt-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
.gantt{min-width:760px}
.g-row{display:grid;grid-template-columns:260px 1fr;border-bottom:1px solid var(--line)}.g-row:last-child{border-bottom:0}
.g-label{padding:7px 12px;display:flex;justify-content:space-between;gap:8px;align-items:center;border-right:1px solid var(--line);font-size:13px;background:var(--surface)}
.g-name{line-height:1.3}.g-dates{color:var(--muted);font-size:11px;white-space:nowrap;font-variant-numeric:tabular-nums}
.g-track{position:relative;min-height:34px}
.g-head .g-label,.g-head{background:var(--surface2)}.g-months{min-height:30px}
.g-month{position:absolute;top:0;bottom:0;border-left:1px solid var(--line);font-size:12px;color:var(--muted);padding:6px 8px;white-space:nowrap;overflow:hidden}
.g-week{position:absolute;top:0;bottom:0;width:1px;background:var(--line);opacity:.6}
.g-grouprow{background:var(--surface2)}.g-grouprow .g-label{background:var(--surface2)}.g-group{font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.g-grouprow .g-track{min-height:28px}
.g-bar{position:absolute;top:9px;height:16px;border-radius:5px;background:var(--accent2)}
.g-bar.k-phase{background:var(--accent);top:8px;height:18px}.g-bar.k-sprint{background:var(--accent2)}.g-bar.k-task{background:var(--muted);opacity:.55}
.g-bar.ok{background:var(--ok)}.g-bar.warn{background:var(--warn)}.g-bar.danger{background:var(--danger)}
.g-base{position:absolute;top:5px;height:24px;border:1.5px dashed var(--muted);border-radius:6px;opacity:.7}
.g-ms{position:absolute;top:10px;width:14px;height:14px;background:var(--warn);transform:translateX(-50%) rotate(45deg);border-radius:2px}
.g-ms.danger{background:var(--danger)}.g-ms.ok{background:var(--ok)}
.k-row-milestone .g-name{font-weight:600}.k-row-phase .g-name{font-weight:600}
.g-today{position:absolute;top:0;bottom:0;width:2px;background:var(--danger);z-index:2}
.g-legend{display:flex;flex-wrap:wrap;gap:16px;font-size:12px;color:var(--muted);margin-top:8px}
.lg{display:inline-block;width:18px;height:10px;border-radius:3px;margin-right:6px;vertical-align:middle;background:var(--accent2)}
.lg.k-phase{background:var(--accent)}.lg.k-task{background:var(--muted);opacity:.55}
.lg-ms{width:10px;height:10px;background:var(--warn);transform:rotate(45deg);border-radius:1px}
.lg-base{background:transparent;border:1.5px dashed var(--muted)}.lg-today{width:2px;height:12px;background:var(--danger)}
footer.doc{color:var(--muted);font-size:12px;text-align:center;padding:8px 0 24px}
@media (max-width:900px){.layout{grid-template-columns:minmax(0,1fr);padding:16px}nav.toc{position:static;display:flex;flex-wrap:wrap;gap:4px}
nav.toc .toc-h{width:100%}nav.toc a{border:1px solid var(--line);border-left-width:1px;font-size:13px;padding:3px 10px}
header.doc,section.sec{padding:18px 16px}h1{font-size:23px}.bar-row{grid-template-columns:110px 1fr 90px}.bar-note{padding-left:0}
.rag-item{grid-template-columns:14px 1fr auto}.rag-note{grid-column:2/-1}}
@media print{body{background:#fff;font-size:12px}nav.toc{display:none}.layout{display:block;padding:0}
section.sec,header.doc{box-shadow:none;break-inside:auto;border-color:#ccc}tr,.kpi,.card,.callout,.g-row{break-inside:avoid}
*{-webkit-print-color-adjust:exact;print-color-adjust:exact}.gantt-scroll,.tbl-wrap{overflow:visible}.gantt{min-width:0}}
"""


EDIT_CSS = r"""
.nt-bar{position:fixed;right:16px;bottom:16px;z-index:50;display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.nt-bar button{font:inherit;font-size:13px;font-weight:600;padding:8px 14px;border-radius:999px;border:1px solid var(--line);
background:var(--surface);color:var(--text);cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.12)}
.nt-bar button:hover{border-color:var(--accent)}.nt-bar button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.nt-bar .hide{display:none}
.nt-banner{display:none;position:sticky;top:0;z-index:40;background:var(--warn-soft);color:var(--text);font-size:13px;padding:8px 16px;text-align:center;border-bottom:1px solid var(--line)}
body.editing .nt-banner{display:block}
body.editing [contenteditable=true]{outline:1px dashed transparent;border-radius:3px;cursor:text}
body.editing [contenteditable=true]:hover{outline-color:var(--accent2)}
body.editing [contenteditable=true]:focus{outline:2px solid var(--accent);background:var(--accent-soft)}
body.editing [data-edited]{box-shadow:inset 0 -2px 0 var(--warn)}
.nt-ui{display:none}
body.editing .nt-ui{display:table-cell}
body.editing button.nt-ui,body.editing .nt-addrow{display:inline-block}
.nt-del{border:0;background:none;color:var(--danger);cursor:pointer;font-size:16px;line-height:1;padding:0 4px}
.nt-addrow{display:none;margin-top:6px;font:inherit;font-size:12px;padding:3px 10px;border-radius:6px;border:1px dashed var(--accent);background:transparent;color:var(--accent);cursor:pointer}
@media print{.nt-bar,.nt-banner,.nt-ui,.nt-addrow{display:none!important}}
"""

EDIT_JS = r"""
(function(){
var EDITABLE='h1,.subtitle,.meta span,.eyebrow,.summary p,.summary li,.prose p,.prose li,.prose h4,ul.plain li,ol.plain li,'+
 '.block>h3,section.sec>h2,th,td,.kpi-label,.kpi-value,.kpi-note,.co-title,.card-title,.rag-area,.rag-note,'+
 '.checklist li>span:last-child,.tbl-cap,.tbl-note,.bar-label,.bar-note,.g-name,footer.doc';
var editing=false,dirty=false,body=document.body;
function $(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function onInput(e){var t=e.target.closest('[contenteditable=true]');if(t){t.setAttribute('data-edited','1');dirty=true;}}
function rowControls(on){
  $('.tbl-wrap table').forEach(function(tb){
    if(on){
      var hr=tb.tHead&&tb.tHead.rows[0];
      if(hr&&!hr.querySelector('.nt-ui')){var th=document.createElement('th');th.className='nt-ui';hr.appendChild(th);}
      $('tbody tr',tb).forEach(addDel);
      var wrap=tb.parentNode;
      if(!wrap.nextElementSibling||!wrap.nextElementSibling.classList.contains('nt-addrow')){
        var b=document.createElement('button');b.className='nt-addrow';b.type='button';b.textContent='+ Thêm dòng';
        b.onclick=function(){var rows=tb.tBodies[0].rows;var src=null;
          for(var i=rows.length-1;i>=0;i--){if(!rows[i].classList.contains('total')){src=rows[i];break;}}
          if(!src)return;var tr=src.cloneNode(true);
          $('td',tr).forEach(function(td){if(!td.classList.contains('nt-ui')){td.innerHTML='';td.setAttribute('contenteditable','true');}});
          tr.setAttribute('data-edited','added');var del=tr.querySelector('.nt-ui');if(del)del.remove();addDel(tr);
          var tot=tb.tBodies[0].querySelector('tr.total');tb.tBodies[0].insertBefore(tr,tot||null);dirty=true;
          var first=tr.querySelector('td');if(first)first.focus();};
        wrap.parentNode.insertBefore(b,wrap.nextSibling);
      }
    }
  });
}
function addDel(tr){
  if(tr.querySelector('td.nt-ui'))return;var td=document.createElement('td');td.className='nt-ui';
  var b=document.createElement('button');b.className='nt-del';b.type='button';b.title='Xóa dòng';b.textContent='×';
  b.onclick=function(){if(confirm('Xóa dòng này?')){tr.remove();dirty=true;}};td.appendChild(b);tr.appendChild(td);
}
function setEdit(on){
  editing=on;body.classList.toggle('editing',on);
  $(EDITABLE).forEach(function(el){if(on)el.setAttribute('contenteditable','true');else el.removeAttribute('contenteditable');});
  rowControls(on);
  document.getElementById('nt-edit').textContent=on?'✓ Xong':'✏️ Chỉnh sửa';
}
function cleanHtml(){
  var root=document.documentElement.cloneNode(true);
  Array.prototype.slice.call(root.querySelectorAll('.nt-ui,.nt-addrow')).forEach(function(e){e.remove();});
  Array.prototype.slice.call(root.querySelectorAll('[contenteditable]')).forEach(function(e){e.removeAttribute('contenteditable');});
  var b=root.querySelector('body');b.classList.remove('editing');
  var now=new Date(),d=('0'+now.getDate()).slice(-2)+'/'+('0'+(now.getMonth()+1)).slice(-2)+'/'+now.getFullYear();
  b.setAttribute('data-edited-at',now.toISOString());
  var f=root.querySelector('footer.doc');
  if(f&&f.textContent.indexOf('Đã chỉnh sửa tay')<0)f.innerHTML+=' · Đã chỉnh sửa tay '+d;
  return '<!doctype html>\n'+root.outerHTML;
}
function save(){
  var name=(decodeURIComponent(location.pathname.split('/').pop()||'')||document.title||'tai-lieu').replace(/\.html?$/i,'').replace(/-da-sua$/,'')+'-da-sua.html';
  var blob=new Blob([cleanHtml()],{type:'text/html'});var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();
  setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},1000);dirty=false;
}
document.getElementById('nt-edit').onclick=function(){setEdit(!editing);};
document.getElementById('nt-save').onclick=save;
document.getElementById('nt-print').onclick=function(){if(editing)setEdit(false);window.print();};
document.addEventListener('input',onInput);
window.addEventListener('beforeunload',function(e){if(dirty){e.preventDefault();e.returnValue='';}});
})();
"""


def render(doc):
    title = doc.get("title", "Tài liệu dự án")
    sections = doc.get("sections", [])
    toc = "".join(f'<a href="#s{i + 1}">{i + 1}. {inline(s.get("title"))}</a>' for i, s in enumerate(sections))
    meta = "".join(f"<span><b>{inline(k)}:</b>{inline(v)}</span>" for k, v in (doc.get("meta") or {}).items())
    summary = f'<div class="summary prose">{md(doc["summary"])}</div>' if doc.get("summary") else ""
    secs = []
    for i, s in enumerate(sections):
        blocks = "".join(render_block(b) for b in s.get("blocks", []))
        secs.append(f'<section class="sec" id="s{i + 1}"><h2><span class="num">{i + 1}</span>{inline(s.get("title"))}</h2>{blocks}</section>')
    footer = doc.get("footer", f"Tạo bởi trợ lý nt-pm · {vn_date(date.today())}")
    # original JSON is embedded so Claude can recover the structure from an edited file
    source = json.dumps(doc, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}{EDIT_CSS}</style></head>
<body><div class="nt-banner">Đang chỉnh sửa — bấm vào chữ hoặc ô bảng để sửa. Tổng số, Gantt và biểu đồ không tự tính lại; đổi số liệu lớn thì gửi file đã sửa cho Claude cập nhật.</div>
<div class="layout"><nav class="toc"><div class="toc-h">Mục lục</div>{toc}</nav>
<main><header class="doc"><div class="eyebrow">{inline(doc.get("doc_type", ""))}</div><h1>{inline(title)}</h1>
{f'<p class="subtitle">{inline(doc["subtitle"])}</p>' if doc.get("subtitle") else ""}<div class="meta">{meta}</div>{summary}</header>
{"".join(secs)}<footer class="doc">{inline(footer)}</footer></main></div>
<div class="nt-bar"><button id="nt-print" type="button">🖨️ In / PDF</button><button id="nt-save" type="button">💾 Lưu bản sửa</button><button id="nt-edit" type="button" class="primary">✏️ Chỉnh sửa</button></div>
<script type="application/json" id="nt-pm-source">{source}</script>
<script>{EDIT_JS}</script></body></html>"""


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Lỗi JSON trong {src}: {e}", file=sys.stderr)
            sys.exit(2)
    out = render(doc)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out)
    for w in WARNINGS:
        print("CẢNH BÁO:", w, file=sys.stderr)
    print(f"Đã tạo {dst} ({len(out) // 1024} KB, {len(doc.get('sections', []))} mục, {len(WARNINGS)} cảnh báo)")


if __name__ == "__main__":
    main()
