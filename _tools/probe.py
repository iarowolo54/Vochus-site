#!/usr/bin/env python3
"""Automated page checks in headless Chrome at a given width (default 360):
scrollWidth, tap targets ≥44x44 for a/button/summary/input/select, text contrast ≥4.5:1
(or 3:1 for ≥24px / ≥18.66px bold), and min font sizes (14px text, 16px controls).
usage: probe.py <page.html> [width]
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
  const d = f.contentDocument, w = f.contentWindow, W = f.offsetWidth;
  const vis = e => { const r = e.getBoundingClientRect(); const cs = w.getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden'; };
  const out = { scrollWidth: d.documentElement.scrollWidth, width: W, tap: [], contrast: [], small: [], overflow: [] };
  if (out.scrollWidth > W) d.querySelectorAll('body *').forEach(e => { const r = e.getBoundingClientRect(); if (r.right > W + 0.5 && r.width > 0 && !e.closest('.sheet,.menu') && out.overflow.length < 12) out.overflow.push(`${e.tagName.toLowerCase()}.${(e.className||'').toString().split(' ')[0]} right=${Math.round(r.right)} w=${Math.round(r.width)}`); });
  d.querySelectorAll('a[href],button,summary,input,select').forEach(e => {
    if (!vis(e)) return;
    let r = e.getBoundingClientRect();
    const ps = w.getComputedStyle(e, '::after');   // absolute ::after boxes extend the hit area
    if (ps.position === 'absolute' && ps.content !== 'none' && parseFloat(ps.height) >= 24) { /* a thin underline pseudo does not change the hit box */ const t = parseFloat(ps.top)||0, b = parseFloat(ps.bottom)||0, l = parseFloat(ps.left)||0, rr = parseFloat(ps.right)||0; r = { width: r.width - l - rr, height: r.height - t - b }; }
    // inline links inside running text are exempt (WCAG 2.5.8 inline exception); flag everything else
    const inline = e.tagName === 'A' && w.getComputedStyle(e).display === 'inline' && e.closest('p,li,figcaption,address,dd');
    if (!inline && (r.width < 44 || r.height < 44)) out.tap.push(`${e.tagName.toLowerCase()}.${(e.className||'').toString().split(' ')[0]} "${(e.textContent||e.value||'').trim().slice(0,30)}" ${Math.round(r.width)}x${Math.round(r.height)}`);
  });
  const parse = c => { const m = c.match(/[\d.]+/g).map(Number); return m.length === 4 ? m : [...m, 1]; };
  const lum = ([r,g,b]) => { const f = v => { v /= 255; return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); }; return .2126*f(r)+.7152*f(g)+.0722*f(b); };
  const bgOf = e => { let n = e; while (n && n !== d.documentElement) { const c = parse(w.getComputedStyle(n).backgroundColor); if (c[3] > 0) return c; n = n.parentElement; } return [255,255,255,1]; };
  const seen = new Set();
  d.querySelectorAll('body *').forEach(e => {
    if (!vis(e) || e.closest('svg,script,style')) return;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const cs = w.getComputedStyle(e), fs = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700;
    const fg = parse(cs.color), bg = bgOf(e);
    const L1 = lum(fg), L2 = lum(bg), ratio = (Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
    const need = (fs >= 24 || (fs >= 18.66 && bold)) ? 3 : 4.5;
    const key = `${e.tagName}.${e.className} ${cs.color} on rgb(${bg.slice(0,3)}) ${fs}px`;
    if (ratio < need && !seen.has(key)) { seen.add(key); out.contrast.push(`${key} = ${ratio.toFixed(2)}:1 "${e.textContent.trim().slice(0,30)}"`); }
    const ctrl = /INPUT|SELECT|TEXTAREA/.test(e.tagName);
    if ((fs < 14 || (ctrl && fs < 16)) && !seen.has('s'+key)) { seen.add('s'+key); out.small.push(`${key} "${e.textContent.trim().slice(0,30)}"`); }
  });
  d.querySelectorAll('input,select,textarea').forEach(e => { const fs = parseFloat(w.getComputedStyle(e).fontSize); if (vis(e) && fs < 16) out.small.push(`${e.tagName} ${e.id} ${fs}px`); });
  document.body.insertAdjacentHTML('beforeend', '<pre id="pr'+'obe">' + JSON.stringify(out).replace(/</g,'&lt;') + '</p'+'re>');
})();
"""

def main():
    page = os.path.abspath(sys.argv[1]); width = int(sys.argv[2]) if len(sys.argv) > 2 else 360
    wrap = os.path.join(tempfile.mkdtemp(), "probe.html")
    with open(wrap, "w") as fh:
        fh.write(f'<!doctype html><meta charset=utf-8><style>html,body{{margin:0}}iframe{{width:{width}px;height:800px;border:0;display:block}}</style>'
                 f'<iframe id=f src="file://{page}"></iframe><script>f.addEventListener("load",()=>setTimeout(()=>{{{JS}}},900))</script>')
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", "--no-first-run",
                        "--user-data-dir=" + tempfile.mkdtemp(), f"--window-size={max(width,500)},900", "--virtual-time-budget=4000",
                        "--dump-dom", "file://" + wrap], capture_output=True, text=True)
    m = re.search(r'<pre id="probe">(.*?)</pre>', r.stdout, re.S)
    if not m:
        sys.exit("probe failed: " + r.stderr[-500:])
    o = json.loads(m.group(1).replace("&lt;", "<").replace("&amp;", "&"))
    print(f"{os.path.basename(page)} @ {width}px — scrollWidth {o['scrollWidth']} ({'OK' if o['scrollWidth'] <= width else 'HORIZONTAL OVERFLOW'})")
    for k, label in (("overflow", "elements past the right edge"), ("tap", "tap targets < 44x44"), ("contrast", "contrast failures"), ("small", "text below minimum size")):
        print(f"  {label}: {len(o[k])}")
        for x in o[k]: print("    - " + x)

if __name__ == "__main__":
    main()
