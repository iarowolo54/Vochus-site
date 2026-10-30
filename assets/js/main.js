/* Vochus Easy Save: progressive enhancement only. The page works without this file. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  root.classList.remove('no-js'); root.classList.add('js');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)');
  var narrow = matchMedia('(max-width: 1023px)'), stacked = matchMedia('(max-width: 899px)');
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };

  /* App destinations, stamped by _tools/assemble.py from its APP constant; do not edit here. */
  window.VOCHUS_APP = /* app-urls:start */{register:"https://easysave.vochusglobalservices.co.uk/customer/enroll",saver_login:"https://easysave.vochusglobalservices.co.uk/customer/login",saver_reset:"https://easysave.vochusglobalservices.co.uk/customer/forgot-password",agent_login:"https://easysave.vochusglobalservices.co.uk/",agent_reset:"https://easysave.vochusglobalservices.co.uk/forgot-password",apk_customer:"https://easysave.vochusglobalservices.co.uk/downloads/easysave-customer.apk",apk_agent:"https://easysave.vochusglobalservices.co.uk/downloads/easysave-agent.apk"}/* app-urls:end */;

  /* ---- Nav: scrolled shadow ---- */
  var nav = $('#nav');
  if (nav) {
    var onScroll = function () { nav.classList.toggle('is-scrolled', scrollY > 4); };
    addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }

  /* ---- Nav: mobile sheet (upgrades the :target fallback) ---- */
  var burger = $('#burger'), sheet = $('#menu');
  if (burger && sheet) {
    var inertables = function () { return $$('main, footer'); };
    var focusables = function () { return $$('a[href], button:not([disabled])', sheet).filter(function (el) { return el.offsetParent !== null; }); };
    var setOpen = function (open) {
      sheet.classList.toggle('is-open', open);
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Menu');
      d.body.classList.toggle('menu-open', open);
      inertables().forEach(function (el) { open ? el.setAttribute('inert', '') : el.removeAttribute('inert'); });
      if (open) { var f = focusables(); if (f[0]) f[0].focus(); } else { burger.focus(); }
    };
    var isOpen = function () { return sheet.classList.contains('is-open'); };
    burger.setAttribute('role', 'button');
    burger.addEventListener('click', function (e) { e.preventDefault(); setOpen(!isOpen()); });
    sheet.addEventListener('click', function (e) { if (e.target.closest('a[href]')) setOpen(false); });
    sheet.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var f = focusables(); if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && d.activeElement === first) { e.preventDefault(); burger.focus(); }
      else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); burger.focus(); }
    });
    burger.addEventListener('keydown', function (e) {
      if (e.key === 'Tab' && isOpen()) { var f = focusables(); if (f.length) { e.preventDefault(); (e.shiftKey ? f[f.length - 1] : f[0]).focus(); } }
    });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && isOpen()) setOpen(false); });
    narrow.addEventListener('change', function (q) { if (!q.matches && isOpen()) setOpen(false); });
    if (location.hash === '#menu') { history.replaceState(null, '', location.pathname); setOpen(true); }
  }

  /* ---- Savings Ledger (§4.1): 1% per month of the cycle, integer kobo ---- */
  var ledger = $('.ledger');
  if (ledger) {
    var det = $('details', ledger);
    if (det && stacked.matches) det.removeAttribute('open');   // mobile: collapsed summary, "See the full breakdown"
    var ctl = $('.ledger-controls', ledger);
    if (ctl) {
      var PLANS = {
        daily:   { label: 'Daily',   ex: 500,   opts: [[30, '30 days', 1]] },
        weekly:  { label: 'Weekly',  ex: 2000,  opts: [[13, '13 weeks', 3], [26, '26 weeks', 6], [52, '52 weeks', 12]] },
        monthly: { label: 'Monthly', ex: 10000, opts: [[3, '3 months', 3], [6, '6 months', 6], [12, '12 months', 12]] }
      };
      var plan = 'daily', dirty = false;
      var amt = $('#lg-amount', ledger), dur = $('#lg-duration', ledger), err = $('#lg-error', ledger);
      var cells = { plan: $('[data-k=plan]', ledger), saved: $('[data-k=saved]', ledger), rate: $('[data-k=rate]', ledger), interest: $('[data-k=interest]', ledger), payout: $('[data-k=payout]', ledger) };
      var N = '<span class="naira">₦</span>';
      var group = function (s) { return s.replace(/\B(?=(\d{3})+(?!\d))/g, ','); };
      var money = function (kobo) { var k = kobo % 100, n = (kobo - k) / 100; return N + group(String(n)) + (k ? '.' + (k < 10 ? '0' : '') + k : ''); };
      var plain = function (kobo) { return money(kobo).replace(/<[^>]+>/g, ''); };
      var fillDur = function () {
        dur.innerHTML = '';
        PLANS[plan].opts.forEach(function (o, i) { var el = d.createElement('option'); el.value = i; el.textContent = o[1]; dur.appendChild(el); });
        dur.selectedIndex = plan === 'monthly' ? 1 : 0;
      };
      var flash = function (el) { if (reduce.matches) return; el.parentNode.classList.remove('flash'); void el.offsetWidth; el.parentNode.classList.add('flash'); };
      var render = function () {
        var raw = amt.value.replace(/[,\s]/g, ''), val = Number(raw);
        var bad = !raw || !isFinite(val) || val <= 0 ? 'Enter an amount above ₦0.' : val > 1e8 ? 'Enter an amount below ₦100,000,000.' : '';
        amt.parentNode.parentNode.classList.toggle('is-invalid', !!bad);
        amt.setAttribute('aria-invalid', bad ? 'true' : 'false');
        err.textContent = bad;
        if (bad) return;
        var o = PLANS[plan].opts[dur.selectedIndex] || PLANS[plan].opts[0];
        var unit = Math.round(val * 100), n = o[0], months = o[2];
        var saved = unit * n, interest = Math.round(saved * months / 100), payout = saved + interest;
        cells.plan.textContent = PLANS[plan].label + ' · ' + plain(unit) + ' × ' + o[1];
        cells.saved.innerHTML = money(saved);
        cells.rate.textContent = months + '%';
        cells.interest.innerHTML = '+' + money(interest);
        cells.payout.innerHTML = money(payout);
        [cells.saved, cells.interest, cells.payout].forEach(flash);
      };
      $$('.seg-btn', ledger).forEach(function (b) {
        b.addEventListener('click', function () {
          $$('.seg-btn', ledger).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
          plan = b.value; fillDur();
          if (!dirty) amt.value = String(PLANS[plan].ex);
          render();
        });
      });
      amt.addEventListener('input', function () { dirty = true; render(); });
      dur.addEventListener('change', render);
      ctl.addEventListener('submit', function (e) { e.preventDefault(); render(); });
      /* Worked-example presets (interest.html): a preset is "pressed" while the controls still match it */
      var presets = $$('.ex', ledger);
      var syncPresets = function () {
        var v = Number(amt.value.replace(/[,\s]/g, ''));
        presets.forEach(function (b) {
          b.setAttribute('aria-pressed', String(b.dataset.plan === plan && Number(b.dataset.amount) === v && Number(b.dataset.dur) === dur.selectedIndex));
        });
      };
      presets.forEach(function (b) {
        b.addEventListener('click', function () {
          plan = b.dataset.plan;
          $$('.seg-btn', ledger).forEach(function (x) { x.setAttribute('aria-pressed', String(x.value === plan)); });
          fillDur(); dur.selectedIndex = Number(b.dataset.dur); amt.value = b.dataset.amount; dirty = false;
          render(); syncPresets();
        });
      });
      if (presets.length) { ['input', 'change', 'click'].forEach(function (ev) { ctl.addEventListener(ev, syncPresets); }); }
      fillDur(); ctl.hidden = false;
    }
  }

  /* ---- How it works: if the step cards start below the fold, reveal their vignette rows once they scroll in ---- */
  var steps = $('.steps');
  if (steps && 'IntersectionObserver' in window && !reduce.matches && steps.getBoundingClientRect().top > innerHeight) {
    steps.classList.add('will-reveal');
    var reveal = function () { steps.classList.add('is-visible'); so.disconnect(); };
    var so = new IntersectionObserver(function (es) {
      if (es.some(function (e) { return e.isIntersecting; })) reveal();
    }, { threshold: 0.1 });
    so.observe(steps);
    setTimeout(reveal, 4000);   /* never leave content hidden if the observer does not fire */
  }


  /* ---- Forms (agent application, contact): the form posts to send.php and works without JS (303 redirects).
         With JS: client-side validation in the page's error styling, fetch with a loading state, success panel in place,
         and an inline alert with a mailto fallback when the request fails. The entered data is kept on failure. ---- */
  $$('form[action="send.php"]').forEach(function (form) {
    var tInput = $('input[name="t"]', form); if (tInput) tInput.value = String(Date.now());
    var btn = $('button[type="submit"]', form), alertBox = $('.form-alert', form), done = $('.form-done', form.parentNode);
    if (/[?&]error=1/.test(location.search) && alertBox) alertBox.classList.add('is-on');
    var fields = $$('input, select, textarea', form).filter(function (f) { return f.name && f.type !== 'hidden' && !f.closest('.hp'); });
    var setErr = function (f, msg) {
      var fld = f.closest('.field'), err = fld && $('.err', fld);
      f.setAttribute('aria-invalid', msg ? 'true' : 'false');
      if (err) { err.textContent = msg; if (msg) f.setAttribute('aria-describedby', err.id); else f.removeAttribute('aria-describedby'); }
      if (fld) fld.classList.toggle('is-invalid', !!msg);
    };
    var validate = function () {
      var first = null;
      fields.forEach(function (f) {
        var v = f.value.trim(), msg = '';
        if (f.required && !v) msg = 'Please fill in this field.';
        else if (f.type === 'email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) msg = 'Enter a valid email address.';
        else if (f.pattern && v && !(new RegExp('^(?:' + f.pattern + ')$')).test(v)) msg = 'Enter a valid phone number.';
        setErr(f, msg); if (msg && !first) first = f;
      });
      return first;
    };
    fields.forEach(function (f) { f.addEventListener('input', function () { if (f.getAttribute('aria-invalid') === 'true') setErr(f, ''); }); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (alertBox) alertBox.classList.remove('is-on');
      var bad = validate(); if (bad) { bad.focus(); return; }
      var label = btn.innerHTML;
      btn.disabled = true; btn.setAttribute('aria-busy', 'true'); btn.innerHTML = '<span class="spin" aria-hidden="true"></span>Sending…';
      var finish = function () { btn.disabled = false; btn.removeAttribute('aria-busy'); btn.innerHTML = label; };
      fetch(form.getAttribute('action'), { method: 'POST', headers: { 'Accept': 'application/json' }, body: new URLSearchParams(new FormData(form)) })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok && j && j.ok, j: j }; }); })
        .then(function (res) {
          finish();
          if (res.ok) { form.hidden = true; if (done) { done.hidden = false; done.focus(); } return; }
          var errs = res.j && res.j.errors || {}, first = null;
          fields.forEach(function (f) { if (errs[f.name]) { setErr(f, errs[f.name]); if (!first) first = f; } });
          if (alertBox) alertBox.classList.add('is-on');
          if (first) first.focus(); else if (alertBox) alertBox.scrollIntoView({ block: 'nearest' });
        })
        .catch(function () { finish(); if (alertBox) alertBox.classList.add('is-on'); });
    });
    var again = done && $('.again', done);
    if (again) again.addEventListener('click', function () {
      form.reset(); fields.forEach(function (f) { setErr(f, ''); }); if (tInput) tInput.value = String(Date.now());
      done.hidden = true; form.hidden = false; if (fields[0]) fields[0].focus();
    });
  });

  /* ---- Sticky sub-nav: mark the link whose section is in view (plain anchors without JS) ---- */
  var subnav = $('.subnav');
  if (subnav && 'IntersectionObserver' in window) {
    var links = $$('a[href^="#"]', subnav), targets = links.map(function (a) { return $(a.getAttribute('href')); }).filter(Boolean);
    var setActive = function (id) {
      links.forEach(function (a) {
        var on = a.getAttribute('href') === '#' + id; a.classList.toggle('is-active', on);
        if (on) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
        if (on && a.scrollIntoView && reduce.matches === false) { var ul = a.closest('ul'); if (ul && ul.scrollWidth > ul.clientWidth) ul.scrollTo({ left: a.offsetLeft - 12, behavior: 'smooth' }); }
      });
    };
    var top = (nav ? nav.offsetHeight : 0) + subnav.offsetHeight + 24, current = null;
    var pick = function () {
      var best = null;
      targets.forEach(function (t) { if (t.getBoundingClientRect().top - top <= 1) best = t; });
      if (!best) best = targets[0];
      if (best && best.id !== current) { current = best.id; setActive(current); }
    };
    addEventListener('scroll', pick, { passive: true }); addEventListener('resize', pick); pick();
  }

  /* ---- Motion: scroll reveals (only for content below the first viewport) and the proof count-up.
         Nothing here hides content unless this code runs, and it does nothing under reduced motion. ---- */
  if (!reduce.matches && 'IntersectionObserver' in window) {
    root.classList.add('js-motion');
    var rvSel = '.section-head, .ftext, .stage, main .card:not(.hero-card):not(.auth-card), .trow li, .proof li, .app-panel, .about-zw, .cta-strip, .editorial figure, .endorse, .trust, .need, .card-quiet';
    var rvs = $$(rvSel).filter(function (el) { return !el.closest('.hero-home, .hero-panel, .auth') && el.getBoundingClientRect().top > innerHeight; });
    rvs.forEach(function (el) {
      var i = 0, p = el.previousElementSibling;
      while (p) { if (p.classList.contains('rv')) i++; p = p.previousElementSibling; }
      el.style.setProperty('--i', String(Math.min(i, 5))); el.classList.add('rv');
    });
    var rio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('rv-in'); rio.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    rvs.forEach(function (el) { rio.observe(el); });
    /* once revealed, drop the reveal classes so hover transitions run at their own speed */
    d.addEventListener('transitionend', function (e) { var t = e.target; if (e.propertyName === 'transform' && t.classList && t.classList.contains('rv-in') && !t.closest('.path')) { t.classList.remove('rv', 'rv-in'); } });
    setTimeout(function () { rvs.forEach(function (el) { el.classList.add('rv-in'); }); }, 6000);   /* never leave content hidden */
    /* proof numerals count up once, in tabular figures; the real text is restored exactly at the end */
    var vals = $$('.proof .v');
    if (vals.length) {
      var pio = new IntersectionObserver(function (es) {
        if (!es.some(function (e) { return e.isIntersecting; })) return;
        pio.disconnect();
        vals.forEach(function (v) {
          var node = null; v.childNodes.forEach(function (n) { if (n.nodeType === 3 && /\d/.test(n.textContent) && !node) node = n; });
          if (!node) return;
          var txt = node.textContent, m = txt.match(/\d+/), target = Number(m[0]), t0 = null;
          v.setAttribute('aria-label', v.textContent.trim());
          var step = function (ts) {
            if (t0 === null) t0 = ts;
            var k = Math.min(1, (ts - t0) / 900); k = 1 - Math.pow(1 - k, 3);
            node.textContent = txt.replace(m[0], String(Math.round(target * k)));
            if (k < 1) requestAnimationFrame(step); else { node.textContent = txt; v.removeAttribute('aria-label'); }
          };
          requestAnimationFrame(step);
        });
      }, { threshold: 0.4 });
      pio.observe(vals[0].closest('.proof') || vals[0]);
    }
  }

  /* ---- FAQ filter (used on faq.html) ---- */
  var q = $('#faq-q');
  if (q) {
    var items = $$('.faq'), groups = $$('.faq-group'), out = $('#faq-results');
    var run = function () {
      var s = q.value.trim().toLowerCase(), n = 0;
      items.forEach(function (it) { var hit = !s || it.textContent.toLowerCase().indexOf(s) > -1; it.hidden = !hit; if (hit) n++; });
      groups.forEach(function (g) { g.hidden = !$$('.faq:not([hidden])', g).length; });
      if (out) out.textContent = s ? (n ? n + ' question' + (n === 1 ? '' : 's') + ' match' : 'No questions match your search.') : '';
      var empty = $('#faq-empty'); if (empty) empty.hidden = !(s && !n);
    };
    if (q.form) q.form.addEventListener('submit', function (e) { e.preventDefault(); });
    q.addEventListener('input', run);
    q.addEventListener('keydown', function (e) { if (e.key === 'Escape') { q.value = ''; run(); } });
  }
})();
