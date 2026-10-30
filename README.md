# Vochus Easy Save website

The marketing website for **Vochus Easy Save**, a Nigerian digital savings platform (daily, weekly and monthly savings with 12% annual interest for online savers), and **Vochus Gift Cards**. Both are products of Zipwaves Technologies Limited.

Live at **https://vochuseasysave.com**. Registration, log-in and the Android apps live in the separate Vochus app at `easysave.vochusglobalservices.co.uk`; this site only links to it.

## What it is

- Static HTML pages, one stylesheet (`assets/css/style.css`) and one script (`assets/js/main.js`). No framework, no build step on the server.
- One PHP file, `send.php`, that emails the Contact and Agent application forms to info@vochuseasysave.com.
- Hosted on GO54 shared hosting (DirectAdmin, LiteSpeed). See [`_docs/DEPLOY.md`](_docs/DEPLOY.md).

Every page works without JavaScript; JS adds the interest calculator, form validation, mobile menu and motion. Motion is switched off for visitors who set "reduce motion".

## Pages

| Page | Purpose |
|---|---|
| `index.html` | Home |
| `how-it-works.html` | Steps, the three ways to save, interest calculator |
| `plans.html` | Daily, weekly, monthly and group savings plans |
| `interest.html` | How the 12% interest is worked out |
| `benefits.html`, `portal.html` | Benefits; the Customer Portal |
| `agent.html` | Become an agent, with the application form |
| `faq.html`, `contact.html`, `privacy.html` | FAQs, contact form, privacy policy |
| `login.html`, `saver-login.html`, `agent-login.html`, `forgot-password.html` | Choosers that link into the Vochus app (no passwords are collected here) |
| `thanks.html`, `404.html` | Form confirmation (no-JS path), page not found |

## Repository layout

```
*.html               the pages (deployed as they are)
assets/              css, js, fonts, img (deployed)
send.php             form handler (deployed)
send-config.php      form recipient and sender addresses (deployed; blocked from the web by .htaccess)
.htaccess            HTTPS + www redirect, 404 page, security headers, caching (deployed)
robots.txt, sitemap.xml
_partials/           shared head, nav, footer and icon sprite, stamped into every page
_tools/              Python build and QA scripts (not deployed)
_src/                source photography for the hero (not deployed)
_docs/               design spec, deploy guide, copy for client approval (not deployed)
```

## Editing

The nav, footer, `<head>` and icon sprite come from `_partials/`. Edit the partial, then stamp it into every page:

```sh
python3 _tools/assemble.py
```

`assemble.py` also holds the single list of app URLs (`APP_BASE`, register, log-in, reset, APK downloads) and the canonical site URL. Change them there, re-run it and commit the pages it rewrites.

Page content is edited directly in each `.html` file. Client wording is kept verbatim; any change to it is listed in [`_docs/copy-for-approval.md`](_docs/copy-for-approval.md).

## Checks

The QA scripts need Python 3 and Google Chrome; `hero.py` and `shoot.py` also need Pillow.

```sh
python3 _tools/linkcheck.py *.html                 # broken links, missing #ids, unsafe new-tab links
python3 _tools/probe.py index.html 360             # overflow, 44px tap targets, contrast, minimum font sizes
python3 _tools/align.py index.html                 # every section lines up with the content edges
python3 _tools/shoot.py --widths 360,1440 out/ index.html   # full-page screenshots
python3 _tools/copydiff.py index.html              # wording changes against the original site
```

`_tools/hero.py` regrades and re-exports the homepage hero photo from `_src/`.

## Forms

Both forms post to `send.php`, which validates the fields, rejects header injection, filters spam (a honeypot field, a minimum fill time and 5 submissions per IP per hour) and sends with PHP `mail()` from noreply@vochuseasysave.com, with Reply-To set to the visitor. With JavaScript it answers in JSON and the page shows the result in place; without it, it redirects to `thanks.html` or back to the form.

Rate-limit data is written to `vochus-data/`, one level above the web root. To test locally without sending mail (PHP 8.1+):

```sh
VOCHUS_MAIL_DRYRUN=1 php -S 127.0.0.1:8000
```

Dry-run writes each composed email to `../vochus-data/` instead of sending it.

## Deploying

```sh
python3 _tools/package.py
```

This builds `dist/` with only the deployable files and zips it to `dist/vochus-website-YYYYMMDD.zip`. For a full first install, follow [`_docs/DEPLOY.md`](_docs/DEPLOY.md). For small changes, upload just the changed files to `public_html` in the DirectAdmin File Manager.
