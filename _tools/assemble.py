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
import datetime, glob, html, json, os, re, sys

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

# ---- Search: pages kept out of the index, and structured data ----
NOINDEX = {"saver-login.html", "agent-login.html", "forgot-password.html", "thanks.html", "404.html"}
ORG = {
    "@type": "Organization", "@id": SITE + "/#org",
    "name": "Vochus Easy Save",
    "alternateName": ["Vochus", "Easy Save", "Vochus EasySave", "VochusEasySave"],
    "url": SITE + "/",
    "logo": SITE + "/assets/img/icon-512.png",
    "email": "info@vochuseasysave.com",
    "telephone": "+2348033948570",
    "address": {"@type": "PostalAddress", "streetAddress": "286, Ikorodu Road, Anthony",
                "addressLocality": "Lagos", "addressCountry": "NG"},
    "areaServed": "NG",
    "parentOrganization": {"@type": "Organization", "name": "Zipwaves Technologies Limited"},
    "contactPoint": [{"@type": "ContactPoint", "contactType": "customer support", "email": "info@vochuseasysave.com",
                      "telephone": "+2348033948570", "areaServed": "NG", "availableLanguage": "en"}],
}
WEBSITE = {"@type": "WebSite", "@id": SITE + "/#website", "name": "Vochus Easy Save",
           "alternateName": ["Vochus", "Easy Save", "Vochus EasySave"], "url": SITE + "/",
           "publisher": {"@id": SITE + "/#org"}, "inLanguage": "en-NG"}

def strip_tags(x):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()

def jsonld(page, src, title, canonical):
    graph = []
    if page == "index.html":
        graph += [ORG, WEBSITE]
    elif page not in NOINDEX:
        name = title.split(" | ")[0].strip()
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": name, "item": canonical}]})
    if page == "faq.html":
        qa = re.findall(r'<details class="faq"><summary>(.*?)</summary><div class="ans">(.*?)</div></details>', src, re.S)
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in qa]})
    if not graph:
        return ""
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">' + data.replace("</", "<\\/") + "</script>\n"

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
        # LCP image: the hero photo, art-directed (graded full image >= 1024px, trader crop below)
        preload += ('<link rel="preload" as="image" type="image/webp" imagesrcset="assets/img/hero-trader-1376.webp 1376w, assets/img/hero-trader-1920.webp 1920w, assets/img/hero-trader-2752.webp 2752w" imagesizes="100vw" media="(min-width:1024px)" fetchpriority="high">\n'
                    '<link rel="preload" as="image" type="image/webp" imagesrcset="assets/img/hero-trader-m-640.webp 640w, assets/img/hero-trader-m-956.webp 956w, assets/img/hero-trader-m-1280.webp 1280w" imagesizes="100vw" media="(max-width:1023px)" fetchpriority="high">\n')
    head = (read("head.html").replace("{{CANONICAL}}", canonical).replace("{{TITLE}}", html.escape(title, quote=True))
            .replace("{{DESCRIPTION}}", html.escape(desc, quote=True)).replace("{{SITE}}", SITE).replace("{{PRELOAD}}", preload)
            .replace("{{ROBOTS}}", '<meta name="robots" content="noindex, follow">\n' if page in NOINDEX else "")
            .replace("{{JSONLD}}", jsonld(page, src, title, canonical)))
    nav = read("nav.html").replace("{{CTA}}", ctas(page))
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

def write_sitemap():
    pages = sorted(os.path.basename(p) for p in glob.glob(P("*.html")) if os.path.basename(p) not in NOINDEX)
    pages.remove("index.html"); pages.insert(0, "index.html")
    today = datetime.date.today().isoformat()
    rows = "".join(f"  <url><loc>{SITE}/{'' if p == 'index.html' else p}</loc><lastmod>{today}</lastmod></url>\n" for p in pages)
    body = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}</urlset>\n'
    with open(P("sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(body)

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
    if not sys.argv[1:]:
        write_sitemap()
