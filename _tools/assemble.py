#!/usr/bin/env python3
"""Stamp the shared partials into every page that carries the markers, and
point every app link at the one APP config below. Run by hand after editing a
partial or a page; commit the output. The host never runs this.

    python3 _tools/assemble.py            # all pages with markers
    python3 _tools/assemble.py index.html # one page

Markers (each pair is replaced wholesale, so re-running is idempotent):
    <!-- head --> ... <!-- /head -->      shared <head> block (built from the page's own <title> and description)
    <!-- nav --> ... <!-- /nav -->        header + mobile sheet, active page and page-specific CTAs
    <!-- footer --> ... <!-- /footer -->  footer
    <!-- sprite --> ... <!-- /sprite -->  lucide <symbol> sprite, only the icons the page references
App links are any <a ... data-app="KEY"> — their href is (re)written from APP.
"""
import glob, html, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

SITE = "https://vochuseasysave.com"

# ---- The ONE place app destinations live (§10). Also stamped into assets/js/main.js. ----
APP_BASE = "https://easysave.vochusglobalservices.co.uk"   # confirmed by the client 2026-10-29 (spec §10)
APP = {
    "register":     APP_BASE + "/customer/enroll",
    "saver_login":  APP_BASE + "/customer/login",
    "saver_reset":  APP_BASE + "/customer/forgot-password",
    "agent_login":  APP_BASE + "/",
    "agent_reset":  APP_BASE + "/forgot-password",
    "apk_customer": APP_BASE + "/downloads/easysave-customer.apk",
    "apk_agent":    APP_BASE + "/downloads/easysave-agent.apk",
}

AUTH_PAGES = {"login.html", "saver-login.html", "agent-login.html", "forgot-password.html"}   # minimal header: logo + Back to website

ARROW = '<svg class="ico" aria-hidden="true"><use href="#i-arrow-right"/></svg>'
def btn(cls, href, label, app=None):
    attrs = f' data-app="{app}" rel="noopener"' if app else ""
    return f'<a class="btn {cls} btn-sm" href="{href}"{attrs}>{label}</a>'

def ctas(page):
    """Header CTAs: Home leads with the saver action; agent.html leads with the agent action."""
    if page == "index.html":
        return btn("btn-secondary", "agent.html", "Apply as an Agent") + "\n      " + btn("btn-primary", APP["register"], "Start Earning Interest", "register")
    if page == "agent.html":
        return btn("btn-secondary", "login.html", "Log In") + "\n      " + btn("btn-primary", "#apply", "Apply as an Agent")
    return btn("btn-secondary", "login.html", "Log In") + "\n      " + btn("btn-primary", APP["register"], "Start Earning Interest", "register")

def between(src, name, body):
    pat = re.compile(rf"<!-- {name} -->.*?<!-- /{name} -->", re.S)
    if not pat.search(src):
        return src
    return pat.sub(lambda m: f"<!-- {name} -->\n{body}<!-- /{name} -->", src)

def read(name):
    with open(P("_partials", name), encoding="utf-8") as fh:
        return fh.read()

def sprite_for(src):
    used = sorted(set(re.findall(r'href="#i-([a-z0-9-]+)"', src)))
    full = read("sprite.html")
    syms = {m.group(1): m.group(0) for m in re.finditer(r'<symbol id="i-([a-z0-9-]+)".*?</symbol>', full, re.S)}
    missing = [u for u in used if u not in syms]
    if missing:
        sys.exit(f"icons missing from _partials/sprite.html: {missing}")
    body = "".join(syms[u] for u in used)
    return f'<svg xmlns="http://www.w3.org/2000/svg" hidden aria-hidden="true">{body}</svg>\n'

def assemble(path):
    page = os.path.basename(path)
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    title = re.search(r"<title>(.*?)</title>", src, re.S)
    desc = re.search(r'<meta name="description" content="(.*?)"', src, re.S)
    title = html.unescape(title.group(1).strip()) if title else "Vochus Easy Save"
    desc = html.unescape(desc.group(1).strip()) if desc else ""
    canonical = SITE + "/" + ("" if page == "index.html" else page)
    preload = ""
    if page == "index.html":
        preload = ('<link rel="preload" href="assets/fonts/PlusJakartaSans-var-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
                   '<link rel="preload" href="assets/fonts/Inter-400-latin.woff2" as="font" type="font/woff2" crossorigin>\n')
    head = (read("head.html").replace("{{CANONICAL}}", canonical).replace("{{TITLE}}", html.escape(title, quote=True))
            .replace("{{DESCRIPTION}}", html.escape(desc, quote=True)).replace("{{SITE}}", SITE).replace("{{PRELOAD}}", preload))
    nav = read("nav-auth.html") if page in AUTH_PAGES else read("nav.html").replace("{{CTA}}", ctas(page))
    # active page: aria-current on the matching link(s)
    nav = re.sub(rf'<a href="{re.escape(page)}">', f'<a href="{page}" aria-current="page">', nav)
    out = between(src, "head", head)
    out = between(out, "nav", nav)
    out = between(out, "footer", read("footer.html"))
    # app links: rewrite href from APP by key
    out = re.sub(r'href="[^"]*"( [^>]*?)?data-app="([a-z_]+)"',
                 lambda m: f'href="{APP[m.group(2)]}"{m.group(1) or ""}data-app="{m.group(2)}"', out)
    out = between(out, "sprite", sprite_for(out))  # last, so it sees every icon the partials added
    if out != src:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(out)
    return out != src

def stamp_js():
    js_path = P("assets", "js", "main.js")
    with open(js_path, encoding="utf-8") as fh:
        js = fh.read()
    obj = "{" + ",".join(f'{k}:"{v}"' for k, v in APP.items()) + "}"
    new = re.sub(r"/\* app-urls:start \*/.*?/\* app-urls:end \*/", f"/* app-urls:start */{obj}/* app-urls:end */", js, flags=re.S)
    if new != js:
        with open(js_path, "w", encoding="utf-8") as fh:
            fh.write(new)

if __name__ == "__main__":
    pages = [P(a) for a in sys.argv[1:]] or sorted(glob.glob(P("*.html")))
    stamp_js()
    for p in pages:
        with open(p, encoding="utf-8") as fh:
            if "<!-- nav -->" not in fh.read():
                continue
        print(("updated " if assemble(p) else "ok      ") + os.path.basename(p))
