#!/usr/bin/env python3
"""Build the upload package: dist/ with only the deployable files, zipped to dist/vochus-website-YYYYMMDD.zip.

Included: every *.html page, send.php, send-config.php, .htaccess, robots.txt, sitemap.xml, and only the files under
assets/ that the pages or the stylesheet actually reference (src, srcset, href, CSS url()).
Excluded: _qa, _tools, _src, _docs, _partials, .git, dist itself, and any dry-run data.

    python3 _tools/package.py
"""
import datetime, glob, os, re, shutil, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
TOP = ["send.php", "send-config.php", ".htaccess", "robots.txt", "sitemap.xml", "favicon.ico"] + [os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "[0-9a-f]" * 32 + ".txt"))]   # + IndexNow key file

def refs_in(text):
    out = set()
    for m in re.finditer(r'(?:src|href|poster)="(assets/[^"#?]+)"', text):
        out.add(m.group(1))
    # absolute self-references (og:image in meta tags, the logo in JSON-LD)
    for m in re.finditer(r'https://(?:www\.)?vochuseasysave\.com/(assets/[^"#?\\]+)', text):
        out.add(m.group(1))
    for m in re.finditer(r'srcset="([^"]+)"', text):
        for part in m.group(1).split(","):
            u = part.strip().split(" ")[0]
            if u.startswith("assets/"):
                out.add(u)
    for m in re.finditer(r'url\((["\']?)(\.\./[^)"\']+|assets/[^)"\']+)\1\)', text):
        u = m.group(2)
        out.add("assets/" + u[3:] if u.startswith("../") else u)
    return out

def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    pages = sorted(p for p in os.listdir(ROOT) if p.endswith(".html"))
    assets = set()
    for p in pages:
        src = open(os.path.join(ROOT, p), encoding="utf-8").read()
        assets |= refs_in(src)
        shutil.copy2(os.path.join(ROOT, p), os.path.join(DIST, p))
    css = os.path.join(ROOT, "assets", "css", "style.css")
    assets |= refs_in(open(css, encoding="utf-8").read())
    for a in sorted(assets):
        srcp = os.path.join(ROOT, a)
        if not os.path.exists(srcp):
            sys.exit(f"referenced asset missing: {a}")
        os.makedirs(os.path.dirname(os.path.join(DIST, a)), exist_ok=True)
        shutil.copy2(srcp, os.path.join(DIST, a))
    for t in TOP:
        shutil.copy2(os.path.join(ROOT, t), os.path.join(DIST, t))
    stamp = datetime.date.today().strftime("%Y%m%d")
    zpath = os.path.join(DIST, f"vochus-website-{stamp}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(DIST):
            for f in files:
                full = os.path.join(base, f)
                if full == zpath:
                    continue
                z.write(full, os.path.relpath(full, DIST))
    n = sum(len(fs) for _, _, fs in os.walk(DIST)) - 1
    print(f"dist/: {len(pages)} pages, {len(assets)} assets, {len(TOP)} top-level files ({n} files)")
    print(f"zip: {os.path.relpath(zpath, ROOT)}  {os.path.getsize(zpath) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    main()
