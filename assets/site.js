// N6C site: header, menu, language memory, floating WhatsApp, drawing/model slider, contact form (WhatsApp or e-mail).
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // language buttons remember the choice (overrides browser detection from then on)
  document.querySelectorAll('[data-setlang]').forEach(function (a) {
    a.addEventListener('click', function () { try { localStorage.setItem('n6c-lang', a.getAttribute('data-setlang')); } catch (_) {} if (location.hash && a.getAttribute('href') !== '#') a.href = a.getAttribute('href').split('#')[0] + location.hash; });
  });

  // header turns solid once the page moves
  var top = document.querySelector('[data-top]');
  function onScroll() { if (top) top.classList.toggle('scrolled', window.scrollY > 24); }
  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });

  // mobile menu
  var mb = document.querySelector('[data-menu]'), mnav = document.getElementById('mnav');
  function closeMenu(focus) { mb.setAttribute('aria-expanded', 'false'); mnav.hidden = true; top.classList.remove('menu-open'); if (focus) mb.focus(); }
  if (mb && mnav) {
    mb.addEventListener('click', function () {
      var open = mb.getAttribute('aria-expanded') === 'true';
      if (open) closeMenu(false); else { mb.setAttribute('aria-expanded', 'true'); mnav.hidden = false; top.classList.add('menu-open'); }
    });
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && mb.getAttribute('aria-expanded') === 'true') closeMenu(true); });
    mnav.addEventListener('click', function (ev) { if (ev.target.closest('a')) closeMenu(false); });
  }

  // floating WhatsApp: after the hero (or the page head), hidden at the closing CTA, contact form and footer
  var fl = document.querySelector('[data-wafloat]');
  var start = document.querySelector('[data-hero]') || document.querySelector('.page-h');
  var ends = [document.querySelector('.cta-band'), document.querySelector('.contact-g'), document.querySelector('.foot')].filter(Boolean);
  if (fl) {
    var upd = function () {
      var past = !start || start.getBoundingClientRect().bottom < 0;
      var atEnd = ends.some(function (el) { return el.getBoundingClientRect().top < innerHeight * 0.9; });
      fl.classList.toggle('show', past && !atEnd);
    };
    upd(); window.addEventListener('scroll', upd, { passive: true }); window.addEventListener('resize', upd);
  }

  // reveal once
  var rv = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, { threshold: 0.15 });
    rv.forEach(function (el) { if (el.getBoundingClientRect().top < innerHeight) el.classList.add('in'); else io.observe(el); });
  } else rv.forEach(function (el) { el.classList.add('in'); });

  // drawing / model comparison: the range input drives --p; the first time it is seen it sweeps once
  document.querySelectorAll('[data-cmp]').forEach(function (cmp) {
    var input = cmp.querySelector('input');
    function set(v) { cmp.style.setProperty('--p', v + '%'); }
    input.addEventListener('input', function () { set(input.value); cmp.dataset.touched = '1'; });
    set(input.value);
    if (reduce || !('IntersectionObserver' in window)) return;
    var so = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      so.disconnect();
      if (cmp.dataset.touched) return;
      var t0 = null, from = 92, to = 50, dur = 1600;
      (function step(ts) {
        if (cmp.dataset.touched) return;
        if (!t0) t0 = ts;
        var k = Math.min(1, (ts - t0) / dur), e = 1 - Math.pow(1 - k, 3), v = from + (to - from) * e;
        set(v.toFixed(2)); input.value = Math.round(v);
        if (k < 1) requestAnimationFrame(step);
      })(performance.now());
    }, { threshold: 0.5 });
    so.observe(cmp);
  });

  // contact form: builds the message and opens WhatsApp; nothing is stored or sent elsewhere
  document.querySelectorAll('[data-waform]').forEach(function (f) {
    function check(el) {
      var bad = !el.value.trim(), msg = document.getElementById(el.getAttribute('aria-describedby'));
      el.setAttribute('aria-invalid', String(bad)); if (msg) msg.hidden = !bad; return !bad;
    }
    [f.name, f.msg].forEach(function (el) { el.addEventListener('input', function () { if (el.getAttribute('aria-invalid') === 'true') check(el); }); });
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var okN = check(f.name), okM = check(f.msg);
      if (!okN || !okM) { (okN ? f.msg : f.name).focus(); return; }
      var name = f.name.value.trim(), msg = f.msg.value.trim(), co = f.company.value.trim(), topic = f.topic.value;
      var text = f.dataset.intro + ' ' + name + (co ? f.dataset.from + ' ' + co : '') + '.\n' + f.dataset.about + ': ' + topic + '\n\n' + msg;
      var viaMail = ev.submitter ? ev.submitter.value === 'mail' : false;
      if (viaMail) location.href = 'mailto:' + f.dataset.email + '?subject=' + encodeURIComponent(f.dataset.subject + ': ' + topic) + '&body=' + encodeURIComponent(text);
      else window.open('https://wa.me/' + f.dataset.phone + '?text=' + encodeURIComponent(text), '_blank', 'noopener');
    });
  });
})();
