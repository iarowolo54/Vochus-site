#!/usr/bin/env python3
"""Walk every href/src in the given pages: local files must exist, same-page #ids must exist,
no javascript: URLs, external links must not open in a new tab without rel=noopener.
usage: linkcheck.py <page.html>...
"""
import os, re, sys

def ids_of(src): return set(re.findall(r'\sid="([^"]+)"', src))

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bad = 0
    for page in sys.argv[1:]:
        path = os.path.join(root, os.path.basename(page)); src = open(path, encoding="utf-8").read()
        ids = ids_of(src)
        for attr, url in re.findall(r'\b(href|src|srcset)="([^"]+)"', src):
            urls = [u.strip().split(" ")[0] for u in url.split(",")] if attr == "srcset" else [url]
            for u in urls:
                if u.startswith(("mailto:", "tel:", "data:")): continue
                if u.startswith("javascript:"): print(f"JAVASCRIPT URL {page}: {u}"); bad += 1; continue
                if u.startswith(("http://", "https://")):
                    tag = re.search(r'<a[^>]*href="' + re.escape(u) + r'"[^>]*>', src)
                    if tag and 'target="_blank"' in tag.group(0) and "noopener" not in tag.group(0): print(f"NOOPENER {page}: {u}"); bad += 1
                    continue
                file_part, _, frag = u.partition("#"); file_part = file_part.split("?")[0]
                if file_part:
                    target = os.path.normpath(os.path.join(os.path.dirname(path), file_part))
                    if not os.path.exists(target): print(f"MISSING FILE {page}: {u}"); bad += 1; continue
                    if frag:
                        if frag not in ids_of(open(target, encoding="utf-8").read()): print(f"MISSING ANCHOR {page}: {u}"); bad += 1
                elif frag and frag not in ids:
                    print(f"MISSING ANCHOR {page}: #{frag}"); bad += 1
        print(f"{page}: checked")
    print(f"{bad} problem(s)")

if __name__ == "__main__":
    main()
