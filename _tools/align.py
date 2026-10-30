#!/usr/bin/env python3
"""Alignment audit: at each width, measure left/right edges of the nav logo, the last nav
button, the h1, the ledger card, every section heading, the trust panel, and the footer logo.
All lefts must equal the wrap's content-left and all rights its content-right.
usage: align.py <page.html> [--guides out.png]   (guides: draws the wrap edges on a 1440 shot)
"""
import json, os, re, subprocess, sys, tempfile

# Every temp dir (Chrome profiles, iframe wrappers) is removed on exit so
# repeated QA runs don't fill the disk.
import atexit, shutil
_mkdtemp = tempfile.mkdtemp
_made = []
def _tracked_mkdtemp(*a, **k):
    d = _mkdtemp(*a, **k); _made.append(d); return d
tempfile.mkdtemp = _tracked_mkdtemp
atexit.register(lambda: [shutil.rmtree(d, ignore_errors=True) for d in _made])

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
JS = r"""
(() => {
  const d = f.contentDocument, r = e => e && e.getBoundingClientRect();
  const row = (name, e, side) => { const b = r(e); return b ? [name, Math.round(b.left*100)/100, Math.round(b.right*100)/100, side] : [name, null, null, side]; };
  const out = [];
  out.push(row('nav logo', d.querySelector('.nav-bar .brand'), 'L'));
  const btns = [...d.querySelectorAll('.nav-cta .btn')].filter(b => b.offsetParent !== null);
  out.push(row('last nav button', btns[btns.length-1], 'R'));
  const h1 = d.querySelector('h1'); if (h1 && !h1.closest('.center,.auth,.notfound')) out.push(row('h1', h1, 'L'));
  const hg = d.querySelector('.hero-grid');
  if (hg && hg.children.length > 1 && getComputedStyle(hg).gridTemplateColumns.split(' ').length > 1) out.push(row('hero right component', hg.lastElementChild, 'R'));
  // every full-width block directly inside a wrap must sit on the wrap's content edges
  d.querySelectorAll('main .wrap > *').forEach(e => {
    if (!/^(DIV|DL|UL|OL|TABLE|FORM|FIGURE)$/.test(e.tagName) || /section-head/.test(e.className)) return;
    if (e.classList.contains('hero-inner') || /hero-grid|two|faq-layout|doc-grid|auth-split/.test(e.parentElement.className) || e.closest('.center')) return;
    out.push(row('block ' + (e.className||e.tagName).split(' ').slice(0,2).join('.'), e, 'LR'));
  });
  // headings: on the wrap edge, or inset by their panel's own padding+border
  d.querySelectorAll('main h2').forEach(h => {
    const panel = h.closest('.trust,.band,.cta,.card,.card-quiet,.vig,.ledger,.form-card,.plate');
    if (panel) { const cs = getComputedStyle(panel); const inset = parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth); const pb = r(panel);
      out.push(['h2 ' + h.textContent.trim().slice(0,22) + ' (in panel)', Math.round(r(h).left*100)/100, Math.round(pb.left*100)/100, 'I', inset]); }
    else out.push(row('h2 ' + h.textContent.trim().slice(0,22), h, h.closest('.two,.grid,.faq-layout,.doc-grid') ? 'X' : 'L'));
  });
  out.push(row('footer logo', d.querySelector('.footer .brand'), 'L'));
  const w = d.querySelector('main .wrap') || d.querySelector('.nav-bar'); const cs = getComputedStyle(w); const wb = r(w);
  const left = wb.left + parseFloat(cs.paddingLeft), right = wb.right - parseFloat(cs.paddingRight);
  document.body.insertAdjacentHTML('beforeend', '<pre id="al'+'ign">' + JSON.stringify({left, right, rows: out, sw: d.documentElement.scrollWidth}) + '</p'+'re>');
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
        for name, l, r, side, *extra in o["rows"]:
            checks = []
            if l is None and r is None: continue
            if "L" in side: checks.append(("left", l, L))
            if "R" in side: checks.append(("right", r, R))
            if "I" in side: checks.append((f"left = panel edge + inset {extra[0]:g}", l, r + extra[0]))
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
