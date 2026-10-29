# Vochus Easy Save — marketing website audit & redesign spec

Site: `/Users/mac/Developer/vochus-website` (static HTML, cPanel `public_html`, no build step).
Scope of this document: audit + design spec only. No site files were edited.
References: Zopa savings marketing pages (what goes on the page, how a rate is shown with footnotes, trust block, FAQs, legal footer) and current Wise marketing (off-white canvas, white rounded cards, big sans headlines, numbered steps, pill CTAs, full-bleed photography). Craft bar: Stripe (typography precision, grid, border/shadow system, states, restrained motion).

Hard rules carried through every section: client wording is preserved verbatim; no gradients, glows, glass, gold, emoji, watermarks or carousels; brand tokens shared with the app; excellent at 360 px; static HTML + one CSS file + small progressive vanilla JS.

---

## 0. How the audit was done (so findings can be reproduced)

- Every page read with base64 stripped (`<scratchpad>/*.nob64.html`). Without images each page is 5–20 KB of HTML; the 150–740 KB on disk is base64.
- Screenshots: `<scratchpad>/shot-<page>-{390,1440}.png` (headless Chrome, OS colour scheme = dark). **Caveat:** headless Chrome clamps the window to ~500 px, so the `-390` files are cropped renders, not true 390 px layouts. True-width renders were made by wrapping each page in a 360/390 px iframe: `<scratchpad>/m-dark-<page>-{360,390}.png`. A forced-light copy (dark-mode media query removed from a *copy* of `style.css`) was rendered to `<scratchpad>/m-light-*.png` and `<scratchpad>/L-<page>-1440.png`.
- Link inventory, image mapping and contrast ratios were computed by script (results below).
- Image sources: `<scratchpad>/imgs/`. Mapping of CSS vars to files: `--img-a` = `f5eb5770.jpg` (900×909, registration queue, man signing a form), `--img-b` = `34459893.jpg` (1280×853, women in line), `--img-c` = `c6613c60.jpg` (1280×853, celebration crowd). Logo = `a70595e3.png` (247×220 glossy PNG, 52 KB, inlined 3× per page = 45+ copies across the site, plus once more as the favicon on 14 pages).

Severity scale: **S1** blocks users or breaks the page · **S2** materially hurts trust, usability or speed · **S3** polish.

---

## 1. Audit

### 1.1 Site-wide findings

| # | Finding | Severity |
|---|---|---|
| A1 | **Footer is unreadable in dark mode (the "empty footer").** `footer{background:var(--ink)}` and the dark-mode block flips `--ink` to `#E2EFE6`, so the footer becomes near-white while its text stays `rgba(228,240,232,…)` (white-ish). Only the logo and the green domain link survive. Any Android phone with dark mode on (very common on low-end devices to save battery) sees this on every page. Light mode is fine. Root cause: tokens are re-purposed (an "ink" colour used as a background) and then inverted. | S1 |
| A2 | **Page weight.** 147–740 KB per page, ~95 % base64. The logo (52 KB PNG) is inlined 3× per page + as favicon; the three photos (96/123/153 KB JPEG, +33 % as base64) are embedded in CSS vars so they cannot be lazy-loaded, cached across pages, or served responsively. A saver on 3G downloads ~1 MB for Home + one inner page. Target: Home ≤ 250 KB incl. images, inner pages ≤ 120 KB (see §7). | S1 |
| A3 | **Auto dark theme** (`prefers-color-scheme: dark` + `[data-theme=dark]`) turns the whole site near-black, which is where the "dark, AI-looking" impression comes from. There is no toggle; the site should ship one deliberate light theme and *not* opt into dark mode (the product app is light). | S2 |
| A4 | **Primary CTA is aimed at the wrong audience.** The nav's filled button, the hero's primary button and the big strip near the bottom all say "Apply as an Agent →"; the saver action ("Start Earning Interest →") is buried inside the rate card, which is `display:none` under 860 px — **mobile visitors never see a saver CTA or the rate table.** | S1 |
| A5 | **No `<h1>` on any inner page** (all use `<h2>`), and the Home `<h1>` is fine. Section labels are `<div>`s, breadcrumbs not in a `<nav>`, no skip link, no `<main>` landmark on 404 (it is `<main class="page-404">` — ok) but `<nav>` has no `aria-label`. | S2 |
| A6 | **Mobile menu accessibility.** Hamburger has `aria-label="Menu"` but no `aria-controls`, no initial `aria-expanded`, is 38 px tall (<44). Menu items are 15 px text with 10 px padding (≈39 px tall). "Support ▾" dropdown button has no `aria-expanded`/`aria-haspopup`. Menu opens on hover on desktop and closes on any document click; it cannot be closed with Esc. | S2 |
| A7 | **Decorative "code" labels instead of icons**: `01 / PLN / INT / BEN`, `DAY / WK / MO / GRP`, `12% / BVN / 100% / NGN / GRP / AGT / TRK / DSC / NEW`, `MSG / TEL / HQ / AGT`, `SVR / AGT`, `BAL / LOG / PAY / AGT / PLN / NEW`, `01/02/03`. These read as unfinished placeholders. All proposed for removal (see §8.1). | S2 |
| A8 | **Contrast failures (dark theme):** `.hs-lbl` 9.5 px at 45 % white, `.footer-rc` 11 px at 25 % white, `.int-note` 11.5 px at 40 %, `.int-table th` 10 px at 38 %. Light theme is mostly AA, but 9.5–11 px text is below any sensible minimum for a phone. | S2 |
| A9 | **Fonts.** Georgia/Cambria serif for display + system sans for body. Georgia's lining figures and the `%` glyph make "12%" look like a newspaper headline; no tabular figures for money anywhere. | S2 |
| A10 | **Breakpoint gap.** Desktop nav collapses at 1180 px, so tablets and small laptops (768–1180) get the hamburger; under 480 px `.nav-actions` disappears, so phones have *no* log-in affordance in the header at all. | S2 |
| A11 | **Links that go nowhere useful.** Footer "Starter Pack", "65% Commission", "Agent Portal" all link to `agent.html` (the application form). `faq.html` has `#contact` (no such id on the page → dead). Mobile menu "Community" → `index.html#community` (an anchor on another page; fine, but it is a section not a page). `https://www.vochuseasysave.com/register` opens `target="_blank"` with no `rel="noopener"`. | S2 |
| A12 | **Login forms POST real credentials cross-origin** from a static page to `https://www.vochuseasysave.com/login` / `/agent` (`main.js` → `VOCHUS_PORTAL`). A marketing site must not collect passwords; this also trains users to type passwords into pages that are not the app. Forgot-password composes a `mailto:` containing account identifiers. To be replaced by a chooser that links into the real app (§3.11). | S1 |
| A13 | **Forms that only open a mail client** (Contact, Agent application). On Android with no mail app configured, nothing happens; the success banner still says "Your email app should have opened". Contact form labels have no `for`/`id` pairing, so tapping a label does not focus the field; JS reads fields by index (`f0[2]`), brittle. | S2 |
| A14 | **Motion.** Hero carousel (3 slides, 21 s loop, scale 1.04→1.12), pulsing dot, hover lift/translate on every card, scroll-in animations that set `opacity:0` via JS (the Interest page's four worked examples render invisible until the observer fires — visible in `L-interest-1440.png`). Only the hero honours `prefers-reduced-motion`. | S2 |
| A15 | **Head metadata.** No Open Graph / Twitter tags, no canonical, `theme-color` is the old forest green, favicon is a 52 KB base64 PNG per page (should be one cached file + SVG). 404 has no description/theme-color. | S3 |
| A16 | **Same 110-line nav + footer pasted into 15 files**; any change is 15 edits. Acceptable for static hosting but needs a single source + a tiny copy script during the build pass (no runtime build). | S3 |
| A17 | Smooth scrolling forced via `html{scroll-behavior:smooth}` without reduced-motion guard. | S3 |

### 1.2 Per-page findings

**index.html** (740 KB)
- S1 A4: saver CTA hidden on mobile; rate table hidden on mobile.
- S1 Hero is a carousel with dots over 3 photos behind a 70–94 % green wash, grid overlay (`.hero-noise`), radial glow, pill eyebrow, pulsing dot, 160 px ghost "12%" behind the card, 200 px "AGENT" watermark. All banned by the brand rules.
- S2 Trust strip ("12% Annual Interest Paid · Daily Weekly & Monthly Plans · BVN Identity Verified · 100% Full Payout at Cycle End") duplicates the hero stat bar ("12% Annual Interest · ₦0 Hidden Charges · 100% Online · 5 min To Register") — two stat rows back to back.
- S2 "Explore Vochus" cards are a second navigation; useful on mobile, redundant on desktop. Keep but demote.
- S2 Community photo grid: captions overlaid on a gradient wash; `role="img"` divs instead of `<img>` (no lazy-load, no responsive sizes).
- S3 Testimonial photo (`7a777f4d`, 4 KB) is a 104 px square used at 54 px — fine, but it is the only face on the page and needs a real name/consent (see C5 in §8).
- Mobile (360): hero stat bar becomes a 4-row vertical table of 9.5 px labels; trust strip becomes 2×2; section headings wrap awkwardly ("Everything you / need to start saving").

**how-it-works.html** (220 KB) — a single 3-step section then the footer; the page is 60 % footer on desktop. Steps are three identical circles on a dashed line (template pattern). Step 1 says "no app download needed" — see open question Q3. No CTA at all on the page.

**plans.html** (222 KB) — four cards with coloured top stripes (orange, forest, blue, pine — four off-brand hues), text-code icons, a pill "12% p.a. interest". Card footers ("Start saving daily →") are `div`s with `cursor:pointer` and **no link** — they look clickable and do nothing (S1). Group card says "Community payout" instead of an interest statement, while the FAQ says group contributions earn 12 % (copy note C4). Below 480 px cards stack to one column — fine.

**interest.html** (223 KB) — dark section only; on desktop the right card is taller than the left column leaving ~400 px of empty dark canvas. The four worked examples start at `opacity:0` (JS) and are invisible until the observer fires. Rate table header 10 px at 38 % alpha (fails contrast). The CTA "Start Earning 12% Today →" is the only saver CTA with a real target and it lives only here.

**benefits.html** (222 KB) — 9 cards, 3×3, each with a two-to-three-letter code in a coloured square (6 different hues). Dense, equal-weight grid; nothing is prioritised. No CTA.

**agent.html** (352 KB) — the only page with both a photo and a form. Form submits via `mailto:` (A13). Perk list uses a proper SVG check (good). The photo is `--img-b` again (used in 3 places site-wide). `h3` styled inline. Form fields 14 px on mobile → iOS zooms on focus (needs 16 px).

**faq.html** (233 KB) — the strongest content page: 36 Q&As in 7 groups, native `<details>`, a working client-side search. Issues: `<summary>` contains the `+` icon as text inside the accessible name; group labels are `div`s not headings; `#contact` link dead; search input 15 px (zoom on iOS); "FAQ" eyebrow above "Frequently Asked Questions" is redundant.

**contact.html** (390 KB) — photo + 4 contact rows + form. "Call or WhatsApp" has `tel:` links only, no `wa.me` link. Labels not associated with inputs. Success copy claims "we'll be in touch within one business day" then JS overwrites it with the mail-app text. Two phone numbers, no indication which is WhatsApp (Q6).

**privacy.html** (222 KB) — readable long-form; `h3`s should be `h2`s under a page `h1`. No table of contents; fine at this length. Cites NDPR (see copy note C9).

**404.html** (147 KB) — no favicon/description/theme-color; giant serif "404" in forest green on near-black; otherwise fine. Should offer links to the main sections.

**login.html** (500 KB) — a 50/50 split with a full-height photo panel that pushes the chooser card below the fold on short laptops and gives mobile a 260 px decorative photo before any content. The chooser itself (Saver / Agent) is the right idea and is kept.

**saver-login.html / agent-login.html** (501 KB each) — real username/password forms posting cross-origin (A12). Tab switch (`.lf-switch`) is two links with `role="tablist"` but no `role="tab"`. To be replaced.

**forgot-password.html** (501 KB) — composes a mailto with account identifiers (A12). To be replaced.

**portal.html** (241 KB) — a marketing page for the Customer Portal (6 feature cards + "How to get started"), with a 4-face avatar row of unnamed people. Two CTAs (Log In / Create an Account). Keep as a content page; it is the natural home of the "product vignette" signature moment (§4.4).

### 1.3 Navigation & footer link inventory (identical on all 15 pages)

Header, desktop (`.nav-links`): Home → `index.html` · How It Works → `how-it-works.html` · Savings Plans → `plans.html` · Interest → `interest.html` · Benefits → `benefits.html` · Become an Agent → `agent.html` · **Support ▾** (dropdown): Customer Portal → `portal.html`, FAQs → `faq.html`, Contact → `contact.html`, Privacy Policy → `privacy.html`.
Header actions: Log In → `login.html` (ghost) · Apply as an Agent → → `agent.html` (gold).
Mobile menu: the same plus **Community → `index.html#community`** (mobile only), Log In, Apply as an Agent.

Footer, four columns:
- Brand: logo, "Vochus Easy Save", tagline, "Vochus Global Services Ltd / Nigeria / 286, Ikorodu Road, Anthony, Lagos, Nigeria", `mailto:info@vochuseasysave.com`, `tel:+2348033948570`, `tel:+2347016634230`.
- Product: Savings Plans → `plans.html` · Interest → `interest.html` · How It Works → `how-it-works.html` · Benefits → `benefits.html`.
- For Agents: Become an Agent → `agent.html` · Starter Pack → `agent.html` · 65% Commission → `agent.html` · Agent Portal → `agent.html` (three fake destinations).
- Support: Customer Portal → `portal.html` · FAQs → `faq.html` · Contact → `contact.html` · Privacy Policy → `privacy.html`.
- Bottom: "© 2026 Vochus Global Services Ltd. All rights reserved." · "www.vochuseasysave.com" (plain text, not a link).

External: `https://www.vochuseasysave.com/register` (index rate card, interest, portal; `target=_blank`, no `rel`). JS: `https://www.vochuseasysave.com/login`, `/agent` (form actions). Broken: `faq.html#contact`.
Not present anywhere: Terms of use, complaints procedure, regulator/registration number, social links, app-store links.

### 1.4 Current colour contrast (for the record)

Old palette: forest on gold 5.31 ✓, sage on forest 4.48 ✓ (large only), muted on cream 5.38 ✓; the dark-theme alpha text listed in A8 fails.
New tokens: white on fill `#17783A` 5.55 ✓ · ink-green `#146C34` on white 6.51 ✓ · on tint `#E7F3EA` 5.71 ✓ · ink-2 `#5E6B64` on white 5.58 ✓ / on canvas `#F3F3F6` 5.04 ✓ · **ink-3 `#8B948F` on white 3.12 ✗ / on canvas 2.82 ✗** → ink-3 is restricted to non-text (dividers, disabled, placeholder icons) and to text ≥ 24 px. Captions and footnotes use ink-2.

---

## 2. Design system

### 2.1 Tokens (`:root` in `style.css`)

```css
:root{
  /* colour — shared with the app */
  --fill:#17783A;      /* buttons, selected state; always white text on it */
  --fill-hover:#146C34;
  --fill-active:#0F5A2B;
  --ink-green:#146C34; /* green text, icons, links */
  --tint:#E7F3EA;      /* soft green surfaces, icon tiles, highlighted row */
  --canvas:#F3F3F6;    /* page background */
  --surface:#FFFFFF;   /* cards, nav, footer */
  --line:#E6E6EB;      /* hairlines */
  --line-strong:#D5D7DD;
  --ink:#0F2A1D;       /* headings, body */
  --ink-2:#5E6B64;     /* secondary text, captions, footnotes */
  --ink-3:#8B948F;     /* non-text only: dividers, disabled, decorative numerals ≥24px */
  --danger:#B3261E;    /* form errors only */
  --focus:#146C34;

  /* type */
  --font-display:"Plus Jakarta Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --font-body:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;

  /* spacing (4px base) */
  --s-1:4px; --s-2:8px; --s-3:12px; --s-4:16px; --s-5:24px; --s-6:32px; --s-7:48px; --s-8:64px; --s-9:96px;
  --section-y:clamp(56px,8vw,96px);
  --gutter:clamp(16px,4vw,32px);
  --measure:62ch;      /* max line length for running text */
  --wrap:1200px;

  /* radii */
  --r-pill:999px; --r-xl:24px; --r-lg:16px; --r-md:12px; --r-sm:8px;

  /* layered shadow + border system (Stripe-style: border does the work, shadow is quiet) */
  --shadow-1:0 1px 2px rgba(15,42,29,.06);
  --shadow-2:0 1px 2px rgba(15,42,29,.06),0 4px 12px rgba(15,42,29,.06);
  --shadow-3:0 2px 4px rgba(15,42,29,.06),0 12px 32px rgba(15,42,29,.10);

  /* motion */
  --ease:cubic-bezier(.2,.7,.2,1); --t-fast:120ms; --t-base:200ms;
}
@media (prefers-reduced-motion:reduce){:root{--t-fast:0ms;--t-base:0ms} html{scroll-behavior:auto}}
```
No dark-mode block. `color-scheme: light` on `:root`; `<meta name="theme-color" content="#FFFFFF">` (nav is white) — the app can keep its own.

### 2.2 Type scale (6 sizes, fluid at the top)

| Token | Size | Face / weight | Tracking | Line-height | Use |
|---|---|---|---|---|---|
| `--t-display` | clamp(40px, 7vw, 72px) | Display 800 | −0.03em | 1.02 | Home h1 only |
| `--t-h1` | clamp(32px, 5vw, 52px) | Display 800 | −0.025em | 1.08 | Inner-page h1 |
| `--t-h2` | clamp(26px, 3.4vw, 36px) | Display 700 | −0.02em | 1.15 | Section headings |
| `--t-h3` | 20px | Display 700 | −0.01em | 1.3 | Card titles, FAQ questions |
| `--t-body` | 17px (16px <400px) | Body 400 | 0 | 1.6 | Paragraphs, FAQ answers |
| `--t-small` | 14px | Body 500 | 0 | 1.5 | Captions, footnotes, labels, nav |

Rules: `text-wrap: balance` on headings, `text-wrap: pretty` on paragraphs; max line length `--measure`; **all money and percentages use `font-variant-numeric: tabular-nums`**; display numerals (the 12 %, ledger totals) are Display 800 with `-0.04em` tracking; the ₦ sign is set as `<span class="naira">₦</span>` in Inter 500 at 0.8em, baseline-aligned, ink-2 — the number stays ink (see §4.5). Nothing below 14 px anywhere; nothing below 16 px in a form control.

Font loading: self-hosted woff2, latin subset only: Plus Jakarta Sans 700 + 800, Inter 400 + 500 + 600 (≈ 95 KB total, cached site-wide), `font-display: swap`, preload the two display files on Home. Fallback stacks are metric-close (system-ui) so swap is not jarring.

### 2.3 Layout

- `.wrap{max-width:var(--wrap);margin-inline:auto;padding-inline:var(--gutter)}`; 12-col grid on ≥1024, 6-col on 600–1023, 4-col (single column) below. Column gap 24 px. Every component snaps to the 4 px spacing scale.
- Vertical rhythm: section padding `--section-y`; heading → sub-copy 12 px; sub-copy → content 40 px; card internal padding 24 px (20 px <400 px).
- Breakpoints: 400 / 600 / 900 / 1200. Nav collapses at **900**, not 1180.
- Alignment: left-aligned headings by default (Wise). Centred only on the FAQ and 404.

### 2.4 Buttons

Pill (`--r-pill`), height 48 px (44 px for `.btn-sm` in nav), padding 0 22 px, Body 600 16 px, inline SVG icon 18 px with 8 px gap; icon is a lucide `arrow-right`, never a `→` character.

| Variant | Rest | Hover | Active | Focus-visible | Disabled |
|---|---|---|---|---|---|
| `.btn-primary` | fill / white | `--fill-hover` | `--fill-active`, `transform:translateY(1px)` | 2 px ring `--focus` offset 3 px | 40 % opacity, no pointer |
| `.btn-secondary` | surface, 1 px `--line-strong`, ink | tint background, border ink-green | translateY(1px) | same ring | same |
| `.btn-ghost` (text link) | ink-green, underline offset 4 px on hover | | | ring | |

Transitions: `background-color, border-color var(--t-fast)`, `transform var(--t-fast)`. No translateY(-2px) "lift", no shadow bloom.

### 2.5 Cards

`.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-xl);padding:var(--s-5);box-shadow:var(--shadow-1)}`. Interactive cards (`a.card`) get `box-shadow:var(--shadow-2)` and `border-color:var(--line-strong)` on hover, the focus ring on focus-visible, and the title colour turns ink-green; no movement. Card title Display 700 20 px, body 16 px ink-2, optional top-left icon tile 40×40 `--tint` radius `--r-md` holding a 20 px ink-green lucide SVG.

Variants: `.card-tint` (tint background, no border — for the single highlighted item in a row), `.card-ledger` (see §4.1), `.card-quiet` (no shadow, dashed `--line` border — for footnote/small-print blocks).

### 2.6 Section patterns (the vocabulary every page is built from)

1. **Hero** — left: label (Body 500 14 px ink-green, no chip), h1, sub, 2 buttons; right: one component (ledger card on Home, photo elsewhere). Canvas background, no photo wash.
2. **Rate statement** (Zopa) — one large figure + unit + footnote marker, footnote text immediately below in ink-2 14 px. Never a figure without its footnote in the same viewport.
3. **Numbered steps** (Wise) — 3 items on one connected path (§4.3), numerals Display 800 in tint circles 40 px.
4. **Feature grid** — 3-col cards with icon tiles; on mobile a 1-col list with icon on the left (no card borders) to save height.
5. **Trust block** (Zopa "Your money is protected") — tint panel, 3 statements with lucide `shield-check`, `badge-check`, `receipt` icons, each with the client's existing sentence.
6. **Photo + caption** — `<figure>` with `<img loading=lazy>` and a caption *below* the photo in ink-2 (no overlay), radius `--r-xl`.
7. **Comparison table** (Zopa) — HTML `<table>` with sticky first column at mobile widths, tabular numbers, zebra rows via `--canvas`.
8. **FAQ accordion** — native `<details>`, see §5.
9. **CTA band** — tint panel, h2 + sub + one primary button; used once per page, at the end.
10. **Footnotes / small print** — numbered list, 14 px ink-2, `id`s so superscripts can link.

### 2.7 Navigation

Desktop (≥900): 64 px white bar, 1 px `--line` bottom border, sticky; left: logo (32 px tall) + wordmark "Vochus Easy Save" Display 700 16 px; centre: Home, How It Works, Savings Plans, Interest, Benefits, Become an Agent — Body 500 15 px ink-2, ink on hover, 2 px ink-green underline (`::after`, scaleX transition) on the active page; "Support" becomes a real `<button aria-expanded aria-controls>` with a `chevron-down` SVG, menu is a white card (`--shadow-3`, radius `--r-lg`), opens on click, closes on Esc / outside click / focus-out; right: "Log In" `.btn-secondary.btn-sm`, "Apply as an Agent" `.btn-primary.btn-sm`.
Hierarchy fix for A4: on **Home only**, the header primary button is "Start Earning Interest" (existing copy) linking to the app register URL; "Apply as an Agent" is the secondary. On `agent.html` the order flips back. Elsewhere: Log In (secondary) + Start Earning Interest (primary).

Mobile (<900): 56 px bar: logo + wordmark, "Log In" as a 44 px text button (always visible — fixes A10), 44×44 hamburger (`aria-controls="menu" aria-expanded`). Menu: full-width sheet under the bar, `--surface`, items 52 px tall 17 px Display 600, divider, Support items, then two full-width buttons. Body scroll locked while open; Esc/overlay closes; focus trapped. Works without JS: the hamburger is a link to `#menu` and the menu uses `:target` to open (progressive enhancement; JS upgrades it).

### 2.8 Footer (white, not dark — the Wise pattern)

Surface background, 1 px `--line` top border. Row 1: logo + wordmark + the existing tagline (max 36ch). Row 2 (4 columns ≥900, 2 columns ≥600, accordion-free single column below with 48 px tap rows): Product · For Agents · Support · **Contact** (the address, mailto and tels move here from the brand column so they are tappable 44 px rows). "For Agents" keeps only real destinations: Become an Agent → `agent.html`, Agent Portal → *agent app URL (Q1)*, Agent FAQs → `faq.html#agents`. "Starter Pack" and "65% Commission" become anchors into `agent.html#starter-pack` / `#commission` (sections exist in the copy). Row 3: company line "Vochus Global Services Ltd · 286, Ikorodu Road, Anthony, Lagos, Nigeria" + "© 2026 Vochus Global Services Ltd. All rights reserved." + `www.vochuseasysave.com` as a link. Row 4 (Zopa legal pattern): the site-wide footnote block in 14 px ink-2 — currently only "per annum · online savers only" exists; the client supplies the rest (Q4).

### 2.9 Icons

Inline SVG, lucide set, 20 px default, `stroke-width:1.75`, `currentColor`, `aria-hidden="true"` with text alongside (never icon-only without `aria-label`). A single `<svg><symbol>` sprite inlined once per page (≈3 KB) and referenced with `<use href="#i-shield">` keeps HTML light. Icons needed: arrow-right, chevron-down, menu, x, shield-check, badge-check, receipt, wallet, calendar-check, users, smartphone, repeat, phone, mail, map-pin, message-circle, search, check, user, briefcase, lock.

---

## 3. Page-by-page layout spec

Copy in quotes is the client's existing text and is used unchanged; only its position changes. Patterns reference §2.6.

### 3.1 index.html

1. **Hero** (pattern 1 + 2). Left: label "Nigeria's Digital Savings Platform" (plain text, no chip or dot); h1 "Save more. Earn 12% every year." with "12%" tabular and a superscript footnote marker ¹; sub "Open a Vochus Easy Save account in minutes — save daily, weekly or monthly online and earn 12% annual interest on your balance. Secure, transparent, and built for Nigerians."; buttons: primary "Start Earning Interest" → register URL, secondary "See How It Works" → `how-it-works.html`. Directly beneath, footnote ¹ "per annum · online savers only" (Zopa). Right (stacks below on <900, never hidden): the **Savings Ledger** (§4.1) seeded with "Annual Interest Rate 12%" and the four rows "Per Month 1.00% · Per Quarter 3.00% · Per Half-Year 6.00% · Per Year 12.00%".
2. **Proof row** (replaces both the hero stat bar and the trust strip; one row, four items, tabular figures, 14 px labels, hairline separators, wraps to 2×2 at <600): "12% Annual Interest" · "₦0 Hidden Charges" · "100% Online" · "5 min To Register". The second set ("Annual Interest Paid / Weekly & Monthly Plans / BVN Identity Verified / Full Payout at Cycle End") moves into the Trust block below so no sentence is lost.
3. **Testimonial** — moves out of the hero into a quiet card beside the Community photos: the quote "Vochus helped me save ₦120,000 in one year and earn interest on top. I re-enrolled the same day I was paid out." and "Adaeze O. — Lagos" (subject to Q5).
4. **How it works preview** (pattern 3, the connected path §4.3) using the three step titles only — "Register Online", "Save Your Way", "Get Paid + Interest" — with "Learn more" to the page. Keeps the full copy on its own page.
5. **"Everything you need to start saving"** (pattern 4): h2, sub "Learn how Vochus works, pick a plan, and see exactly how your 12% interest grows.", four link cards with lucide icons (route, layers, percent, shield-check) and the existing titles/blurbs/"Learn more →"-style links (arrow as SVG).
6. **Trust block** (pattern 5): tint panel; three statements using existing sentences: "BVN Identity Verified", "Full Payout at Cycle End" and "Daily, Weekly & Monthly Plans" as headings with the Benefits-page sentences beneath ("Your identity is verified with BVN and a valid government ID…", "Every naira you save comes back to you at cycle end, plus your interest…", "Pick the plan that matches how you earn…").
7. **"Built for the way Nigerians save"** (pattern 6, editorial): h2, sub; three `<figure>`s in a 7/5 asymmetric grid, captions below the photos in the client's words: "Register with your agent — Open your account in person or online, with a local agent beside you." etc. Crops per §6.
8. **Agent band** (pattern 9 variant, surface card on canvas, photo right): h2 "Earn with Vochus. Become an Agent.", sub, the four perks as a check list (lucide `check` in tint circles), button "Apply as an Agent". No watermark.
9. **Footnotes** + footer.

Mobile order: 1 hero (ledger directly under the buttons, collapsed to its summary row with a "See the full breakdown" disclosure), 2 proof row, 4 steps, 5 cards as a list, 6 trust, 7 photos (single column, first photo 4:3, others 16:9), 3 testimonial, 8 agent, footer.

### 3.2 how-it-works.html

h1 "Three steps to your first payout"; sub "Getting started takes under five minutes…". The **connected path** (§4.3) at full size with the complete step copy. Below it, a two-column aside (pattern 10 card-quiet): "What you'll need" is not new copy — instead reuse the sentence "You'll need your phone number, a valid ID and your BVN." as a pulled quote with three lucide icons (smartphone, id-card, badge-check). Then a CTA band: "Start Earning Interest" + secondary "See plans". Footer.

### 3.3 plans.html

h1 "Save at your own pace", sub. Four plan cards in a 4-col grid (2-col <900, 1-col <600) — each: lucide icon (sun, calendar-days, calendar, users), "Daily Savings" / "Save every single day", the description, "Best for:" line, and the rate line "12% p.a. interest" rendered as a small tabular statement with footnote marker (Group keeps "Community payout"). The card footer becomes a real link: "Start saving daily" → register URL (Q1); "Join a group" → register URL. Beneath: a **comparison table** (pattern 7) built only from facts already in the copy — columns Daily / Weekly / Monthly / Group; rows "How often" (Save every single day / once every week / once every month / Everyone contributes the same amount each cycle), "Duration" (Flexible duration / 13, 26 or 52 weeks / 3, 6 or 12 months / rotating until every member has been paid out), "Best for" (existing), "Interest" (12% p.a. interest ×3 / Community payout). Then the sentence "You can run multiple plans at the same time — each tracks separately on your portal." as a card-quiet note. CTA band. Footer.

### 3.4 interest.html

Light page. h1 "Your savings work harder with Vochus" (no colour split); sub "Interest is calculated on your total savings at the end of your cycle, prorated for the months you saved, and added to your payout automatically." Then the **Rate statement**: "12%" Display at clamp(72px,12vw,128px) with "per annum · online savers only" beneath and footnote marker. Two-column body: left the **Savings Ledger** (§4.1) in its full interactive form, seeded with the four worked examples ("Daily — ₦500 × 30 days … ₦15,150 / +₦150 interest" etc.) as selectable presets; right a card with the table "Rate Breakdown by Period" (Per Week ≈ 0.23% … Per Full Year 12.00%, highlighted row in tint) and "How It's Applied" as an ordered list `<ol>` (numerals replace the 01/02/03 tiles). CTA "Start Earning 12% Today". Footer with footnotes. Mobile: rate statement, ledger, table (horizontal-scroll-free: two columns fit), list, CTA.

### 3.5 benefits.html

h1 "Built around how you save", sub. Nine benefits grouped by weight: the first three ("12% Annual Interest", "Safe & BVN Verified", "Full Payout — Zero Deductions") as large cards in a row (these are the trust claims), the remaining six as a 3×2 feature grid (list on mobile). Icons: percent, shield-check, banknote, smartphone, users, user-round, activity, target, repeat. Single accent colour throughout (no 6-hue tiles). CTA band. Footer.

### 3.6 agent.html

h1 "Apply as a Vochus Agent", sub "Help people in your community save and earn 65% of the commission your portfolio generates. Tell us a little about yourself and we will be in touch." Two columns: left, editorial photo (women in line, crop B2) + the four perks as `<section id="commission">`, `<section id="starter-pack">` headings using the perk sentences; right, the application form card — field labels properly associated, 16 px inputs, 48 px controls, `inputmode="tel"` kept, honest helper text (existing: "Submitting opens your email app with this application ready to send to info@vochuseasysave.com.") shown *above* the button, and a visible fallback link "info@vochuseasysave.com" (Q7 asks whether a real form endpoint exists). Below: a link row to the agent FAQ groups ("For agents: Getting started", "…Registration", "…Contributions & payouts", "…Group savings", "…Earning commission", "…Help & support") → `faq.html#agents`. Footer.

### 3.7 faq.html

h1 "Frequently Asked Questions", sub "Everything you need to know about saving with Vochus." Search input (16 px, 48 px tall, lucide search icon, clears with Esc). A sticky-on-desktop left rail of group links (For savers / For agents: Getting started / … / Help & support) as `h2`s with ids (`#savers`, `#agents`, `#agents-registration`…). Accordion per §6. Empty-state copy "No questions match your search. Contact us and we will help." with the link fixed to `contact.html`. Footer.

### 3.8 contact.html

h1 "Get in Touch", sub. Left: four contact rows as 56 px tappable list items with lucide icons (mail, phone, map-pin, user): "Email us", "Call or WhatsApp" (tel links; add `wa.me` once Q6 is answered), "Address", "Speak to your agent". Right: message form card (labels associated, 16 px, subject `<select>` kept). Photo A (registration queue) as a 16:9 figure above the rows on desktop, below on mobile. Footer.

### 3.9 privacy.html

h1 "Privacy Policy", sub, "Last updated: October 2026". Single column `--measure` width; the nine `h3`s become `h2`s with ids; a small "On this page" list at the top (links to the nine sections) on ≥900 as a sticky right rail. Footer.

### 3.10 404.html

Canvas page: h1 "404" in Display 800 ink-green at `--t-display`, "Sorry, we could not find that page.", primary button "Back to the home page", plus a quiet link row to Savings Plans, Interest, FAQs, Contact. Nav + footer like every other page; add the shared `<head>` block (favicon, description, theme-color).

### 3.11 login.html (chooser) and the four auth pages

Design only — integration later. `login.html` becomes a single centred card on canvas (no photo panel): logo 40 px, h1 "Log in", sub "Choose how you use Vochus. You will sign in on our secure portal.", two large option cards (64 px tall, lucide `user` / `briefcase` in tint tiles, title + one line): "Saver login — Access your savings and payouts" → *saver app URL* and "Agent login — Manage your portfolio and commission" → *agent app URL*; both are plain `<a>` with `rel="noopener"`. Under them the two existing links "Become an agent" / "Need help?" and the safety line "For your safety, never share your password or one-time codes with anyone, including Vochus staff or agents." Optional app-badge row (Zopa pattern) if the Flutter apps are in the stores (Q3).
`saver-login.html`, `agent-login.html` → thin pages with the same card showing only the relevant option plus a "Not you? Choose a different login" link, so old bookmarks keep working. `forgot-password.html` → same card: "Forgot password" + "We will never ask for your current password or any one-time code." + one button "Reset in the app" → *app reset URL*, and the existing fallback sentence "If nothing opened, email info@vochuseasysave.com." No form fields on any of these pages.
`portal.html` stays as a marketing page (§3.12).

### 3.12 portal.html

h1 "Your savings, in one place", sub. Hero right: the **product vignette** (§4.4) instead of the avatar row. Buttons "Log In to Portal" (→ `login.html`) and "Create an Account" (→ register URL). Six feature cards as a 3×2 grid (list on mobile) with lucide icons. "How to get started" and "Need help?" as a card-quiet two-column block. Footer.

---

## 4. Signature moments

Each is an idea, not decoration; each works at 360 px on a cheap Android phone and without JS.

### 4.1 The Savings Ledger (interactive "your money over time")
Sketch: a white card shaped like a statement. Header row: "Annual Interest Rate · 12%" with footnote marker. Controls (three segmented pills: Daily / Weekly / Monthly; an amount field with the ₦ prefix; a duration select whose options are only the durations the client publishes: 30 days / 13, 26, 52 weeks / 3, 6, 12 months). Body: a running table with dotted leaders (receipt style) — "Saved", "Interest applied (n%)", a hairline, "Payout" in Display 800 tabular. Rows use the published prorated rule (1 % per month of the cycle) and the four client examples are the presets, so by default the card simply *shows the client's own worked examples*; nothing new is claimed. Every figure is labelled "Example — per annum · online savers only".
Why it serves a Nigerian saver: the question is always "if I put ₦500 a day, what do I collect?" — answering it in naira, in the saver's own plan, is more persuasive than a percentage.
Degradation: without JS the card renders the four worked examples as four static rows (the HTML is server-rendered in the file); with JS the controls appear (`hidden` attribute removed) and rows update on `input`. No count-up animation; the changed row gets a 200 ms tint flash (opacity only), none under reduced-motion. At 360 px the controls stack, the table is two columns, numbers right-aligned and tabular so decimals line up. Numbers are computed with integer kobo to avoid float drift. **Blocked on Q2** (rule confirmation) — until then the ledger ships preset-only.

### 4.2 The receipt motif
The business already runs on printed thermal receipts ("every offline customer must get a printed receipt"). Plan cards, the rate table and the ledger share a receipt language: dotted leaders between label and value, tabular figures, a hairline "tear" line (a `border-top:1px dashed var(--line-strong)`) above totals. Pure CSS, no images. Serves trust: paper proof is what savers already rely on; the site speaks that language. Degrades perfectly — it is just typography.

### 4.3 How it works as one cycle
Sketch: a single SVG path (stroke `--line-strong`, 2 px) runs Register → Save → Get Paid, then a dashed return segment loops back to Register, labelled with the client's own words "Re-enrol Any Time". The three nodes are 40 px tint circles with Display numerals; the path is drawn once with `stroke-dashoffset` over 600 ms when it enters the viewport (transform/opacity-free, and skipped under reduced-motion — the path is simply there). Serves the saver: the loop is the Ajo rhythm they already know — save, collect, start again. At 360 px the path becomes a vertical rail on the left (CSS `border-left` on an `<ol>`; the SVG is `display:none`), with the loop shown as a small `repeat` icon on the last step.

### 4.4 Product vignettes in the app's own style
Two HTML/CSS components built with the shared tokens, no screenshots: (a) a **balance card** — "Live balance" label, "₦60,000" saved, "+₦3,600 interest" in ink-green, a thin progress bar in `--tint`/`--fill`, "Payout date" row; (b) a **payout row** — receipt icon, "Monthly — ₦10,000 × 6 months", right-aligned "₦63,600". All figures come from the client's published examples. Used on `portal.html` and as the Home ledger's "collapsed" face on mobile. Degrades: static markup; on a narrow phone the card is full-width with 20 px padding; nothing is clipped because every number is text.

### 4.5 The ₦ and the numbers
A deliberate numeral style instead of a generic big "12%": the figure is Display 800 with −0.04em tracking; the `%` is set at 0.6em and superscripted to the cap height; the ₦ is a separate `span` in Inter 500 at 0.8em, ink-2, with a 0.05em gap, so the amount reads as the number first and the currency second — the way people say it ("sixty thousand naira"). Tabular figures everywhere money appears so columns align. Verify at build time that the chosen Plus Jakarta Sans subset includes U+20A6; if not, the `.naira` span falls back to Inter, which does. Degrades to plain text; the style is CSS only.

### 4.6 Editorial photography
Three photos, cropped with intent (details §6): the registration queue cropped to the *hands and the form* (the act of registering), the women in line cropped to the central face looking at the camera (a saver, not a crowd), the celebration kept wide (community). Captions are the client's existing figcaption copy, placed below the image in ink-2 — never over a wash. Served responsively (`srcset` 480/960/1440, WebP + JPEG fallback), `loading="lazy"`, intrinsic `width`/`height` so nothing shifts. On 360 px the first photo is 4:3 and the other two 16:9 to keep the page short.

---

## 5. Component quality bar

For each component: states · spacing · type · motion · accessibility. All interactive targets ≥ 44 × 44 px; all focus rings 2 px `--focus` with 3 px offset, never removed.

**Nav** — States: rest, hover (ink), active page (underline), focus-visible, menu open (`aria-expanded=true`, chevron rotates 180°), scrolled (adds `--shadow-1`). Spacing: 64/56 px bar, 24 px between links, 12 px between buttons. Type: Body 500 15 px. Motion: underline `scaleX` 120 ms; mobile sheet fades/translates 8 px over 200 ms (opacity + transform only). A11y: `<nav aria-label="Main">`, skip link first in DOM, Esc closes, focus returns to the trigger, `inert` on page content while the sheet is open, works via `:target` without JS.

**Buttons** — States as §2.4 plus `aria-busy` loading state (spinner SVG, label stays). Spacing: 48 px tall, 22 px side padding, 8 px icon gap, 12 px between adjacent buttons (stack at <400 with full width). Type: Body 600 16 px, no letter-spacing, no uppercase. Motion: colour 120 ms, `translateY(1px)` on active. A11y: real `<a>`/`<button>`, visible text label always, `rel="noopener"` on external.

**Cards** — States: rest, hover (shadow-2 + border-strong + title ink-green, link cards only), focus-visible, selected (`.card-tint`). Spacing: 24 px padding (20 px <400), 12 px icon→title, 8 px title→body. Type: h3 20 px / body 16 px ink-2. Motion: shadow and border 200 ms; no transform. A11y: whole card is one `<a>` with the title as its name; icon `aria-hidden`.

**Rate display** — States: static; footnote marker is a link with hover underline. Spacing: figure → unit 4 px, unit → footnote 12 px. Type: §4.5. Motion: none. A11y: `aria-describedby` from the figure to the footnote; the superscript is `<a href="#fn1"><sup>1</sup></a>` with `aria-label="Footnote 1"`.

**Calculator / ledger** — States: preset selected (tint segment, `aria-pressed`), input focus, invalid amount (danger border + 14 px message with `aria-live="polite"`), updated row (tint flash). Spacing: controls 48 px tall, 12 px gaps, table rows 44 px. Type: labels 14 px ink-2, values 16 px tabular, total Display 800 28 px. Motion: 200 ms background tint on the changed row; none under reduced motion. A11y: `<fieldset><legend>` for the plan segment, `<label>`s, `inputmode="decimal"`, results in a `<table>` with `<th scope>`, live region announces the payout; fully usable with keyboard; no JS → presets as static rows.

**Steps / path** — States: none interactive; `.is-visible` draws the path once. Spacing: 40 px node, 16 px node→title, 8 px title→body, 32 px between steps on mobile. Type: numeral Display 800 18 px, title h3, body 16 px ink-2. Motion: `stroke-dashoffset` 600 ms `--ease`, skipped for reduced motion. A11y: an `<ol>` is the source of truth; SVG is `aria-hidden`.

**FAQ accordion** — States: closed, open (`[open]` border ink-green, `plus` icon rotates to `x`), hover (summary tint), focus-visible, search-filtered (hidden via `hidden` attribute, group hidden when empty). Spacing: summary 56 px min, 20 px padding, answer 0 20 20. Type: question h3 17 px Display 600, answer 16 px body. Motion: icon rotate 200 ms; content height not animated (native `<details>`). A11y: native semantics; icon outside the accessible name (`aria-hidden`), group headings are `<h2 id>`; search has a visible label, `type=search`, results count in a live region; `Esc` clears.

**Footer** — States: link hover underline, focus ring. Spacing: 64 px top padding, 40 px column gap, 12 px between links (48 px rows on mobile). Type: column heads Body 600 14 px ink, links 15 px ink-2, legal 14 px ink-2. Motion: none. A11y: `<footer>` with `<nav aria-label="Footer">`, address in `<address>`, tels and mailto as links.

**Login chooser** — States: option rest, hover (border ink-green, shadow-2), focus, active. Spacing: card 32 px padding, options 72 px tall, 12 px apart. Type: option title Display 600 17 px, line 14 px ink-2. Motion: 120 ms border/shadow. A11y: options are `<a>` with full text names; external targets state "Opens the Vochus app" visually (14 px ink-2) — this is UI chrome, not marketing copy.

**Forms (agent, contact)** — States: rest, focus (border ink-green 2 px inset ring), invalid (`aria-invalid`, danger border, message linked via `aria-describedby`), disabled, success (`role="status"` panel). Spacing: 48 px controls, 8 px label→control, 16 px between rows. Type: labels 14 px ink 500 sentence-case (no uppercase tracking), inputs 16 px. Motion: none. A11y: `<label for>`, `autocomplete`, `inputmode`, errors announced, submit never disabled before the user acts.

**Photos / figures** — `<figure><img srcset sizes width height loading=lazy decoding=async alt><figcaption>`; radius `--r-xl`; `object-fit: cover` with `object-position` per crop; captions ink-2 14 px with 12 px gap. No hover effects.

---

## 6. Asset plan

```
assets/
  css/style.css                 (one file, ≤ 30 KB minified, no inline <style> anywhere)
  js/main.js                    (≤ 8 KB, progressive: nav, FAQ search, ledger, path draw)
  fonts/
    PlusJakartaSans-700-latin.woff2, PlusJakartaSans-800-latin.woff2
    Inter-400-latin.woff2, Inter-500-latin.woff2, Inter-600-latin.woff2
  img/
    logo.svg                    (preferred — ask client, Q8) or logo.png 96×86 @2x, ≤ 10 KB, + logo.webp
    favicon.svg, favicon-32.png, apple-touch-icon.png (180)
    og-home.jpg                 (1200×630, ≤ 90 KB, canvas + logo + "Save more. Earn 12% every year.")
    photo-register-{480,960,1440}.{webp,jpg}   from f5eb5770.jpg (900×909)
    photo-savers-{480,960,1440}.{webp,jpg}     from 34459893.jpg (1280×853)
    photo-celebrate-{480,960,1440}.{webp,jpg}  from c6613c60.jpg (1280×853)
    avatar-adaeze.jpg           from 7a777f4d (104×104) — only if Q5 confirms consent; otherwise drop
```
Targets: WebP quality 72–78 (JPEG q78 fallback), 960 w ≤ 70 KB, 480 w ≤ 30 KB, 1440 w ≤ 140 KB (only served on ≥1200 px screens). Sprite of lucide `<symbol>`s inlined in each page (~3 KB).

Crops (object-position values for `object-fit: cover`):
- **photo-register** (900×909, portrait-ish): Home 7/5 grid tall tile and Contact 16:9 → `object-position: 50% 70%` so the signing hands, purse and form sit in frame; the man's head may crop — intentional, the act is the subject.
- **photo-savers** (1280×853): Home square tile and Agent 16:10 → `object-position: 48% 40%` centring the woman in the blue head-tie; at 4:3 on mobile the two flanking faces remain.
- **photo-celebrate** (1280×853): Home 16:9 wide tile → `object-position: 50% 45%`; at 360 px use the 480 w file, 16:9.
- The four portal avatars (`ac0dcf65, 343d8f40, d979b461, db66e0c2`) are dropped (unnamed faces add no information; replaced by the product vignette).
- Logo: the supplied PNG is a glossy 3-D mark; it is the client's logo and is kept, but it is the only gradient on the site. Request a flat SVG (Q8). Display at 32 px in nav, 40 px on the login card, 28 px in footer.

---

## 7. Implementation plan (build pass)

Order matters: structure first, then assets, then pages, then polish.

1. **Branch + baseline screenshots** of every page at 360/390/768/1440 into `/_qa/before/` (outside `public_html`), using the iframe-wrapper method for sub-500 px widths.
2. **Extract assets**: write the 9 images from the base64 to `assets/img/` (sources are already in the scratchpad), generate the responsive WebP/JPEG sets (`cwebp`/`sips`/ImageMagick — one-off, not a build step), favicon set, subset fonts (`pyftsubset` or download latin subsets), lucide sprite.
3. **Write `assets/css/style.css`** from §2 tokens → base → layout → components → page sections. Delete the old `style.css` at the root (keep path `assets/css/style.css`; update links). Remove *every* `<style id="vochus-images">` block and inline `style=""` attribute.
4. **Author `_partials/head.html`, `_partials/nav.html`, `_partials/footer.html`** and a 30-line Python script `_tools/assemble.py` that stamps them into each page between `<!-- nav -->` markers. Run it by hand; commit the output. (Still "no build step" for the host — the generated HTML is what gets uploaded. `_partials/` and `_tools/` stay out of `public_html`.)
5. **Write `assets/js/main.js`** (vanilla, ≤ 8 KB, `defer`): nav sheet + dropdown (Esc, focus trap, inert), FAQ filter, ledger, path draw via `IntersectionObserver`, all guarded by `matchMedia('(prefers-reduced-motion: reduce)')`. Delete `handleLogin`, `togglePass`, `handleForgot`, `VOCHUS_PORTAL`, the scroll-in opacity hacks and the smooth-scroll handler.
6. **Rebuild pages in this order**: index → interest (ledger) → how-it-works (path) → plans → benefits → portal → agent → faq → contact → privacy → login + the three auth stubs → 404. Each page: move the client's copy into the new sections verbatim (diff the text nodes before/after with a script to prove zero copy changes, modulo the dropped labels in §8.1).
7. **Head block** on every page: charset, viewport, title, description, canonical, OG/Twitter, `theme-color #FFFFFF`, favicon links, preload of the two display fonts (Home only), `<link rel="stylesheet" href="assets/css/style.css">`, `<script defer src="assets/js/main.js">`.
8. **Fix links**: footer agent links, `faq.html#contact` → `contact.html`, `rel="noopener"` on externals, section ids used by anchors (`#commission`, `#starter-pack`, `#agents`, `#community`).
9. **Robots/sitemap**: keep `robots.txt`; add `sitemap.xml` listing the 10 content pages (exclude auth stubs).
10. **Verification checklist** (all must pass before upload):
    - Screenshots at 360 / 390 / 768 / 1440 for all 15 pages, light theme, into `/_qa/after/`; eyeball against §3.
    - No horizontal scroll at 360 px (`document.documentElement.scrollWidth === 360`).
    - Page weight: Home ≤ 250 KB transferred on a 390 px viewport (HTML ≤ 25 KB, CSS ≤ 30 KB, JS ≤ 8 KB, fonts ≤ 95 KB cached after first page, images lazy); every other page ≤ 120 KB excluding fonts. Measure with Chrome DevTools "Network" at Slow 3G or `curl -w` sums.
    - Lighthouse (mobile) ≥ 95 Performance / 100 Accessibility / 100 Best Practices / 100 SEO on Home, Interest, FAQ.
    - Link check: a script walks every `href` in every file; zero 404s, zero `#` targets without an id, zero `javascript:`.
    - Copy check: text-node diff of old vs new per page shows only the removals listed in §8.1.
    - Keyboard pass: Tab through nav, menu, FAQ, ledger, forms on each page; Esc closes menus; focus always visible.
    - `prefers-reduced-motion: reduce` emulation: no animation anywhere; path and ledger still correct.
    - JS disabled: nav opens via `:target`, FAQ fully readable, ledger shows presets, login chooser links work.
    - Contrast: every text/background pair ≥ 4.5:1 (ink-3 never used for text < 24 px).
    - Tap targets: automated check that every `a`, `button`, `summary`, `input` has a bounding box ≥ 44 × 44 at 360 px.
    - Validate HTML (Nu validator) — zero errors.
11. **Upload** to cPanel `public_html` (replace in place; `.htaccess` adds `Cache-Control: max-age=31536000, immutable` for `assets/` and gzip/brotli for text).

What gets deleted: root `style.css` (replaced), all `<style id="vochus-images">` blocks, all inline `style=""`, the three base64 logo copies per page, base64 favicon, hero carousel markup (`.hero-slides`, `.hero-dots`, `.hero-noise`, `.hero-glow`, `.hrc-bg-num`, `.agent-wordmark`), the trust strip (merged), avatar row on portal, auth forms, dark-mode CSS, all `onclick=` attributes.

---

## 8. Copy notes for the client (no changes made — for his decision)

C1. **How interest is calculated is described two ways.** Interest page: "calculated on your total savings at the end of your cycle, prorated for the months you saved" (1 % per month). FAQ "How is the 12% annual interest calculated?": "Interest accrues daily on your saved balance at the equivalent daily rate… ₦50,000 saved for a full year earns ₦6,000". These are different methods and ₦50,000 × 12 % = ₦6,000 only if the full balance was there all year. The ledger (§4.1) needs one rule.
C2. **"₦0 Hidden Charges" / "Full Payout — Zero Deductions" vs "65% of the commission on every contribution".** Where does the commission come from if nothing is deducted from the saver? Worth one explanatory sentence (Zopa-style footnote) or the claims will be questioned.
C3. **"Earn 12% every year"** is unqualified in the h1 while the footnote says "online savers only" and the FAQ says "Early withdrawals may forfeit accrued interest." Zopa pairs every rate with its conditions in the same view; the redesign does this with footnote ¹, but the client should confirm the exact wording of the condition.
C4. **Group plan and interest**: Plans page shows "Community payout" (no interest); FAQ says group members get "the same 12% interest on individual contributions". One of them is wrong.
C5. **Testimonial "Adaeze O. — Lagos"** and the photo: confirm this is a real customer with consent, or remove. Same for "Most Vochus savers re-enrol immediately after their first payout" (Benefits) — an unverifiable claim.
C6. **Trust claims needing substantiation**: "regulated banking partners", "ring-fenced bank accounts", "bank-grade encryption", "registered Nigerian company" — the redesign's trust block would be far stronger with the company RC number and the named partner bank/licence (CBN/NDIC status). Currently no registration number appears anywhere.
C7. **"no app download needed"** (How it works, Portal) vs the plan to send log-ins "into the real app" and the existence of Flutter apps. Decide the message.
C8. **Contact**: "Call or WhatsApp" — which number is on WhatsApp? Also "we'll be in touch within one business day" is promised in the contact success message but not elsewhere.
C9. **Privacy**: cites "NDPR"; Nigeria's current law is the Nigeria Data Protection Act 2023 (NDPC). Legal review suggested. "Last updated: October 2026" is fine.
C10. Footer "Vochus Global Services Ltd / Nigeria" — add RC number and, if applicable, "Licensed by…". No Terms of Use or complaints page exists; both are standard on a savings site.
C11. Minor: "Get Paid + Interest" uses a plus sign in a heading; "Ajo & Esusu — digitised" vs "fully digitalised" (FAQ) — two spellings; "Starter pack" list differs slightly between Home ("T-shirt, cap, bag, power bank, Bluetooth printer & paper rolls") and FAQ ("branded T-shirt, face cap, cross bag…") — fine, but noted.

### 8.1 Decorative labels proposed for removal (structural, AI-invented)
- Code tiles: `01 PLN INT BEN` (Home explore cards), `DAY WK MO GRP` (Plans), `12% BVN 100% NGN GRP AGT TRK DSC NEW` (Benefits), `MSG TEL HQ AGT` (Contact), `SVR AGT` (Login), `BAL LOG PAY AGT PLN NEW` (Portal), `01 02 03` (Interest "How It's Applied" — becomes an ordered list) → replaced by lucide icons / list numerals.
- Pill chips: all `.sec-eyebrow` / `.section-label` chips. Their *text* is kept as a plain label where it adds information ("Nigeria's Digital Savings Platform", "Our community", "Why Vochus", "Savings Plans", "Become an Agent", "Customer Portal", "Contact", "Legal") and dropped where it only repeats the heading beneath it: "FAQ" (above "Frequently Asked Questions"), "How It Works" (above "Three steps…"), "12% Annual Interest" (above the 12 % figure), "Explore Vochus".
- Glyph arrows "→" and "▾" in button/link text → SVG icons (the words stay).
- Ghost "12%" behind the rate card, "AGENT" watermark, carousel dots, pulsing dot, hero grid texture.
- The `.hero-stat-bar` and `#trust` strip are merged into one proof row; no sentence is removed (second set moves to the trust block).
- Portal avatar row (four unnamed faces).

---

## 9. Open questions for the user

Q1. **App URLs.** What are the real destinations for: saver log-in, agent log-in, saver registration ("Create an Account" / "Start Earning Interest"), password reset? Currently `https://www.vochuseasysave.com/register`, `/login`, `/agent`. Is the marketing site staying on `www.vochuseasysave.com` with the app on a subdomain, or vice versa?
Q2. **Interest rule for the ledger** (see C1): monthly proration (1 %/month, as the Interest page) or daily accrual (as the FAQ)? Until confirmed the ledger ships preset-only.
Q3. **App badges**: are the Flutter apps live on Google Play / App Store? If yes, the Zopa-style badge row goes on Home hero, Portal and the login chooser; if not, the chooser links to the web app and C7 needs resolving.
Q4. **Legal footnotes**: does the client have the standard small print (rate conditions, early-withdrawal terms, company registration, regulator)? The footer reserves a block for it.
Q5. **Testimonial consent** (C5).
Q6. **WhatsApp number** (C8) so a `wa.me` link can be added.
Q7. **Form handling**: keep `mailto:` for Contact and Agent application, or is there an endpoint (cPanel PHP mailer, Formspree, or the app's API) we may post to? The spec assumes `mailto:` with honest helper text until told otherwise.
Q8. **Logo**: can the client supply a flat/SVG version of the mark? The glossy PNG is the one gradient left on the site.
Q9. **Fonts**: accept ~95 KB of self-hosted fonts (cached after first page) or prefer system fonts for the body and Plus Jakarta Sans only for headings (~50 KB)?
Q10. **Page budget sign-off**: Home ≤ 250 KB / inner ≤ 120 KB acceptable, or stricter?
Q11. Is "Community" (mobile-menu link to `index.html#community`) wanted as a nav item, or should it be dropped from the menu (the section stays)?

---

## 10. Decisions from the user (2026-10-29) — these override the open questions above

- **Q1 Domain:** the website is `https://vochuseasysave.com` (canonical, OG URLs, sitemap). App destinations are kept in ONE place (a single config object in `assets/js/main.js` AND the hrefs stamped by `_tools/assemble.py` from one constant) so they can be repointed in one edit. App paths: saver sign-up `/customer/enroll`, saver login `/customer/login`, saver reset `/customer/forgot-password`, agent login `/`, agent reset `/forgot-password`, APKs `/downloads/easysave-customer.apk` and `/downloads/easysave-agent.apk`. App base: `https://easysave.vochusglobalservices.co.uk` — CONFIRMED by the user (2026-10-29): the app is NOT moving to vochuseasysave.com.
- **Q2 Interest rule:** 1% per month of the cycle (the Interest page's prorated rule). The Savings Ledger may be fully interactive using this rule, still seeded with the client's four worked examples.
- **Q3 Apps:** no store listings. Android APKs only → no App Store / Google Play badges. Use a plain "Download the Android app (APK)" link/button pattern where the spec placed badges; never imply a store listing.
- **Q5 Testimonial:** NOT a real customer → remove the "Adaeze O. — Lagos" testimonial and its avatar entirely (a fabricated review must not ship). This is the one copy removal beyond §8.1.
- **Q8 Logo:** use the app's SVG logo: `/Users/mac/Developer/vochus-easysave-main/public/brand/logo-mark.svg` (full colour mark), `logo-mark-mono.svg`, `logo-icon.svg`. Copy into `assets/img/`. The mark's own gradients are the brand logo and are allowed; nothing else uses gradients.
- Q4, Q6, Q7, Q9–Q11 deferred: use the spec's defaults (reserved legal block, tel links only, mailto forms with honest helper text, self-hosted fonts within budget, budgets as stated, keep "Community" in the mobile menu).
