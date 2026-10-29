#!/usr/bin/env python3
"""Text-node diff between the committed original page and the rebuilt one.
usage: copydiff.py <page.html>   (compares `git show 7807f64:<page>` with the working file)

Text is taken from <body>, split at block boundaries, whitespace-normalised and compared as
multisets. Stripped before comparing: <script>/<style>, <svg>, <sup> footnote markers,
.sr-only text, and `→`/`▾` glyphs (replaced by icons per spec §8.1). Everything else counts.
"""
import collections, html, re, subprocess, sys, os

BASELINE = "7807f64"
BLOCK = r"</?(p|h[1-6]|li|div|section|article|header|footer|nav|figure|figcaption|dt|dd|td|th|tr|table|ul|ol|br|hr|main|form|fieldset|legend|label|button|summary|details|blockquote|address|aside|picture|span|strong|em|a|select|option)\b[^>]*>"

def lines(src):
    body = re.search(r"<body.*?</body>", src, re.S)
    s = body.group(0) if body else src
    s = re.sub(r"<(script|style|svg|template)\b.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r"<sup\b.*?</sup>", " ", s, flags=re.S)
    s = re.sub(r'<[^>]+class="[^"]*sr-only[^"]*"[^>]*>.*?</[a-z0-9]+>', " ", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(BLOCK, "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("→", " ").replace("▾", " ")
    out = []
    for ln in s.split("\n"):
        ln = re.sub(r"\s+", " ", ln).strip(" ·")
        if ln:
            out.append(ln)
    return out

def main():
    page = sys.argv[1]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    old = subprocess.run(["git", "-C", root, "show", f"{BASELINE}:{os.path.basename(page)}"], capture_output=True, text=True).stdout
    new = open(os.path.join(root, os.path.basename(page)), encoding="utf-8").read()
    a, b = collections.Counter(lines(old)), collections.Counter(lines(new))
    removed, added = a - b, b - a
    print(f"== {page}: {sum(a.values())} text lines before, {sum(b.values())} after")
    print(f"-- REMOVED ({sum(removed.values())}):")
    for k, n in removed.items(): print(f"  - {k}" + (f"  (x{n})" if n > 1 else ""))
    print(f"-- ADDED ({sum(added.values())}):")
    for k, n in added.items(): print(f"  + {k}" + (f"  (x{n})" if n > 1 else ""))

if __name__ == "__main__":
    main()
