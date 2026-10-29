#!/usr/bin/env python3
"""Full-page screenshots of static pages at exact viewport widths.

Headless Chrome clamps its window width to ~500px, so every page is rendered
inside an <iframe> of the requested width. Two passes: the first measures the
document height through the iframe (file:// access enabled), the second takes
the screenshot at that height and crops it to the iframe.

usage: shoot.py <out_dir> <page.html>... [--widths 360,390,768,1440]
"""
import os, re, subprocess, sys, tempfile
from PIL import Image

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_H = 16000

WRAPPER = """<!doctype html><meta charset=utf-8>
<style>html,body{{margin:0;background:#888}}iframe{{display:block;border:0;width:{w}px;height:{h}px}}</style>
<iframe id=f src="{src}"></iframe>
<script>
f.addEventListener('load',()=>{{setTimeout(()=>{{
  const d=f.contentDocument.documentElement;
  document.title='H='+Math.max(d.scrollHeight,f.contentDocument.body.scrollHeight)+' W='+d.scrollWidth;
}},800)}});
</script>"""

def run(args, timeout=60):
    return subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--allow-file-access-from-files",
                           "--disable-gpu", "--no-first-run", "--force-device-scale-factor=1",
                           "--user-data-dir=" + tempfile.mkdtemp(prefix="vochus-shoot-")] + args,
                          capture_output=True, text=True, timeout=timeout)

def shoot(page, width, out_png, workdir):
    src = "file://" + os.path.abspath(page)
    wrap = os.path.join(workdir, f"wrap-{os.path.basename(page)}-{width}.html")
    with open(wrap, "w") as fh:
        fh.write(WRAPPER.format(w=width, h=200, src=src))  # short frame so scrollHeight = content height
    r = run(["--dump-dom", "--virtual-time-budget=4000", "file://" + wrap])
    m = re.search(r"<title>H=(\d+) W=(\d+)</title>", r.stdout)
    h = min(int(m.group(1)), MAX_H) if m else 4000
    sw = int(m.group(2)) if m else 0
    win_w = max(width, 500)
    with open(wrap, "w") as fh:
        fh.write(WRAPPER.format(w=width, h=h, src=src))
    run([f"--window-size={win_w},{h}", f"--screenshot={out_png}", "--virtual-time-budget=4000", "file://" + wrap], timeout=120)
    im = Image.open(out_png)
    im.crop((0, 0, width, min(h, im.height))).save(out_png, optimize=True)
    return h, sw

def main():
    args = sys.argv[1:]
    widths = [360, 390, 768, 1440]
    if "--widths" in args:
        i = args.index("--widths"); widths = [int(x) for x in args[i + 1].split(",")]; del args[i:i + 2]
    out_dir, pages = args[0], args[1:]
    os.makedirs(out_dir, exist_ok=True)
    workdir = tempfile.mkdtemp(prefix="vochus-wrap-")
    for page in pages:
        name = os.path.splitext(os.path.basename(page))[0]
        for w in widths:
            out = os.path.join(out_dir, f"{name}-{w}.png")
            h, sw = shoot(page, w, out, workdir)
            flag = "" if sw <= w else f"  <-- horizontal overflow (scrollWidth {sw})"
            print(f"{name}-{w}.png  {w}x{h}{flag}", flush=True)

if __name__ == "__main__":
    main()
