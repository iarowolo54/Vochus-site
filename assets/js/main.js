/* Vochus Easy Save — progressive enhancement only. The page works without this file. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  root.classList.remove('no-js'); root.classList.add('js');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)');
  var narrow = matchMedia('(max-width: 1023px)'), stacked = matchMedia('(max-width: 899px)');
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };

  /* App destinations — stamped by _tools/assemble.py from its APP constant; do not edit here. */
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

  /* ---- Nav: Support dropdown ---- */
  var sbtn = $('#support-btn'), smenu = $('#support-menu');
  if (sbtn && smenu) {
    var wrap = sbtn.parentNode;
    var show = function (on) { smenu.hidden = !on; sbtn.setAttribute('aria-expanded', String(on)); };
    sbtn.addEventListener('click', function () { show(smenu.hidden); if (!smenu.hidden) { var a = $('a', smenu); if (a) a.focus(); } });
    d.addEventListener('click', function (e) { if (!wrap.contains(e.target)) show(false); });
    wrap.addEventListener('focusout', function (e) { if (!wrap.contains(e.relatedTarget)) show(false); });
    wrap.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !smenu.hidden) { show(false); sbtn.focus(); } });
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
        cells.plan.textContent = PLANS[plan].label + ' — ' + plain(unit) + ' × ' + o[1];
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
    q.addEventListener('input', run);
    q.addEventListener('keydown', function (e) { if (e.key === 'Escape') { q.value = ''; run(); } });
  }
})();
