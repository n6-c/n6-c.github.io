// n6c.org/midia: share a piece (Web Share API with the file; download when the browser can't), copy the suggested text, remember the format.
(function () {
  var toastEl = document.querySelector('[data-toast]'), tId;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg; toastEl.classList.add('on');
    clearTimeout(tId); tId = setTimeout(function () { toastEl.classList.remove('on'); }, 3200);
  }

  // format switch: remembered between visits
  var radios = document.querySelectorAll('.fmt input');
  try {
    var saved = localStorage.getItem('n6c-midia-fmt');
    radios.forEach(function (r) { if (r.value === saved) r.checked = true; });
  } catch (_) {}
  radios.forEach(function (r) { r.addEventListener('change', function () { try { localStorage.setItem('n6c-midia-fmt', r.value); } catch (_) {} }); });

  // can this browser share image files? (phones: yes; most desktops: no, so the button downloads)
  var canFiles = false;
  try { canFiles = !!(navigator.canShare && navigator.canShare({ files: [new File([''], 'x.jpg', { type: 'image/jpeg' })] })); } catch (_) {}

  // Safari wants share() close to the tap, so the file is fetched before: when the piece comes into view
  var cache = {};
  function load(url, name) {
    if (!cache[url]) cache[url] = fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.blob(); })
      .then(function (b) { var f = new File([b], name, { type: 'image/jpeg' }); cache[url].file = f; return f; });
    return cache[url];
  }
  var buttons = document.querySelectorAll('[data-share]');
  if (canFiles && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { load(e.target.dataset.share, e.target.dataset.name).catch(function () {}); io.unobserve(e.target); } });
    }, { rootMargin: '300px 0px' });
    buttons.forEach(function (b) { io.observe(b); });
  }

  function download(url, name) {
    var a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
  }
  function caption(btn) { var s = btn.closest('[data-caption]'); return s ? s.dataset.caption : ''; }

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var url = btn.dataset.share, name = btn.dataset.name;
      if (!canFiles) { download(url, name); toast('Peça baixada. No celular, este botão abre direto o WhatsApp e o Instagram.'); return; }
      var go = function (file) {
        return navigator.share({ files: [file], text: caption(btn) }).catch(function (e) {
          if (e && e.name === 'AbortError') return;          // closed the share sheet
          download(url, name); toast('Não deu para abrir o compartilhamento; a peça foi baixada.');
        });
      };
      var c = cache[url];
      if (c && c.file) { go(c.file); return; }
      btn.setAttribute('aria-busy', 'true');
      load(url, name).then(go, function () { download(url, name); toast('A peça foi baixada.'); })
        .then(function () { btn.removeAttribute('aria-busy'); });
    });
  });

  // copy the suggested text
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var t = caption(btn);
      var ok = function () { toast('Texto copiado. Cole junto com a peça.'); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(ok, fallback); else fallback();
      function fallback() {
        var ta = document.createElement('textarea'); ta.value = t; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); ok(); } catch (_) { toast('Não deu para copiar; selecione o texto e copie.'); }
        ta.remove();
      }
    });
  });
})();
