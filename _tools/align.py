#!/usr/bin/env python3
"""Alignment audit: at each width, measure left/right edges of the nav logo, the last nav
button, the h1, the ledger card, every section heading, the trust panel, and the footer logo.
All lefts must equal the wrap's content-left and all rights its content-right.
usage: align.py <page.html> [--guides out.png]   (guides: draws the wrap edges on a 1440 shot)
"""
import json, os, re, subprocess, sys, tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
JS = r"""
(() => {
  const d = f.contentDocument, r = e => e && e.getBoundingClientRect();
  const row = (name, e, side) => { const b = r(e); return b ? [name, Math.round(b.left*100)/100, Math.round(b.right*100)/100, side] : [name, null, null, side]; };
  const out = [];
  out.push(row('nav logo', d.querySelector('.nav-bar .brand'), 'L'));
  const btns = [...d.querySelectorAll('.nav-cta .btn')].filter(b => b.offsetParent !== null);
  out.push(row('last nav button', btns[btns.length-1], 'R'));
  out.push(row('h1', d.querySelector('h1'), 'L'));
  out.push(row('ledger card', d.querySelector('.ledger'), 'R'));
  d.querySelectorAll('main h2').forEach(h => { const panel = h.closest('.trust,.band,.cta'); out.push(row('h2 ' + h.textContent.trim().slice(0,22) + (panel ? ' (in panel)' : ''), h, panel ? 'P' : 'L')); });
  const panelEl = d.querySelector('.trust,.band,.cta'); const pad = panelEl ? parseFloat(getComputedStyle(panelEl).paddingLeft) + parseFloat(getComputedStyle(panelEl).borderLeftWidth) : 0;
  out.push(row('trust panel', d.querySelector('.trust'), 'LR'));
  out.push(row('agent band', d.querySelector('.band'), 'LR'));
  out.push(row('footer logo', d.querySelector('.footer .brand'), 'L'));
  const w = d.querySelector('main .wrap'); const cs = getComputedStyle(w); const wb = r(w);
  const left = wb.left + parseFloat(cs.paddingLeft), right = wb.right - parseFloat(cs.paddingRight);
  document.body.insertAdjacentHTML('beforeend', '<pre id="al'+'ign">' + JSON.stringify({left, right, pad, rows: out, sw: d.documentElement.scrollWidth}) + '</p'+'re>');
})();
"""

def measure(page, width):
    wrap = os.path.join(tempfile.mkdtemp(), "a.html")
    open(wrap, "w").write(f'<!doctype html><meta charset=utf-8><style>html,body{{margin:0}}iframe{{width:{width}px;height:900px;border:0;display:block}}</style>'
                          f'<iframe id=f src="file://{page}"></iframe><script>f.addEventListener("load",()=>setTimeout(()=>{{{JS}}},900))</script>')
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", "--no-first-run", "--user-data-dir=" + tempfile.mkdtemp(),
                        f"--window-size={max(width,500)},900", "--virtual-time-budget=4000", "--dump-dom", "file://" + wrap], capture_output=True, text=True)
    m = re.search(r'<pre id="align">(.*?)</pre>', r.stdout, re.S)
    return json.loads(m.group(1))

def main():
    page = os.path.abspath(sys.argv[1]); ok_all = True
    for width in (1024, 1200, 1440, 1920):
        o = measure(page, width); L, R = o["left"], o["right"]
        print(f"\n@ {width}px  wrap content left={L:g} right={R:g}  (scrollWidth {o['sw']})")
        for name, l, r, side in o["rows"]:
            checks = []
            if "L" in side: checks.append(("left", l, L))
            if "R" in side: checks.append(("right", r, R))
            if "P" in side: checks.append((f"left = wrap + panel inset {o['pad']:g}", l, L + o["pad"]))
            flags = ["OK" if v is not None and abs(v - ref) < 0.51 else f"MISMATCH ({v} vs {ref:g})" for _, v, ref in checks]
            ok_all &= all(x == "OK" for x in flags)
            print(f"  {name:<32} left={l!s:<8} right={r!s:<8} {' / '.join(f'{c[0]} {x}' for c, x in zip(checks, flags))}")
    print("\nALL ALIGNED" if ok_all else "\nMISMATCHES FOUND")
    if "--guides" in sys.argv:
        from PIL import Image, ImageDraw
        src = sys.argv[sys.argv.index("--guides") + 1]
        o = measure(page, 1440); im = Image.open(src).convert("RGB"); dr = ImageDraw.Draw(im)
        for x in (o["left"], o["right"]):
            dr.line([(x, 0), (x, im.height)], fill=(179, 38, 30), width=1)
        out = src.replace(".png", "-guides.png"); im.save(out); print("guides:", out)

if __name__ == "__main__":
    main()
