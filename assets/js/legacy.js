/* Vochus Easy Save: site scripts (no dependencies) */

// Sticky nav shadow
(function () {
  var nav = document.getElementById('nav');
  if (!nav) return;
  window.addEventListener('scroll', function () {
    nav.classList.toggle('scrolled', window.scrollY > 16);
  }, { passive: true });
})();

// Mobile menu
var hamburger = document.getElementById('hamburger');
var navMobile = document.getElementById('navMobile');
function closeMobile() {
  if (!navMobile || !hamburger) return;
  navMobile.classList.remove('open');
  hamburger.setAttribute('aria-expanded', 'false');
  hamburger.querySelectorAll('span').forEach(function (s) { s.style.transform = ''; s.style.opacity = ''; });
}
if (hamburger && navMobile) {
  hamburger.addEventListener('click', function () {
    var open = navMobile.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
    var spans = hamburger.querySelectorAll('span');
    if (open) {
      spans[0].style.transform = 'translateY(7px) rotate(45deg)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
    } else {
      spans.forEach(function (s) { s.style.transform = ''; s.style.opacity = ''; });
    }
  });
}

// Support dropdown: also opens on click/tap
(function () {
  var sup = document.querySelector('.nav-support');
  var toggle = document.querySelector('.nav-support-toggle');
  if (!sup || !toggle) return;
  toggle.addEventListener('click', function (e) { e.stopPropagation(); sup.classList.toggle('open'); });
  document.addEventListener('click', function () { sup.classList.remove('open'); });
})();

// Smooth scroll for same-page anchors
document.querySelectorAll('a[href^="#"]').forEach(function (a) {
  a.addEventListener('click', function (e) {
    var href = a.getAttribute('href');
    if (href.length < 2) return;
    var el = document.getElementById(href.slice(1));
    if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});

// Forms: open the visitor's email app with the details filled in
function sendMail(subject, lines) {
  location.href = 'mailto:info@vochuseasysave.com?subject=' + encodeURIComponent(subject) +
    '&body=' + encodeURIComponent(lines.join('\n'));
}
function handleAgent(e) {
  e.preventDefault();
  var v = function (id) { return document.getElementById(id).value.trim(); };
  sendMail('Agent application: ' + v('ag-first') + ' ' + v('ag-last'), [
    'First name: ' + v('ag-first'), 'Last name: ' + v('ag-last'), 'Phone: ' + v('ag-phone'), '', v('ag-msg')
  ]);
  document.getElementById('agent-ok').hidden = false;
}
function handleContact(e) {
  e.preventDefault();
  var f0 = e.target.querySelectorAll('input,select,textarea');
  sendMail('Website message: ' + (f0[2].value || 'General'), [
    'Name: ' + f0[0].value, 'Email: ' + f0[1].value, '', f0[3].value
  ]);
  var ok = document.getElementById('cf-success');
  ok.textContent = 'Your email app should have opened with your message. Please press send. If nothing opened, email info@vochuseasysave.com.';
  ok.hidden = false;
}

// Scroll-in animations
document.querySelectorAll('.int-ex').forEach(function (el, i) {
  el.style.transform = 'translateX(-16px)';
  el.style.opacity = '0';
  el.style.transition = 'transform .4s ease, opacity .4s ease';
  var o = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) {
        setTimeout(function () { el.style.transform = 'translateX(0)'; el.style.opacity = '1'; }, i * 80);
        o.disconnect();
      }
    });
  }, { threshold: 0.2 });
  o.observe(el);
});
document.querySelectorAll('.step-item').forEach(function (el, i) {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity .5s ease ' + (i * 120) + 'ms, transform .5s ease ' + (i * 120) + 'ms';
  var o2 = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { el.style.opacity = '1'; el.style.transform = 'none'; o2.disconnect(); }
    });
  }, { threshold: 0.3 });
  o2.observe(el);
});


// ── Login pages ──
// Where the Saver / Agent login forms send their details. Change these two
// addresses if your portal lives somewhere else.
window.VOCHUS_PORTAL = {
  saver: 'https://www.vochuseasysave.com/login',
  agent: 'https://www.vochuseasysave.com/agent'
};
document.querySelectorAll('form[data-portal]').forEach(function (f) {
  f.setAttribute('action', window.VOCHUS_PORTAL[f.getAttribute('data-portal')] || '');
});
function togglePass(btn) {
  var i = document.getElementById(btn.getAttribute('data-for'));
  var show = i.type === 'password';
  i.type = show ? 'text' : 'password';
  btn.textContent = show ? 'Hide' : 'Show';
  btn.setAttribute('aria-pressed', show ? 'true' : 'false');
}
function handleLogin(e) {
  var f = e.target, id = f.querySelector('[name=username]'), pw = f.querySelector('[name=password]');
  var err = f.querySelector('.lf-err');
  var msg = '';
  if (!id.value.trim()) msg = 'Enter your email address or phone number.';
  else if (!pw.value) msg = 'Enter your password.';
  if (msg) { e.preventDefault(); err.textContent = msg; err.hidden = false; (id.value.trim() ? pw : id).focus(); return; }
  err.hidden = true; // valid: the browser now submits the form to the portal
}
function handleForgot(e) {
  e.preventDefault();
  var f = e.target;
  var type = f.querySelector('[name=acct]').value, id = f.querySelector('[name=ident]').value.trim();
  var note = f.querySelector('[name=note]').value.trim();
  sendMail('Password reset request (' + type + ')', [
    'Account type: ' + type, 'Email or phone on the account: ' + id, '', note,
    '', '(I have not included my password in this message.)'
  ]);
  var ok = document.getElementById('forgot-ok');
  ok.textContent = 'Your email app should have opened with your reset request. Please press send. Our team will verify your details and reply with reset instructions. If nothing opened, email info@vochuseasysave.com.';
  ok.hidden = false;
}

/* FAQ search */
function filterFaq(v){
  var q=(v||'').trim().toLowerCase(),list=document.querySelector('#pg-faq .faq-list')||document.querySelector('.faq-list');
  if(!list)return;
  var any=false,group=null,gAny=false,els=list.children;
  function endGroup(){if(group)group.style.display=(!q||gAny)?'':'none'}
  for(var i=0;i<els.length;i++){
    var e=els[i];
    if(e.classList.contains('faq-group')){endGroup();group=e;gAny=false;continue}
    if(e.tagName==='DETAILS'){
      var m=!q||e.textContent.toLowerCase().indexOf(q)>-1;
      e.style.display=m?'':'none';
      if(m){gAny=true;any=true}
    }
  }
  endGroup();
  var em=document.getElementById('faq-empty');if(em)em.hidden=!q||any;
}
