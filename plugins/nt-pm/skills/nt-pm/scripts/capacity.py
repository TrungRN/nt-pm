#!/usr/bin/env python3
"""Tính năng lực (man-day) theo từng người × từng sprint.

Usage:
    python3 capacity.py roster.json [--blocks blocks.json] [--json result.json]

- In bảng tóm tắt ra màn hình.
- --blocks: ghi ra các khối (table/list/callout) dùng thẳng trong JSON của render_report.py.
- --json:   ghi kết quả chi tiết (để tính tiếp, ví dụ dự báo timeline).

Định dạng roster.json: xem references/resource-planning.md. Chỉ dùng thư viện chuẩn.
"""
import json
import sys
from datetime import date, datetime, timedelta

LEVEL_PRODUCTIVITY = {"fresher": 0.5, "junior": 0.7, "middle": 1.0, "mid": 1.0, "senior": 1.1}
WARN = []


def d(s, where=""):
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        WARN.append(f"Ngày không hợp lệ '{s}' {where} (dùng YYYY-MM-DD)")
        return None


def fmt(x):
    x = round(x, 1)
    return int(x) if x == int(x) else x


def build_sprints(cfg):
    sp = cfg.get("sprints")
    if isinstance(sp, list):
        out = []
        for s in sp:
            a, b = d(s.get("start"), f"(sprint {s.get('name')})"), d(s.get("end"), f"(sprint {s.get('name')})")
            if a and b:
                out.append({"name": s["name"], "start": a, "end": b})
        return out
    # generator: {"first_start": "...", "length_weeks": 2, "count": 6, "prefix": "Sprint "}
    start = d(sp["first_start"], "(sprints.first_start)")
    n, w, pre = int(sp["count"]), int(sp.get("length_weeks", 2)), sp.get("prefix", "Sprint ")
    first = int(sp.get("first_number", 1))
    out = []
    for i in range(n):
        a = start + timedelta(weeks=w * i)
        out.append({"name": f"{pre}{first + i}", "start": a, "end": a + timedelta(weeks=w) - timedelta(days=3)})
    return out


def holiday_set(cfg):
    hs = set()
    for h in cfg.get("holidays", []):
        if isinstance(h, dict):
            a, b = d(h.get("start"), "(holidays)"), d(h.get("end", h.get("start")), "(holidays)")
        else:
            a = b = d(h, "(holidays)")
        while a and b and a <= b:
            hs.add(a)
            a += timedelta(days=1)
    return hs


def workdays(a, b, hol):
    n, x = 0, a
    while x <= b:
        if x.weekday() < 5 and x not in hol:
            n += 1
        x += timedelta(days=1)
    return n


def per_sprint(val, sprint, default=None):
    """val may be a number (all sprints) or {sprint_name: number}."""
    if isinstance(val, dict):
        return val.get(sprint, val.get("*", default))
    return default if val is None else val


def compute(cfg):
    sprints = build_sprints(cfg)
    hol = holiday_set(cfg)
    ff_default = float(cfg.get("focus_factor", 0.75))
    ff_role = cfg.get("focus_by_role", {})
    proj_start = sprints[0]["start"] if sprints else None
    people_out, changes = [], []
    names = [s["name"] for s in sprints]

    for p in cfg.get("people", []):
        name, role = p.get("name", "?"), p.get("role", "?")
        level = p.get("level", "")
        prod = float(p.get("productivity", LEVEL_PRODUCTIVITY.get(str(level).lower(), 1.0)))
        ff = float(p.get("focus_factor", ff_role.get(role, ff_default)))
        p_start = d(p["start"], f"({name}.start)") if p.get("start") else None
        p_end = d(p["end"], f"({name}.end)") if p.get("end") else None
        ramp = p.get("ramp_up")
        if ramp is None:
            ramp = bool(p_start and proj_start and p_start > proj_start)
        ramp_factor = 0.5 if ramp is True else (float(ramp) if ramp not in (False, None) else 1.0)
        for k in ("allocation_by_sprint", "leave_days", "capacity_override"):
            for s_name in (p.get(k) or {}):
                if s_name not in names and s_name != "*":
                    WARN.append(f"{name}: '{s_name}' trong {k} không khớp tên sprint nào ({', '.join(names)})")

        base_alloc = float(p.get("allocation", 1.0))
        alloc_from = sorted((d(k, f"({name}.allocation_from)"), float(v))
                            for k, v in (p.get("allocation_from") or {}).items())
        alloc_from = [x for x in alloc_from if x[0]]

        def alloc_on(day):
            a_ = base_alloc
            for dt, v in alloc_from:
                if day >= dt:
                    a_ = v
            return a_

        cells, first_active, prev_by_sprint = [], True, None
        for s in sprints:
            a = max(s["start"], p_start) if p_start else s["start"]
            b = min(s["end"], p_end) if p_end else s["end"]
            days, x = [], a
            while x <= b:
                if x.weekday() < 5 and x not in hol:
                    days.append(x)
                x += timedelta(days=1)
            wd = len(days)
            leave = float(per_sprint(p.get("leave_days"), s["name"], 0) or 0)
            fixed = per_sprint(p.get("allocation_by_sprint"), s["name"], None)
            if fixed is not None:
                alloc = float(fixed)
            elif days:
                alloc = sum(alloc_on(x) for x in days) / len(days)   # weighted when % changes mid-sprint
            else:
                alloc = alloc_on(s["start"])
            avail = max(0.0, wd - leave)
            rf = 1.0
            if avail > 0 and alloc > 0 and first_active:
                rf = ramp_factor
                first_active = False
            override = per_sprint(p.get("capacity_override"), s["name"], None)
            cap = float(override) if override is not None else avail * alloc * ff * prod * rf
            note = []
            if override is not None:
                note.append("nhập tay")
            if rf < 1:
                note.append(f"làm quen ×{rf:g}")
            if leave:
                note.append(f"nghỉ {leave:g} ngày")
            if wd and 0 < alloc < 1:
                note.append(f"{alloc:.0%}")
            cells.append({"sprint": s["name"], "workdays": wd, "leave": leave, "allocation": round(alloc, 3),
                          "capacity": round(cap, 2), "note": ", ".join(note)})

            # roster change log — explicit events only (no noise for people who are simply part-time)
            if p_start and proj_start and p_start > proj_start and s["start"] <= p_start <= s["end"] + timedelta(days=2):
                changes.append((s["name"], f"**+ {name}** ({role}) vào dự án từ {p_start:%d/%m}"
                                + (f", sprint đầu làm quen ×{ramp_factor:g}" if ramp_factor < 1 else "")))
            if p_end and s["start"] <= p_end <= s["end"] + timedelta(days=2) and s is not sprints[-1]:
                changes.append((s["name"], f"**− {name}** ({role}) rời dự án sau {p_end:%d/%m}"))
            for dt, v in alloc_from:
                if s["start"] <= dt <= s["end"] + timedelta(days=2):
                    before = alloc_on(dt - timedelta(days=1))
                    changes.append((s["name"], f"{name} ({role}): phân bổ {before:.0%} → {v:.0%} từ {dt:%d/%m}"))
            cur = float(fixed) if fixed is not None else None
            if wd and s is not sprints[0] and cur != prev_by_sprint:
                old = prev_by_sprint if prev_by_sprint is not None else base_alloc
                new_ = cur if cur is not None else base_alloc
                if abs(old - new_) > 1e-9:
                    changes.append((s["name"], f"{name} ({role}): phân bổ {old:.0%} → {new_:.0%}"))
            if wd:
                prev_by_sprint = cur
            if leave:
                changes.append((s["name"], f"{name} nghỉ phép {leave:g} ngày"))
        people_out.append({"name": name, "role": role, "level": level, "productivity": prod, "focus_factor": ff,
                           "sprints": cells, "total": round(sum(c["capacity"] for c in cells), 2)})

    roles = []
    for p in people_out:
        if p["role"] not in roles:
            roles.append(p["role"])
    by_role = {r: {s: 0.0 for s in names} for r in roles}
    for p in people_out:
        for c in p["sprints"]:
            by_role[p["role"]][c["sprint"]] += c["capacity"]

    demand = {r: dict(v) for r, v in (cfg.get("demand") or {}).items()}
    work, unplanned = [], []
    for w in cfg.get("work", []):
        parts = w.get("md_by_role") or {w.get("role", "?"): w.get("md", 0)}
        sp = w.get("sprint")
        item = {"id": w.get("id", ""), "name": w.get("name", ""), "sprint": sp, "priority": w.get("priority", ""),
                "md_by_role": {r: float(v) for r, v in parts.items()}}
        work.append(item)
        if not sp:
            unplanned.append(item)
            continue
        if sp not in names:
            WARN.append(f"Hạng mục '{item['id']} {item['name']}': sprint '{sp}' không khớp tên sprint nào")
            continue
        for r, v in item["md_by_role"].items():
            demand.setdefault(r, {})
            demand[r][sp] = demand[r].get(sp, 0) + float(v)
    load = {}
    for r, per in demand.items():
        if r not in by_role:
            WARN.append(f"demand có vai trò '{r}' nhưng không có người nào vai trò này")
            continue
        load[r] = {s: (float(per.get(s, 0)), by_role[r][s]) for s in names}

    order = {n: i for i, n in enumerate(names)}
    changes.sort(key=lambda x: order.get(x[0], 0))
    return {"sprints": [{"name": s["name"], "start": s["start"].isoformat(), "end": s["end"].isoformat(),
                         "workdays": workdays(s["start"], s["end"], hol)} for s in sprints],
            "people": people_out, "by_role": by_role, "load": load, "changes": changes,
            "work": work, "unplanned": unplanned}


def status(pct):
    return "Quá tải" if pct > 1.0 else ("Sát" if pct > 0.85 else "OK")


def to_blocks(res):
    names = [s["name"] for s in res["sprints"]]
    blocks = []
    rows = [[s["name"], f"{s['start'][8:10]}/{s['start'][5:7]} – {s['end'][8:10]}/{s['end'][5:7]}", s["workdays"]]
            for s in res["sprints"]]
    blocks.append({"type": "table", "title": "Lịch sprint & ngày làm việc", "columns": ["Sprint", "Thời gian", "Ngày làm việc"],
                   "rows": rows, "note": "Đã trừ cuối tuần và ngày lễ."})

    cols = ["Vai trò"] + names + ["Tổng"]
    rows, grand = [], [0.0] * len(names)
    for r, per in res["by_role"].items():
        vals = [per[s] for s in names]
        grand = [g + v for g, v in zip(grand, vals)]
        rows.append([r] + [fmt(v) for v in vals] + [fmt(sum(vals))])
    rows.append(["**Tổng**"] + [fmt(g) for g in grand] + [fmt(sum(grand))])
    blocks.append({"type": "table", "title": "Năng lực theo vai trò × sprint (MD)", "columns": cols, "rows": rows,
                   "total_row": True,
                   "note": "Năng lực = ngày làm việc trên dự án − nghỉ phép, × % phân bổ × focus factor × hệ số năng suất (× hệ số làm quen ở sprint đầu của người mới)."})

    cols = ["Người", "Vai trò", "Cấp"] + names + ["Tổng"]
    rows = []
    for p in res["people"]:
        cells = []
        for c in p["sprints"]:
            if c["capacity"] == 0 and (c["workdays"] == 0 or c["allocation"] == 0):
                cells.append("–")
            else:
                cells.append(f"{fmt(c['capacity'])}" + (f" *({c['note']})*" if c["note"] else ""))
        rows.append([p["name"], p["role"], p["level"] or ""] + cells + [fmt(p["total"])])
    blocks.append({"type": "table", "title": "Chi tiết năng lực từng người (MD)", "columns": cols, "rows": rows,
                   "note": "'–' = không tham gia sprint đó."})

    if res["load"]:
        cols = ["Vai trò"] + names
        rows = []
        flagged = []
        for r, per in res["load"].items():
            row = [r]
            for s in names:
                need, cap = per[s]
                if need == 0:
                    row.append("–")
                    continue
                pct = need / cap if cap else float("inf")
                st = status(pct)
                row.append(f"{fmt(need)}/{fmt(cap)} ({pct:.0%}) {'⚠️' if st != 'OK' else ''}".strip()
                           if cap else f"{fmt(need)}/0 ⛔")
                if st == "Quá tải":
                    flagged.append(f"{r} ở {s}: cần {fmt(need)} MD, có {fmt(cap)} MD ({pct:.0%})")
            rows.append(row)
        blocks.append({"type": "table", "title": "Tải công việc / năng lực theo vai trò (MD)", "columns": cols, "rows": rows,
                       "note": "Mục tiêu ≤ 85% để còn chỗ cho phát sinh. ⚠️ = trên 85%."})
        if flagged:
            blocks.append({"type": "callout", "tone": "danger", "title": "Vai trò quá tải",
                           "content": "\n".join("- " + f for f in flagged)})

    if res.get("work"):
        cols = ["ID", "Hạng mục", "Vai trò (MD)", "Sprint", "Ưu tiên", "MD"]
        rows, tot = [], 0.0
        for w in res["work"]:
            md_ = sum(w["md_by_role"].values())
            tot += md_
            roles_txt = ", ".join(f"{r} {fmt(v)}" for r, v in w["md_by_role"].items())
            rows.append([w["id"], w["name"], roles_txt, w["sprint"] or "Chưa xếp", w["priority"], fmt(md_)])
        rows.append(["", "**Tổng**", "", "", "", fmt(tot)])
        blocks.append({"type": "table", "title": "Hạng mục công việc & sprint (WBS)", "columns": cols, "rows": rows,
                       "total_row": True})
        cap_by_sprint = {s: sum(per[s] for per in res["by_role"].values()) for s in names}
        rows = []
        for sp in res["sprints"]:
            items = [w for w in res["work"] if w["sprint"] == sp["name"]]
            need = sum(sum(w["md_by_role"].values()) for w in items)
            cap = cap_by_sprint[sp["name"]]
            rows.append([sp["name"], f"{sp['start'][8:10]}/{sp['start'][5:7]} – {sp['end'][8:10]}/{sp['end'][5:7]}",
                         "; ".join(f"{w['id']} {w['name']}".strip() for w in items) or "–",
                         fmt(need), fmt(cap), f"{need / cap:.0%}" if cap else "–"])
        blocks.append({"type": "table", "title": "Kế hoạch sprint: effort so với năng lực",
                       "columns": ["Sprint", "Thời gian", "Hạng mục", "Kế hoạch (MD)", "Năng lực (MD)", "% dùng"],
                       "rows": rows})
        if res.get("unplanned"):
            blocks.append({"type": "callout", "tone": "warn", "title": "Hạng mục chưa xếp sprint",
                           "content": "\n".join(f"- {w['id']} {w['name']} ({fmt(sum(w['md_by_role'].values()))} MD)"
                                                for w in res["unplanned"])})

    if res["changes"]:
        blocks.append({"type": "table", "title": "Thay đổi nhân sự theo sprint", "columns": ["Sprint", "Thay đổi"],
                       "rows": [[s, t] for s, t in res["changes"]]})
    return blocks


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        sys.exit(1)
    cfg = json.load(open(args[0], encoding="utf-8"))
    res = compute(cfg)
    names = [s["name"] for s in res["sprints"]]
    w = max([len(r) for r in res["by_role"]] + [8])
    print("Năng lực theo vai trò (MD):")
    short = [n.replace("Sprint ", "S") for n in names]
    print(" " * w + " | " + " | ".join(f"{n[:6]:>6}" for n in short) + " |  Tổng")
    for r, per in res["by_role"].items():
        print(f"{r:<{w}} | " + " | ".join(f"{fmt(per[s]):>6}" for s in names) + f" | {fmt(sum(per.values())):>5}")
    tot = sum(sum(per.values()) for per in res["by_role"].values())
    print(f"Tổng năng lực: {fmt(tot)} MD, {len(res['people'])} người, {len(names)} sprint")
    for r, per in res["load"].items():
        for s in names:
            need, cap = per[s]
            if need and (not cap or need / cap > 1):
                print(f"QUÁ TẢI: {r} ở {s}: cần {fmt(need)}, có {fmt(cap)}")
    if "--blocks" in args:
        out = args[args.index("--blocks") + 1]
        json.dump(to_blocks(res), open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Đã ghi khối render: {out}")
    if "--json" in args:
        out = args[args.index("--json") + 1]
        json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
        print(f"Đã ghi kết quả: {out}")
    for x in WARN:
        print("CẢNH BÁO:", x, file=sys.stderr)


if __name__ == "__main__":
    main()
