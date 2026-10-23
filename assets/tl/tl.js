/* N6C construction timelapse, used as the home hero: scroll-scrubbed image sequence on a canvas.
   Track phases: intro (the headline scrolls away while the first sheet grows from beside it to full screen) -> four drawing sheets -> the site-plan linework lifts off the sheet and lands on the top-down render
   -> 162 rendered frames, paced per construction stage. */
(() => {
  const root = document.querySelector('.tl');
  if (!root) return;
  const base = (document.currentScript && document.currentScript.src) ? new URL('.', document.currentScript.src).href : '';
  const lang = (document.documentElement.lang || 'pt').toLowerCase().startsWith('en') ? 'en' : 'pt';
  const $ = (s) => root.querySelector(s);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const P_SHEETS = 0.20, P_REG = 0.30;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const ease = (t) => t * t * (3 - 2 * t);
  const pad2 = (n) => String(n).padStart(2, '0');

  fetch(base + 'data.json').then((r) => r.json()).then(init).catch(() => root.classList.add('is-static'));

  function init(D) {
    const L = (o, k) => (k ? o[k + (lang === 'en' ? '_en' : '_pt')] : o[lang]);
    const facts = D.facts[lang];
    root.querySelectorAll('[data-pt]').forEach((el) => { el.textContent = el.dataset[lang].replace(/\{(\w+)\}/g, (m, k) => facts[k] ?? m); });
    root.querySelectorAll('[data-label-pt]').forEach((el) => el.setAttribute('aria-label', el.dataset[lang === 'en' ? 'labelEn' : 'labelPt']));
    $('.tl-sr').innerHTML = D.stages.map((s) => `<li>${s[lang]}: ${L(s, 'sub')}</li>`).join('');
    if (reduce.matches) { root.classList.add('is-static'); if (intro) intro.apply(1); return; }
    reduce.addEventListener?.('change', (e) => root.classList.toggle('is-static', e.matches));

    const track = $('[data-tl-track]'), view = $('.tl-view'), canvas = $('.tl-canvas'), ctx = canvas.getContext('2d', { alpha: false });
    const sheetsBox = $('.tl-sheets'), ovInk = $('.tl-ov-ink'), ovWhite = $('.tl-ov-white');
    const cap = $('.tl-cap'), stepN = $('.tl-step-n'), stepOf = $('.tl-step-of'), title = $('.tl-title'), sub = $('.tl-sub');
    const bar = $('.tl-bar'), fill = $('.tl-bar-fill'), ticks = $('.tl-ticks'), loading = $('.tl-loading');
    const N = D.n, total = D.stages.length;
    const ofTxt = lang === 'en' ? ` of ${pad2(total)}` : ` de ${pad2(total)}`;

      const sheetsIn = $('[data-tl-sheets]') || sheetsBox, first = sheetsIn.querySelector('.tl-sheet.is-first');
    const intro = window.__tlIntro;
    const sheets = D.sheets.map((s, i) => {
      if (i === 0 && first) return first;
      const im = new Image(); im.className = 'tl-sheet'; im.alt = ''; im.decoding = 'async'; im.src = base + s.src;
      sheetsIn.appendChild(im); return im;
    });

    // ---------------- frames: compressed blobs for all, decoded bitmaps only around the playhead ----------------
    let set = pickSet(), blobs = [], bms = new Map(), pending = new Set(), settled = 0, cur = 0, started = false, gen = 0;
    function pickSet() { return innerWidth / innerHeight < 0.9 ? 'm' : 'd'; }
    function url(i) { return `${base}frames/${set}/${String(i).padStart(4, '0')}.webp`; }
    const conn = navigator.connection;
    const lite = !!(conn && (conn.saveData || /(^|-)(2g|3g)$/.test(conn.effectiveType || '')));
    function load() {
      gen++; const g = gen;
      blobs = new Array(N).fill(null); bms.forEach((b) => b.close && b.close()); bms = new Map(); pending = new Set(); settled = 0;
      const order = [], seen = new Set();
      const push = (i) => { if (i >= 0 && i < N && !seen.has(i) && !(lite && i >= 24 && i % 2)) { seen.add(i); order.push(i); } };
      for (let i = 0; i < 24; i += 3) push(i);
      for (const s of [16, 8, 4, 2, 1]) for (let i = 0; i < N; i += s) push(i);
      const want_n = order.length;
      let k = 0, inflight = 0;
      const next = () => {
        while (inflight < 6 && k < order.length) {
          const i = order[k++]; inflight++;
          fetch(url(i)).then((r) => (r.ok ? r.blob() : null)).then((b) => {
            if (g !== gen) return;
            if (b) blobs[i] = b;
            settled++; inflight--; next(); want(); schedule();
            if (settled >= order.length) root.dataset.ready = '1';
          }).catch(() => { if (g !== gen) return; settled++; inflight--; next(); });
        }
      };
      load.total = want_n;
      next();
    }
    async function decodeOne(i) {
      pending.add(i); const g = gen;
      try {
        const b = blobs[i];
        const bmp = ('createImageBitmap' in window) ? await createImageBitmap(b) : await new Promise((res, rej) => {
          const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = URL.createObjectURL(b);
        });
        if (g === gen && Math.abs(i - cur) <= 14) bms.set(i, bmp); else if (bmp.close) bmp.close();
      } catch (e) { /* undecodable frame: skipped */ }
      pending.delete(i); want(); schedule();
    }
    function want() {
      for (let d = 0; d <= 10 && pending.size < 4; d++) {
        for (const i of [cur + d, cur - d]) {
          if (i >= 0 && i < N && blobs[i] && !bms.has(i) && !pending.has(i) && pending.size < 4) decodeOne(i);
        }
      }
      for (const [i, b] of bms) if (Math.abs(i - cur) > 14) { if (b.close) b.close(); bms.delete(i); }
    }
    function nearest(i) {
      if (bms.has(i)) return i;
      for (let d = 1; d < 15; d++) { if (bms.has(i - d)) return i - d; if (bms.has(i + d)) return i + d; }
      return -1;
    }

    // ---------------- layout ----------------
    let vw = 0, vh = 0, dpr = 1, lastKey = '', raf = 0;
    function fit() {
      const [w, h] = D.size[set];
      const s = Math.max(vw / w, vh / h);
      return { s, ox: (vw - w * s) * (set === 'm' ? 0.68 : 0.5), oy: (vh - h * s) / 2 };
    }
    function resize() {
      vw = view.clientWidth; vh = view.clientHeight;
      const s = pickSet();
      if (s !== set) { set = s; if (started) load(); }
      dpr = Math.min(devicePixelRatio || 1, 2, Math.max(1, 1 / fit().s));
      const cw = Math.round(vw * dpr), ch = Math.round(vh * dpr);
      if (canvas.width !== cw || canvas.height !== ch) { canvas.width = cw; canvas.height = ch; }
      lastKey = ''; buildTicks(); schedule();
    }
    function drawFrame(n) {
      const i0 = Math.floor(n), a = n - i0;
      const A = nearest(i0);
      if (A < 0) return false;
      const f = fit(), [w, h] = D.size[set];
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.globalAlpha = 1;
      ctx.drawImage(bms.get(A), f.ox, f.oy, w * f.s, h * f.s);
      const noBlend = i0 >= D.no_blend[0] && i0 < D.no_blend[1];
      if (!noBlend && a > 0.02 && A === i0 && bms.has(i0 + 1)) {
        ctx.globalAlpha = a; ctx.drawImage(bms.get(i0 + 1), f.ox, f.oy, w * f.s, h * f.s); ctx.globalAlpha = 1;
      }
      return true;
    }

    // ---------------- stage pacing: each stage gets a share of the track (sqrt of its frame count) ----------------
    function stageAt(n) {
      for (let i = D.stages.length - 1; i >= 0; i--) { const s = D.stages[i]; if (s.n0 <= n && n <= s.n1) return i; }
      let k = 0; D.stages.forEach((s, i) => { if (s.n0 <= n) k = i; }); return k;
    }
    const segs = [];
    for (let n = 0; n < N; n++) {
      const si = stageAt(n);
      if (segs.length && segs[segs.length - 1].si === si) segs[segs.length - 1].n1 = n; else segs.push({ si, n0: n, n1: n });
    }
    let acc = 0;
    segs.forEach((s) => { s.w = Math.sqrt(s.n1 - s.n0 + 1); acc += s.w; });
    let c0 = 0; segs.forEach((s) => { s.q0 = c0; c0 += s.w / acc; s.q1 = c0; });
    function qToN(q) {
      const s = segs.find((x) => q < x.q1) || segs[segs.length - 1];
      const u = clamp((q - s.q0) / (s.q1 - s.q0));
      const last = s === segs[segs.length - 1];
      return Math.min(N - 1, s.n0 + u * (s.n1 - s.n0 + (last ? 0 : 1)));
    }
    function buildTicks() {
      ticks.innerHTML = segs.map((s, i) => i === 0 ? '' : `<i style="left:${((P_REG + s.q0 * (1 - P_REG)) * 100).toFixed(2)}%"></i>`).join('')
        + D.sheets.map((s, i) => i === 0 ? '' : `<i style="left:${(i / D.sheets.length * P_SHEETS * 100).toFixed(2)}%"></i>`).join('');
    }

    // ---------------- overlay: plan linework in model metres ----------------
    const O = D.overlay;
    (function buildOverlay() {
      const pts = (a) => a.map((p) => `${p[0]},${p[1]}`).join(' ');
      let h = `<polygon class="lot" points="${pts(O.lot)}"/><polygon class="fp" points="${pts(O.fp)}"/>`;
      for (const x of O.gx) h += `<line class="ax" x1="${x}" y1="-4" x2="${x}" y2="18.4"/>`;
      for (const y of O.gy) h += `<line class="ax" x1="-4" y1="${y}" x2="28" y2="${y}"/>`;
      for (const v of O.var) h += `<rect class="pl" x="${v[0]}" y="${Math.min(v[1], v[3])}" width="${v[2] - v[0]}" height="${Math.abs(v[3] - v[1])}"/>`;
      for (const p of O.piles) h += `<circle class="pl" cx="${p[0]}" cy="${p[1]}" r=".25"/>`;
      for (const s of O.stalls) h += `<line class="st" x1="${s[0]}" y1="${s[1]}" x2="${s[0]}" y2="${s[2]}"/>`;
      ovInk.innerHTML = h; ovWhite.innerHTML = h;
    })();
    function regPose() {
      const R = D.reg[set];
      if (!R) return null;
      const f = fit();
      const P = Object.values(R.pts).map((p) => ({ q: [p.model[0], -p.model[1]], w: [f.ox + p.px[0] * f.s * (D.size[set][0] / R.w), f.oy + p.px[1] * f.s * (D.size[set][1] / R.h)] }));
      const qm = [0, 0], wm = [0, 0];
      P.forEach((p) => { qm[0] += p.q[0] / P.length; qm[1] += p.q[1] / P.length; wm[0] += p.w[0] / P.length; wm[1] += p.w[1] / P.length; });
      let re = 0, im = 0, nn = 0;
      P.forEach((p) => {
        const qx = p.q[0] - qm[0], qy = p.q[1] - qm[1], wx = p.w[0] - wm[0], wy = p.w[1] - wm[1];
        re += wx * qx + wy * qy; im += wy * qx - wx * qy; nn += qx * qx + qy * qy;
      });
      return { s: Math.hypot(re / nn, im / nn), th: Math.atan2(im / nn, re / nn), c: wm, qc: qm };
    }
    function sheetPose() {
      // where the lot is drawn on the site-plan sheet right now (north up)
      const sd = D.sheets[D.sheets.length - 1], im = sheets[sheets.length - 1];
      const r = im.getBoundingClientRect(), vr = view.getBoundingClientRect();
      const k = r.width / 420, [x0, y0, x1, y1] = sd.lot_mm;
      const lx = r.left - vr.left + (x0 + x1) / 2 * k, ly = r.top - vr.top + (y0 + y1) / 2 * k;
      const s = (x1 - x0) * k / (O.lot[1][0] - O.lot[0][0]);
      const lc = [(O.lot[0][0] + O.lot[1][0]) / 2, -(O.lot[0][1] + O.lot[2][1]) / 2];
      const rp = regPose(), qc = rp ? rp.qc : lc;
      return { s, th: 0, c: [lx + s * (qc[0] - lc[0]), ly + s * (qc[1] - lc[1])], qc };
    }
    function setPose(P) {
      const c = Math.cos(P.th) * P.s, s = Math.sin(P.th) * P.s;
      const e = P.c[0] - (c * P.qc[0] - s * P.qc[1]), f = P.c[1] - (s * P.qc[0] + c * P.qc[1]);
      const m = `matrix(${c} ${s} ${s} ${-c} ${e} ${f})`;
      ovInk.setAttribute('transform', m); ovWhite.setAttribute('transform', m);
    }

    // ---------------- captions ----------------
    let capKey = '';
    function setCaption(key, step, t, s) {
      if (key === capKey) return;
      capKey = key;
      cap.classList.add('swap');
      setTimeout(() => {
        stepN.textContent = pad2(step);
        stepOf.textContent = ofTxt + (key.startsWith('sheet') ? (lang === 'en' ? ' · Design' : ' · Projeto') : '');
        title.textContent = t; sub.textContent = s; cap.classList.remove('swap');
      }, 160);
    }

    // ---------------- render ----------------
    // the first viewport of scroll is the intro; the rest of the track is the film
    function progress() {
      const r = track.getBoundingClientRect(), span = r.height - vh, q = clamp(-r.top / span), pi = vh / span;
      return { k: clamp(q / pi), p: clamp((q - pi) / (1 - pi)) };
    }
    function sheetTransform(im, sd, e) {
      // desktop: push in towards the sheet's focus point; portrait: the sheet is already large, pan to the focus
      const desk = set === 'd';
      const z = desk ? 1 + (sd.zoom - 1) * e : 1;
      const g = desk ? e : 0.35 + 0.65 * e;
      const fo = desk ? sd.focus : (sd.focus_m || sd.focus);
      const dx = (fo[0] - 0.5) * im.offsetWidth * g, dy = (fo[1] - 0.5) * im.offsetHeight * g;
      im.style.transform = `translate(-50%, -50%) scale(${z.toFixed(4)}) translate(${(-dx).toFixed(1)}px, ${(-dy).toFixed(1)}px)`;
    }
    function render() {
      raf = 0;
      const pr = progress(), p = pr.p, k = pr.k;
      if (intro) intro.apply(k);
      view.classList.toggle('intro', k < 1);
      const kin = clamp((k - 0.55) / 0.45);
      fill.style.transform = `scaleX(${p.toFixed(4)})`;
      let paper = 0, ink = 0, white = 0, capOp = 1, n = 0;
      const S = D.sheets.length;
      if (p < P_SHEETS) {
        paper = 1;
        const t = p / P_SHEETS * S, i = Math.min(S - 1, Math.floor(t)), u = t - i;
        sheets.forEach((im, k) => {
          let a = 0;
          if (k === i) a = i === 0 ? 1 : clamp(u / 0.18);
          if (k === i - 1) a = clamp(1 - u / 0.18);
          im.style.opacity = a.toFixed(3);
          if (a > 0) sheetTransform(im, D.sheets[k], k === i ? ease(clamp((u - 0.2) / 0.65)) : 1);
        });
        const sd = D.sheets[i];
        setCaption('sheet' + i, 1, L(sd), L(sd, 'sub'));
      } else if (p < P_REG) {
        const r = (p - P_SHEETS) / (P_REG - P_SHEETS);
        sheets.forEach((im, k) => { im.style.opacity = k === S - 1 ? (1 - clamp((r - 0.06) / 0.22)).toFixed(3) : 0; });
        sheetTransform(sheets[S - 1], D.sheets[S - 1], 1);
        paper = 1 - clamp((r - 0.42) / 0.36);
        const ov = clamp(r / 0.08) * (1 - clamp((r - 0.84) / 0.16));
        ink = ov * paper; white = ov * (1 - paper);
        const k = ease(clamp((r - 0.10) / 0.62));
        const A = sheetPose(), B = regPose() || A;
        let dth = B.th - A.th; while (dth > Math.PI) dth -= 2 * Math.PI; while (dth < -Math.PI) dth += 2 * Math.PI;
        setPose({ s: A.s * Math.pow(B.s / A.s, k), th: A.th + dth * k, c: [A.c[0] + (B.c[0] - A.c[0]) * k, A.c[1] + (B.c[1] - A.c[1]) * k], qc: B.qc });
        capOp = paper > 0.04 && paper < 0.96 ? 0 : 1;
        const s0 = D.stages[0];
        setCaption('st0', 1, s0[lang], L(s0, 'sub'));
      } else {
        n = qToN((p - P_REG) / (1 - P_REG));
        const si = stageAt(Math.round(n)), s = D.stages[si];
        setCaption('st' + si, si + 1, s[lang], L(s, 'sub'));
      }
      cur = Math.round(n); want();
      sheetsBox.style.opacity = paper.toFixed(3);
      ovInk.style.opacity = ink.toFixed(3); ovWhite.style.opacity = white.toFixed(3);
      cap.style.opacity = capOp * kin;
      bar.style.opacity = kin;
      view.classList.toggle('paper', paper > 0.5);
      cap.classList.toggle('on-paper', paper > 0.5);
      const key = `${set}:${n.toFixed(3)}:${bms.size}`;
      if (key !== lastKey && paper < 1 && drawFrame(Math.min(N - 1, n))) lastKey = key;
      const missing = started && paper < 1 && !blobs[Math.round(n)] && settled < (load.total || N);
      loading.textContent = missing ? `${lang === 'en' ? 'Loading images' : 'Carregando imagens'} ${Math.round(100 * settled / (load.total || N))}%` : '';
    }
    function schedule() { if (!raf) raf = requestAnimationFrame(render); }

    // frames start downloading on the first interaction, or shortly after the page has loaded, so they never compete with it
    const go = () => {
      if (started) return; started = true; load();
      ['scroll', 'pointerdown', 'keydown', 'touchstart'].forEach((t) => removeEventListener(t, go));
    };
    ['scroll', 'pointerdown', 'keydown', 'touchstart'].forEach((t) => addEventListener(t, go, { passive: true }));
    const later = () => setTimeout(go, 2500);
    if (document.readyState === 'complete') later(); else addEventListener('load', later, { once: true });

    addEventListener('scroll', schedule, { passive: true });
    addEventListener('resize', resize);
    resize();
  }
})();
