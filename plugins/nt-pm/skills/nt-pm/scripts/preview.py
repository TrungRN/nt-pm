#!/usr/bin/env python3
"""Kiểm tra nhanh một file HTML đã render: lỗi JavaScript + ảnh chụp toàn trang để xem bằng mắt.

Usage:
    python3 preview.py report.html [out.png] [--width 1280] [--mobile] [--dark]

Cần playwright + chromium. Nếu không có, script báo và thoát mã 3 — khi đó chỉ cần kiểm tra
render_report.py không in CẢNH BÁO.
Ảnh dài được cắt thành nhiều phần out_0.png, out_1.png… (mỗi phần ~2400px) để dễ xem.
"""
import sys


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    src = args[0]
    out = args[1] if len(args) > 1 else src.rsplit(".", 1)[0] + "-preview.png"
    width = 390 if "--mobile" in sys.argv else 1280
    if "--width" in sys.argv:
        width = int(sys.argv[sys.argv.index("--width") + 1])
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Không có playwright — bỏ qua bước chụp ảnh.")
        sys.exit(3)
    import os
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 900},
                        color_scheme="dark" if "--dark" in sys.argv else "light")
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("file://" + os.path.abspath(src))
        pg.wait_for_timeout(400)
        overflow = pg.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
        pg.evaluate("document.querySelector('.nt-bar') && (document.querySelector('.nt-bar').style.display='none')")
        pg.screenshot(path=out, full_page=True)
        b.close()
    parts = [out]
    try:
        from PIL import Image
        im = Image.open(out)
        w, h = im.size
        if h > 2600:
            base = out.rsplit(".", 1)[0]
            parts = []
            for i, y in enumerate(range(0, h, 2400)):
                fn = f"{base}_{i}.png"
                im.crop((0, y, w, min(h, y + 2400))).save(fn)
                parts.append(fn)
    except ImportError:
        pass
    print("Lỗi JS:", errors or "không có")
    if overflow:
        print("CẢNH BÁO: trang bị tràn ngang (có thanh cuộn ngang) ở độ rộng", width)
    print("Ảnh:", ", ".join(parts))


if __name__ == "__main__":
    main()
