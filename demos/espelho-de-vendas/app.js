/* Vale do Araçá: espelho de vendas (demonstração N6C, empreendimento fictício). No dependencies. */
(() => {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const SVGNS = 'http://www.w3.org/2000/svg';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const phoneMQ = matchMedia('(max-width: 767px)');
  const STATUS = { disponivel: 'Disponível', reservado: 'Reservado', vendido: 'Vendido' };
  const ORDER = ['disponivel', 'reservado', 'vendido'];
  const brl = (n) => 'R$ ' + Math.round(n).toLocaleString('pt-BR');
  const num = (n, d = 0) => n.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const AREA_BINS = [
    { id: 'all', label: 'Todas', test: () => true },
    { id: 's', label: 'até 350 m²', test: (l) => l.area <= 350 },
    { id: 'm', label: '350 a 450 m²', test: (l) => l.area > 350 && l.area <= 450 },
    { id: 'l', label: 'acima de 450 m²', test: (l) => l.area > 450 },
  ];
  const FLAGS = [
    { id: 'norte', label: 'Frente norte', test: (l) => l.faces === 'N' },
    { id: 'esquina', label: 'De esquina', test: (l) => !!l.corner },
    { id: 'verde', label: 'Em frente à área verde', test: (l) => l.street === 'Rua das Pitangueiras' },
  ];
  const PRICE_MAX = 395000;
  const state = { status: { disponivel: true, reservado: true, vendido: true }, area: 'all', price: PRICE_MAX, flags: {}, sort: 'id' };

  let D, lots, byId = {}, sel = null, lastTrigger = null;
  const svg = $('#map'), wrap = $('#mapStage');
  const el = (tag, attrs = {}, parent) => {
    const n = document.createElementNS(SVGNS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  };
  const ring = (pts) => 'M' + pts.map((p) => p[0] + ' ' + p[1]).join('L') + 'Z';
  const line = (pts) => 'M' + pts.map((p) => p[0] + ' ' + p[1]).join('L');
  const multi = (polys) => polys.map((rings) => rings.map(ring).join('')).join('');
  const h = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const k in attrs) {
      if (k === 'class') n.className = attrs[k];
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    }
    for (const c of kids) if (c != null) n.append(c);
    return n;
  };

  /* ---------------- map ---------------- */
  const G = {};
  function buildMap() {
    const defs = el('defs', {}, svg);
    const pat = el('pattern', { id: 'hatch', patternUnits: 'userSpaceOnUse', width: 2.4, height: 2.4, patternTransform: 'rotate(45)' }, defs);
    el('rect', { width: 2.4, height: 2.4, fill: '#e8b453' }, pat);
    el('rect', { width: 0.8, height: 2.4, fill: '#c98f22' }, pat);

    G.terrain = svg.querySelector('image');
    svg.insertBefore(defs, G.terrain);
    const gc = el('g', { 'aria-hidden': 'true' }, svg);
    for (const c of D.contours) el('path', { d: line(c.pts), class: 'm-contour' + (c.major ? ' major' : ''), 'vector-effect': 'non-scaling-stroke' }, gc);
    // the existing road fades out past the drawing, like the terrain does
    const fx = el('linearGradient', { id: 'fadeX', gradientUnits: 'userSpaceOnUse', x1: -30, x2: D.w + 30, y1: 0, y2: 0 }, defs);
    [[0, 0], [30 / (D.w + 60), 1], [(D.w + 30) / (D.w + 60), 1], [1, 0]].forEach(([o, a]) => el('stop', { offset: o, 'stop-color': '#fff', 'stop-opacity': a }, fx));
    const mk = el('mask', { id: 'fadeMask', maskUnits: 'userSpaceOnUse', x: -40, y: -40, width: D.w + 80, height: D.h + 80 }, defs);
    el('rect', { x: -40, y: -40, width: D.w + 80, height: D.h + 80, fill: 'url(#fadeX)' }, mk);
    const gr = el('g', { 'aria-hidden': 'true', mask: 'url(#fadeMask)' }, svg);
    el('path', { d: multi(D.asphalt), class: 'm-asphalt', 'fill-rule': 'evenodd' }, gr);
    el('path', { d: multi(D.walk), class: 'm-walk', 'fill-rule': 'evenodd' }, gr);
    el('path', { d: multi(D.median), class: 'm-median' }, gr);
    // street trees on the avenue sidewalks, every 10 m between the crossings
    const gt = el('g', { 'aria-hidden': 'true' }, svg);
    const crossings = [94, 168].map((y0) => y0 + 5 * Math.sin(159 / 55 + 0.6));
    const yTop = 30 + 7 + 5 * Math.sin(159 / 55 + 0.6) + 9, yBot = 246 - 7 + 5 * Math.sin(159 / 55 + 0.6) - 9;
    for (const x of [151.7, 166.3]) {
      for (let y = yTop; y <= yBot; y += 10) {
        if (crossings.some((c) => Math.abs(y - c) < 16)) continue;
        el('circle', { cx: x + 0.5, cy: y + 0.6, r: 1.7, fill: 'rgba(30,42,26,.28)' }, gt);
        el('circle', { cx: x, cy: y, r: 1.6, fill: '#5f8350' }, gt);
        el('circle', { cx: x - 0.35, cy: y - 0.35, r: 0.9, fill: '#7a9b62' }, gt);
      }
    }
    // praça: a loop path around the clearing and a link to the street
    const gp = el('g', { 'aria-hidden': 'true' }, svg);
    el('ellipse', { cx: 334, cy: 100, rx: 11.5, ry: 31, class: 'm-lawn' }, gp);
    el('ellipse', { cx: 334, cy: 100, rx: 11.5, ry: 31, class: 'm-path', 'stroke-width': 1.6 }, gp);
    el('path', { d: 'M314 100H322.5', class: 'm-path', 'stroke-width': 1.6 }, gp);
    el('path', { d: ring(D.pub), class: 'm-public', 'vector-effect': 'non-scaling-stroke' }, gp);
    el('path', { d: line(D.split), class: 'm-public', 'vector-effect': 'non-scaling-stroke', 'stroke-dasharray': '4 3' }, gp);
    el('path', { d: line(D.appLimit), class: 'm-app', 'vector-effect': 'non-scaling-stroke' }, gp);
    el('path', { d: ring(D.boundary), class: 'm-boundary', 'vector-effect': 'non-scaling-stroke' }, gp);

    G.lots = el('g', {}, svg);
    for (const l of lots) {
      l.shape = el('path', { d: ring(l.poly), class: 'm-lot lot-shape ' + l.status, 'data-id': l.id, 'vector-effect': 'non-scaling-stroke' }, G.lots);
    }
    G.sel = el('g', { 'aria-hidden': 'true' }, svg);

    // labels: sizes are set in screen px by setLabelSizes()
    G.areas = el('g', { 'aria-hidden': 'true' }, svg);
    const area = (x, y, a, b, near) => {
      const t = el('text', { x, y, class: 'm-area' + (near ? ' near' : '') }, G.areas);
      el('tspan', { x, dy: '0' }, t).textContent = a;
      if (b) { const s = el('tspan', { x, dy: '1.25em', class: 's' }, t); s.textContent = b; }
    };
    area(334, 97, 'Praça', num(D.stats.praca) + ' m²', true);
    area(334, 209, 'Institucional', num(D.stats.inst) + ' m²', true);
    area(159, 268, 'Área verde e APP', num(D.stats.verde / 10000, 2) + ' ha');
    area(70, 305, 'Córrego do Araçá', null);
    const ap = D.appLimit.find((p) => p[0] >= 262);
    area(ap[0], ap[1] - 1.6, 'Limite da APP', null, true);
    G.streets = el('g', { 'aria-hidden': 'true' }, svg);
    D.labels.forEach((lb, i) => {
      if (lb.name.startsWith('Estrada') && lb.pts[0][0] < 100) return;  // the map title sits over the west half of the road
      el('path', { id: 'sl' + i, d: line(lb.pts), fill: 'none' }, defs);
      const t = el('text', { class: 'm-street', dy: '.35em' }, G.streets);
      const tp = el('textPath', { href: '#sl' + i, startOffset: '50%', 'text-anchor': 'middle' }, t);
      tp.textContent = lb.name;
    });
    const vx = { 'Rua dos Jerivás': 13, 'Avenida dos Araçás': 155.5, 'Rua das Quaresmeiras': 307 };
    for (const v of D.vlabels) {
      const t = el('text', { class: 'm-street', x: 0, y: 0, dy: '.35em', 'text-anchor': 'middle', transform: `translate(${vx[v.name]} ${v.y}) rotate(-90)` }, G.streets);
      t.textContent = v.name;
    }
    G.nums = el('g', { 'aria-hidden': 'true' }, svg);
    for (const l of lots) {
      l.label = el('text', { x: l.cx, y: l.cy, class: 'm-num ' + l.status }, G.nums);
      l.label.textContent = l.id;
    }
    G.qs = el('g', { 'aria-hidden': 'true' }, svg);
    for (const q of D.quadras) {
      const t = el('text', { x: q.cx, y: q.cy, class: 'm-q' }, G.qs);
      t.textContent = q.q;
    }
  }

  /* ---------------- view box, zoom, pan ---------------- */
  let vb = null, kFit = 1, anim = null;
  const K_MAX = 8;
  const fitBox = () => ({ x: D.view[0], y: D.view[1], w: D.view[2], h: D.view[3] });
  const kOf = (v) => Math.min(svg.clientWidth / v.w, svg.clientHeight / v.h);
  function clamp(v) {
    const k = kOf(v), f = fitBox();
    let w = v.w, hh = v.h;
    if (k < kFit) { const s = k / kFit; w *= s; hh *= s; }
    if (kOf({ w, h: hh }) > K_MAX) { const s = kOf({ w, h: hh }) / K_MAX; w *= s; hh *= s; }
    // keep the view inside the drawing: the centre may only travel as far as the edge allows
    const lim = (c, half, a, len) => (half * 2 >= len ? a + len / 2 : Math.max(a + half, Math.min(a + len - half, c)));
    const k2 = Math.min(svg.clientWidth / w, svg.clientHeight / hh);
    const visW = svg.clientWidth / k2, visH = svg.clientHeight / k2;  // what "meet" really shows
    const cx = lim(v.x + w / 2, visW / 2, f.x, f.w), cy = lim(v.y + hh / 2, visH / 2, f.y, f.h);
    return { x: cx - w / 2, y: cy - hh / 2, w, h: hh };
  }
  function setVB(v, clampIt = true) {
    vb = clampIt ? clamp(v) : v;
    svg.setAttribute('viewBox', `${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
    setLabelSizes();
  }
  function animateTo(target) {
    target = clamp(target);
    if (anim) cancelAnimationFrame(anim);
    if (reduce) return setVB(target);
    const from = { ...vb }, t0 = performance.now(), dur = 380;
    const ease = (t) => 1 - Math.pow(1 - t, 3);
    const step = (now) => {
      const t = Math.min(1, (now - t0) / dur), e = ease(t);
      setVB({ x: from.x + (target.x - from.x) * e, y: from.y + (target.y - from.y) * e, w: from.w + (target.w - from.w) * e, h: from.h + (target.h - from.h) * e }, false);
      anim = t < 1 ? requestAnimationFrame(step) : null;
    };
    anim = requestAnimationFrame(step);
  }
  function zoomAt(f, sx, sy, animate) {
    const r = svg.getBoundingClientRect();
    const k = kOf(vb);
    const ox = (r.width - vb.w * k) / 2, oy = (r.height - vb.h * k) / 2;
    const px = vb.x + (sx - r.left - ox) / k, py = vb.y + (sy - r.top - oy) / k;
    const t = { x: px - (px - vb.x) / f, y: py - (py - vb.y) / f, w: vb.w / f, h: vb.h / f };
    animate ? animateTo(t) : setVB(t);
  }
  function boxAround(minx, miny, maxx, maxy, pad) {
    const w = maxx - minx + pad * 2, hh = maxy - miny + pad * 2;
    const ar = svg.clientWidth / svg.clientHeight;
    const W = Math.max(w, hh * ar), H = W / ar;
    return { x: (minx + maxx) / 2 - W / 2, y: (miny + maxy) / 2 - H / 2, w: W, h: H };
  }
  const bbox = (pts) => pts.reduce((b, p) => [Math.min(b[0], p[0]), Math.min(b[1], p[1]), Math.max(b[2], p[0]), Math.max(b[3], p[1])], [1e9, 1e9, -1e9, -1e9]);

  let lod = '';
  function setLabelSizes() {
    const k = kOf(vb);
    const px = (n) => (n / k).toFixed(3);
    G.nums.setAttribute('font-size', px(13));
    G.streets.setAttribute('font-size', px(13));
    G.areas.setAttribute('font-size', px(13));
    G.areas.setAttribute('stroke-width', px(3));
    G.qs.setAttribute('font-size', px(30));
    G.qs.setAttribute('stroke-width', px(4));
    const near = k >= 2.45;
    const nl = near ? 'lod-near' : 'lod-far';
    if (nl !== lod) { svg.classList.remove('lod-near', 'lod-far'); svg.classList.add(nl); lod = nl; }
    svg.classList.toggle('zoomed', k > kFit * 1.05);
    const need = k * (devicePixelRatio || 1);
    const tier = need > 6 ? 'terrain-xl' : need > 2.6 ? 'terrain' : null;
    if (tier && G.tier !== tier && !(G.tier === 'terrain-xl')) {
      G.tier = tier;
      const src = 'assets/' + tier + '.webp', im = new Image();
      im.onload = () => { if (G.tier === tier) G.terrain.setAttribute('href', src); };
      im.src = src;
    }
    updateHint(k);
    updateScale(k);
  }
  function updateHint(k) {
    const hint = $('#mapHint');
    const txt = k < 2.45 ? 'Toque numa quadra para aproximar' : (k > kFit * 1.05 ? 'Arraste para mover o mapa' : 'Toque num lote para ver a ficha');
    if (hint.dataset.t !== txt) { hint.dataset.t = txt; hint.textContent = txt; }
  }

  // scale bar + north arrow (screen space)
  const scaleEl = h('div', { class: 'scale', 'aria-hidden': 'true' });
  wrap.appendChild(scaleEl);
  function updateScale(k) {
    const steps = [10, 20, 25, 50, 100];
    const m = steps.find((s) => s * k >= 48) || 100;
    scaleEl.innerHTML = `<span class="nn"><svg viewBox="0 0 24 24" class="north"><path d="M12 2l7 20-7-5-7 5z" fill="currentColor"/></svg>N</span><span class="sb"><i style="width:${(m * k).toFixed(1)}px"></i><b>${m} m</b></span>`;
  }

  // pointers: drag to pan, pinch to zoom, tap to select
  const ptrs = new Map();
  let gesture = null;
  svg.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 1) gesture = { x: e.clientX, y: e.clientY, t: performance.now(), vb: { ...vb }, moved: false, target: e.target, type: e.pointerType };
    if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; gesture = { pinch: true, d: Math.hypot(a.x - b.x, a.y - b.y), vb: { ...vb }, mid: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }, moved: true }; }
  });
  svg.addEventListener('pointermove', (e) => {
    if (!ptrs.has(e.pointerId)) { hover(e); return; }
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (!gesture) return;
    if (gesture.pinch && ptrs.size === 2) {
      const [a, b] = [...ptrs.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      vb = { ...gesture.vb };
      zoomAt(d / gesture.d, gesture.mid.x, gesture.mid.y, false);
      return;
    }
    const dx = e.clientX - gesture.x, dy = e.clientY - gesture.y;
    if (!gesture.moved && Math.hypot(dx, dy) > 6) {
      gesture.moved = true;
      if (anim) cancelAnimationFrame(anim);
      try { svg.setPointerCapture(e.pointerId); } catch (_) {}
      svg.classList.add('dragging');
      tip.hidden = true;
    }
    if (gesture.moved) {
      const k = kOf(gesture.vb);
      setVB({ ...gesture.vb, x: gesture.vb.x - dx / k, y: gesture.vb.y - dy / k });
    }
  });
  const endPtr = (e) => {
    if (!ptrs.has(e.pointerId)) return;
    ptrs.delete(e.pointerId);
    svg.classList.remove('dragging');
    if (e.type === 'pointerup' && gesture && !gesture.moved && !gesture.pinch && ptrs.size === 0) tap(gesture);
    if (ptrs.size === 0) gesture = null;
  };
  svg.addEventListener('pointerup', endPtr);
  svg.addEventListener('pointercancel', endPtr);
  svg.addEventListener('pointerleave', () => { tip.hidden = true; });
  svg.addEventListener('wheel', (e) => {
    if (!(e.ctrlKey || e.metaKey)) return;  // plain wheel scrolls the page; ctrl/⌘ + wheel and trackpad pinch zoom
    e.preventDefault();
    zoomAt(Math.exp(-e.deltaY * 0.01), e.clientX, e.clientY, false);
  }, { passive: false });
  svg.addEventListener('dblclick', (e) => { e.preventDefault(); zoomAt(1.8, e.clientX, e.clientY, true); });

  function tap(g) {
    const id = g.target && g.target.dataset && g.target.dataset.id;
    if (!id) return;
    const l = byId[id];
    if (g.type !== 'mouse' && kOf(vb) < 2.45) {  // too small for a finger: zoom to the quadra first
      const q = D.quadras.find((qq) => qq.q === l.q);
      const b = bbox(q.poly);
      animateTo(boxAround(b[0], b[1], b[2], b[3], 6));
      return;
    }
    lastTrigger = null;
    select(id, { from: 'map' });
  }

  // hover tooltip (mouse only; the same facts are in the sheet and the list)
  const tip = h('div', { class: 'tip', hidden: '' });
  wrap.appendChild(tip);
  function hover(e) {
    if (e.pointerType !== 'mouse') return;
    const id = e.target.dataset && e.target.dataset.id;
    if (!id) { tip.hidden = true; return; }
    const l = byId[id];
    tip.innerHTML = `<b>${l.id}</b> ${num(l.area)} m² · ${l.status === 'vendido' ? 'Vendido' : brl(l.price) + (l.status === 'reservado' ? ' · reservado' : '')}`;
    const r = wrap.getBoundingClientRect();
    tip.hidden = false;
    const x = Math.min(e.clientX - r.left + 14, r.width - tip.offsetWidth - 8);
    tip.style.transform = `translate(${x}px, ${e.clientY - r.top + 16}px)`;
  }

  document.querySelectorAll('[data-zoom]').forEach((b) => b.addEventListener('click', () => {
    const r = svg.getBoundingClientRect();
    const z = b.dataset.zoom;
    if (z === 'fit') animateTo(fitBox());
    else zoomAt(z === 'in' ? 1.6 : 1 / 1.6, r.left + r.width / 2, r.top + r.height / 2, true);
  }));

  /* ---------------- filters + list ---------------- */
  const pass = (l) => state.status[l.status] && AREA_BINS.find((b) => b.id === state.area).test(l) &&
    (l.status === 'vendido' || l.price <= state.price) && FLAGS.every((f) => !state.flags[f.id] || f.test(l));
  const filtersActive = () => state.area !== 'all' || state.price < PRICE_MAX || FLAGS.some((f) => state.flags[f.id]) || ORDER.some((s) => !state.status[s]);

  function buildPanel() {
    $('#updated').textContent = D.updated;
    const counts = Object.fromEntries(ORDER.map((s) => [s, lots.filter((l) => l.status === s).length]));
    const bar = $('#bar');
    for (const s of ORDER) bar.appendChild(h('i', { class: 'sw-' + s, style: `flex:${counts[s]}` }));
    const leg = $('#legend');
    for (const s of ORDER) {
      leg.appendChild(h('button', { type: 'button', class: 'leg', 'aria-pressed': 'true', 'data-s': s,
        onclick: (e) => { state.status[s] = !state.status[s]; e.currentTarget.setAttribute('aria-pressed', state.status[s]); render(); } },
        h('span', { class: 'leg-top' }, STATUS[s] + (s === 'disponivel' ? 'is' : 's')),
        h('span', { class: 'leg-n' }, h('i', { class: 'sw sw-' + s }), String(counts[s]))));
    }
    const ac = $('#areaChips');
    for (const b of AREA_BINS) {
      ac.appendChild(h('button', { type: 'button', class: 'chip', 'aria-pressed': String(b.id === state.area), 'data-a': b.id,
        onclick: () => { state.area = b.id; ac.querySelectorAll('.chip').forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.a === b.id))); render(); } }, b.label));
    }
    const fc = $('#flagChips');
    for (const f of FLAGS) {
      fc.appendChild(h('button', { type: 'button', class: 'chip', 'aria-pressed': 'false',
        onclick: (e) => { state.flags[f.id] = !state.flags[f.id]; e.currentTarget.setAttribute('aria-pressed', String(!!state.flags[f.id])); render(); } }, f.label));
    }
    const pr = $('#price');
    pr.value = state.price;
    const out = () => { $('#priceOut').textContent = state.price >= PRICE_MAX ? 'sem limite' : brl(state.price); pr.setAttribute('aria-valuetext', $('#priceOut').textContent); };
    out();
    pr.addEventListener('input', () => { state.price = +pr.value; out(); render(); });
    $('#sort').addEventListener('change', (e) => { state.sort = e.target.value; render(); });
    $('#clear').addEventListener('click', clearFilters);

    // about section facts
    const areas = lots.map((l) => l.area), prices = lots.map((l) => l.price);
    const sheet = $('#sheet');
    const fact = (dt, dd) => sheet.appendChild(h('div', {}, h('dt', {}, dt), h('dd', {}, dd)));
    fact('Lotes', String(lots.length));
    fact('Áreas', `${Math.min(...areas)} a ${Math.max(...areas)}\u00a0m²`);
    fact('Preços à vista, em mil reais', `${Math.round(Math.min(...prices) / 1000)} a ${Math.round(Math.max(...prices) / 1000)}`);
    fact('Gleba', num(D.stats.gleba / 10000, 1) + ' ha');
    fact('Área verde e APP', num(D.stats.verde / 10000, 2) + ' ha');
    fact('Praça', num(D.stats.praca) + ' m²');
    const R = D.rules, rules = $('#rules');
    const rule = (dt, dd) => rules.appendChild(h('div', {}, h('dt', {}, dt), h('dd', {}, dd)));
    rule('Recuo da frente', `${R.front} m`);
    rule('Recuos laterais', `${num(R.side, 1)} m`);
    rule('Lateral na esquina', `${R.sideStreet} m`);
    rule('Recuo do fundo', `${R.back} m`);
    rule('Taxa de ocupação', `${R.to}%`);
    rule('Coeficiente', num(R.ca, 1));
  }
  /* terrain section (corte) for the about block, from the same ground model as the map */
  function drawProfile() {
    const P = $('#profile'), pf = D.profile;
    const VW = 1200, VH = 300, ML = 64, MR = 24, MT = 40, MB = 56, EX = 4;
    const y0 = pf.pts[0][0], y1 = pf.pts[pf.pts.length - 1][0];
    const zs = pf.pts.map((p) => p[1]), zmin = Math.floor(Math.min(...zs) / 5) * 5 - 5, zmax = Math.max(...zs) + 2;
    const sx = (VW - ML - MR) / (y1 - y0), sz = sx * EX;
    const H0 = MT + (zmax - zmin) * sz;
    P.setAttribute('viewBox', `0 0 ${VW} ${H0 + MB}`);
    const X = (y) => ML + (y - y0) * sx, Z = (z) => MT + (zmax - z) * sz;
    const zAt = (y) => { const p = pf.pts.reduce((a, b) => (Math.abs(b[0] - y) < Math.abs(a[0] - y) ? b : a)); return p[1]; };
    for (let z = zmin; z <= zmax; z += 5) {
      el('line', { x1: ML, x2: VW - MR, y1: Z(z), y2: Z(z), class: 'pf-grid' }, P);
      el('text', { x: ML - 10, y: Z(z), dy: '.35em', 'text-anchor': 'end', class: 'pf-t' }, P).textContent = `${z} m`;
    }
    const ground = pf.pts.map((p) => `${X(p[0]).toFixed(1)} ${Z(p[1]).toFixed(1)}`);
    el('path', { d: `M${X(y0)} ${H0}L${ground.join('L')}L${X(y1)} ${H0}Z`, class: 'pf-ground' }, P);
    // forest on the APP side of the creek
    for (let y = pf.app + 2; y < y1 - 1; y += 3.2) {
      if (Math.abs(y - pf.creek) < 3) continue;
      const r = 5 + ((y * 7.3) % 4);
      el('circle', { cx: X(y), cy: Z(zAt(y)) - r - 6, r, class: 'pf-tree' }, P);
      el('line', { x1: X(y), x2: X(y), y1: Z(zAt(y)), y2: Z(zAt(y)) - 7, stroke: '#5b6b4c', 'stroke-width': 1.5 }, P);
    }
    el('path', { d: `M${X(pf.creek - 2)} ${Z(zAt(pf.creek)) + 1}h${4 * sx}v5h${-4 * sx}Z`, class: 'pf-water' }, P);
    for (const q of pf.quadras) {
      el('path', { d: `M${X(q.y0)} ${Z(zAt(q.y0)) - 3}L${X(q.y1)} ${Z(zAt(q.y1)) - 3}`, stroke: '#3f8f62', 'stroke-width': 6, 'stroke-linecap': 'butt' }, P);
      el('text', { x: X((q.y0 + q.y1) / 2), y: Z(zAt((q.y0 + q.y1) / 2)) - 18, 'text-anchor': 'middle', class: 'pf-t b' }, P).textContent = `Quadra ${q.q}`;
    }
    el('path', { d: `M${ground.join('L')}`, class: 'pf-line' }, P);
    for (const st of pf.streets) {
      const x = X(st.y);
      el('line', { x1: x, x2: x, y1: Z(zAt(st.y)) + 4, y2: H0 + 8, stroke: '#434b44', 'stroke-width': 1, 'stroke-dasharray': '3 3' }, P);
      el('text', { x, y: H0 + 28, 'text-anchor': 'middle', class: 'pf-t' }, P).textContent = st.name.replace('Rua das ', '').replace('Rua dos ', '');
    }
    el('text', { x: X(pf.creek), y: H0 + 28, 'text-anchor': 'middle', class: 'pf-t' }, P).textContent = 'Córrego';
    el('text', { x: X(y0), y: 16, class: 'pf-t b' }, P).textContent = 'Norte';
    el('text', { x: X(y1), y: 16, 'text-anchor': 'end', class: 'pf-t b' }, P).textContent = 'Sul';
  }
  function clearFilters() {
    state.area = 'all'; state.price = PRICE_MAX; state.flags = {}; ORDER.forEach((s) => (state.status[s] = true));
    document.querySelectorAll('#legend .leg').forEach((b) => b.setAttribute('aria-pressed', 'true'));
    document.querySelectorAll('#areaChips .chip').forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.a === 'all')));
    document.querySelectorAll('#flagChips .chip').forEach((c) => c.setAttribute('aria-pressed', 'false'));
    $('#price').value = PRICE_MAX; $('#price').dispatchEvent(new Event('input'));
  }
  function render() {
    const shown = lots.filter(pass);
    const ok = new Set(shown.map((l) => l.id));
    for (const l of lots) {
      const dim = !ok.has(l.id);
      l.shape.classList.toggle('dim', dim);
      l.label.classList.toggle('dim', dim);
    }
    const sorters = { id: (a, b) => a.id.localeCompare(b.id), price: (a, b) => a.price - b.price, area: (a, b) => b.area - a.area };
    shown.sort(sorters[state.sort]);
    if (state.sort === 'price') shown.sort((a, b) => (a.status === 'vendido') - (b.status === 'vendido'));
    const n = shown.length;
    $('#count').textContent = `${n} ${n === 1 ? 'lote' : 'lotes'}${filtersActive() ? ' com esses filtros' : ''}`;
    $('#empty').hidden = n > 0;
    const list = $('#list');
    list.textContent = '';
    const frag = document.createDocumentFragment();
    for (const l of shown) {
      const right = l.status === 'vendido'
        ? h('span', { class: 'row-price' }, h('small', {}, 'Vendido'))
        : h('span', { class: 'row-price' }, brl(l.price), l.status === 'reservado' ? h('small', {}, 'reservado até ' + l.until.slice(0, 5)) : null);
      frag.appendChild(h('li', {}, h('button', { type: 'button', class: 'row' + (sel === l.id ? ' on' : ''), 'data-id': l.id,
        'aria-label': `Lote ${l.id}, ${num(l.area)} metros quadrados, ${STATUS[l.status]}${l.status !== 'vendido' ? ', ' + brl(l.price) : ''}`,
        onclick: (e) => { lastTrigger = e.currentTarget; select(l.id, { from: 'list' }); } },
        h('i', { class: 'sw sw-' + l.status }), h('span', { class: 'row-id' }, l.id),
        h('span', { class: 'row-meta' }, `${num(l.area)} m² · ${l.street.startsWith('Estrada') ? 'Estrada' : l.street.replace(/^(Rua|Avenida) d[aeo]s? /, '')}`), right)));
    }
    list.appendChild(frag);
  }

  /* ---------------- lot sheet ---------------- */
  const waLink = (msg) => 'https://wa.me/?text=' + encodeURIComponent(msg);
  function similar(l) {
    return lots.filter((o) => o.status === 'disponivel' && o.id !== l.id)
      .map((o) => ({ o, s: Math.abs(o.area - l.area) / l.area + (o.faces === l.faces ? 0 : 0.08) + (o.q === l.q ? -0.03 : 0) }))
      .sort((a, b) => a.s - b.s).slice(0, 4).map((x) => x.o);
  }
  function select(id, opts = {}) {
    const l = byId[id];
    if (!l) return;
    sel = id;
    // map highlight
    G.sel.textContent = '';
    el('path', { d: ring(l.poly), class: 'm-sel-halo', 'vector-effect': 'non-scaling-stroke' }, G.sel);
    el('path', { d: ring(l.poly), class: 'm-sel', 'vector-effect': 'non-scaling-stroke' }, G.sel);
    if (!phoneMQ.matches) {
      const b = bbox(l.poly), k = kOf(vb);
      const inView = b[0] > vb.x && b[2] < vb.x + vb.w && b[1] > vb.y && b[3] < vb.y + vb.h;
      if (!inView || k < 2.45) animateTo(boxAround(b[0], b[1], b[2], b[3], Math.max(40, 300 / Math.max(k, 2.45))));
    }
    document.querySelectorAll('.row.on').forEach((r) => r.classList.remove('on'));
    const row = document.querySelector(`.row[data-id="${id}"]`);
    if (row) row.classList.add('on');

    $('#lotQ').textContent = `Quadra ${l.q} · ${l.street}`;
    $('#lotTitle').textContent = `Lote ${l.id}`;
    const st = $('#lotStatus');
    st.className = 'pill ' + l.status;
    st.textContent = '';
    st.append(h('i', { class: 'sw sw-' + l.status }), l.status === 'reservado' ? `Reservado até ${l.until}` : STATUS[l.status]);

    const R = D.rules;
    const ent = l.price * R.entrada / 100, parc = (l.price - ent) / R.parcelas;
    const pr = $('#lotPrice');
    pr.textContent = '';
    if (l.status === 'vendido') {
      pr.append(h('p', { class: 'price-sub' }, 'Este lote já foi vendido. Abaixo, lotes parecidos que estão disponíveis.'));
    } else {
      pr.append(h('p', { class: 'price-main' }, brl(l.price), h('span', { class: 'sr' }, ' à vista')),
        h('p', { class: 'price-sub' }, `à vista, ou entrada de ${brl(ent)} + ${R.parcelas} × ${brl(parc)}*`));
    }
    const msgs = {
      disponivel: `Olá! Vi no espelho de vendas o lote ${l.id} do Vale do Araçá (${num(l.area)} m², ${brl(l.price)}) e quero saber mais.`,
      reservado: `Olá! O lote ${l.id} do Vale do Araçá está reservado até ${l.until}. Quero entrar na fila caso ele volte a ficar disponível.`,
      vendido: `Olá! Gostei do lote ${l.id} do Vale do Araçá, que já foi vendido. Vocês têm lotes parecidos disponíveis?`,
    };
    const ctaTxt = { disponivel: 'Quero este lote', reservado: 'Entrar na fila do lote', vendido: 'Pedir lotes parecidos' };
    const cta = $('#lotCta');
    cta.textContent = '';
    const wa = h('a', { class: 'btn btn-ink', href: waLink(msgs[l.status]), target: '_blank', rel: 'noopener' });
    wa.innerHTML = document.querySelector('.top-cta .ico').outerHTML;
    wa.append(ctaTxt[l.status], h('span', { class: 'sr' }, ' (abre o WhatsApp)'));
    cta.append(wa, h('button', { type: 'button', class: 'btn btn-line', onclick: () => copyLink(l.id) }, 'Copiar link'));

    drawPlan(l);
    const fp = Math.min(l.buildArea, l.to), total = Math.min(l.ca, fp * 2);
    const facts = $('#lotFacts');
    facts.textContent = '';
    const fact = (dt, dd, small) => { facts.append(h('dt', {}, dt), h('dd', {}, dd, small ? h('small', {}, small) : null)); };
    fact('Área', `${num(l.area)} m²`);
    fact('Medidas', `${num(l.front, 1)} m de frente`, `${num(l.depth, 1)} m de profundidade${l.corner ? '; a esquina é arredondada (raio de 6 m)' : ''}`);
    fact('Frente para', l.street, l.corner ? `Lote de esquina com a ${l.corner}` : null);
    fact('Sol', l.faces === 'N' ? 'Fachada da frente para o norte' : 'Fundos para o norte',
      l.faces === 'N' ? 'A frente recebe sol na maior parte do dia, mais ainda no inverno.' : 'O quintal recebe sol na maior parte do dia; a frente fica mais fresca.');
    fact('Terreno', l.fall >= 0 ? `Desce ${num(Math.abs(l.fall), 1)} m da frente para o fundo` : `Sobe ${num(Math.abs(l.fall), 1)} m da frente para o fundo`,
      `Inclinação média de ${num(l.slope, 1)}%`);
    const fpNote = l.to < l.buildArea
      ? `Dentro dos recuos cabem ${num(l.buildArea)} m², mas a taxa de ocupação de ${R.to}% limita a casa a ${num(l.to)} m² de projeção.`
      : `É a área dentro dos recuos; a taxa de ocupação de ${R.to}% permitiria ${num(l.to)} m².`;
    const soNote = l.ca <= fp * 2 ? ` (limite do coeficiente de aproveitamento ${num(R.ca, 1)})` : '';
    fact('Para construir', `Casa térrea de até ${num(fp)} m²`, `${fpNote} Sobrado: até ${num(total)} m² somando os dois pavimentos${soNote}.`);

    const sim = $('#similar');
    sim.textContent = '';
    sim.hidden = l.status === 'disponivel';
    if (!sim.hidden) {
      const chips = h('div', { class: 'chips' });
      for (const o of similar(l)) chips.append(h('button', { type: 'button', class: 'chip', onclick: () => select(o.id, { from: 'similar', focus: true }) }, `${o.id} · ${num(o.area)} m² · ${brl(o.price)}`));
      sim.append(h('h3', {}, 'Parecidos e disponíveis'), chips);
    }
    $('#lotFine').textContent = (l.status !== 'vendido' ? `* Simulação sem juros e sem correção, só para a demonstração. ` : '') +
      'Preços, medidas e regras são fictícios. Na demonstração, o WhatsApp abre sem destinatário; no espelho do seu loteamento, a conversa vai direto para o corretor de plantão.';

    const lotEl = $('#lot');
    const wasHidden = lotEl.hidden;
    lotEl.hidden = false;
    $('#viewAll').setAttribute('aria-hidden', phoneMQ.matches ? 'false' : 'true');
    if (!phoneMQ.matches) $('#viewAll').hidden = true;
    $('#lotScroll').scrollTop = 0;
    if (phoneMQ.matches && wasHidden && !reduce) {
      lotEl.classList.add('enter');
      requestAnimationFrame(() => requestAnimationFrame(() => lotEl.classList.remove('enter')));
    }
    if (opts.from !== 'map' || opts.focus) $('#lotTitle').focus({ preventScroll: true });
    history.replaceState(null, '', '#' + id);
  }
  function closeLot() {
    sel = null;
    G.sel.textContent = '';
    document.querySelectorAll('.row.on').forEach((r) => r.classList.remove('on'));
    $('#lot').hidden = true;
    $('#viewAll').hidden = false;
    $('#viewAll').removeAttribute('aria-hidden');
    history.replaceState(null, '', location.pathname + location.search);
    if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus();
  }
  $('#back').addEventListener('click', closeLot);
  $('#close').addEventListener('click', closeLot);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && sel) closeLot(); });

  function copyLink(id) {
    const url = location.origin + location.pathname + '#' + id;
    const done = () => toast('Link do lote ' + id + ' copiado');
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, () => toast(url));
    else toast(url);
  }
  let toastT;
  function toast(t) {
    const n = $('#toast');
    n.textContent = t; n.classList.add('on');
    clearTimeout(toastT); toastT = setTimeout(() => n.classList.remove('on'), 2400);
  }

  /* lot diagram: front at the bottom, setbacks, buildable zone, dimensions */
  function drawPlan(l) {
    const P = $('#plan');
    P.textContent = '';
    const flip = l.faces === 'N';  // street to the north: turn the drawing so the street is at the bottom
    const tf = (p) => (flip ? [-p[0], -p[1]] : [p[0], p[1]]);
    const lp = l.poly.map(tf), bp = l.build.map(tf);
    const b = bbox(lp);
    const VW = 340, VH = 250, L0 = 72, T0 = 20, RW = 118, B0 = 48;
    const s = Math.min((VW - L0 - RW) / (b[2] - b[0]), (VH - T0 - B0) / (b[3] - b[1]));
    const X = (x) => L0 + (x - b[0]) * s, Y = (y) => T0 + (y - b[1]) * s;
    const pth = (pts) => 'M' + pts.map((p) => X(p[0]).toFixed(1) + ' ' + Y(p[1]).toFixed(1)).join('L') + 'Z';
    const lx0 = X(b[0]), lx1 = X(b[2]), ly0 = Y(b[1]), ly1 = Y(b[3]), midx = (lx0 + lx1) / 2;
    const txt = (x, y, t, a = {}) => { const n = el('text', { x, y, 'font-size': 13, fill: '#434b44', ...a }, P); n.textContent = t; return n; };
    const STREET = '#ddd8cc';
    el('rect', { x: 0, y: ly1 + 6, width: VW, height: 30, fill: STREET }, P);
    let streetLeft = null;
    if (l.corner) {
      // the rounded corner (many vertices) is on the side of the side street
      const xs = lp.map((p) => p[0]);
      const nearMin = xs.filter((x) => x - b[0] < 6.5).length, nearMax = xs.filter((x) => b[2] - x < 6.5).length;
      streetLeft = nearMin > nearMax;
      const sx = streetLeft ? lx0 - 36 : lx1 + 6;
      el('rect', { x: sx, y: 0, width: 30, height: ly1 + 36, fill: STREET }, P);
      txt(0, 0, l.corner, { 'text-anchor': 'middle', transform: `translate(${sx + 15} ${(ly0 + ly1) / 2}) rotate(-90)`, dy: '.35em' });
    }
    el('path', { d: pth(lp), fill: '#f6f1e3', stroke: '#1b231e', 'stroke-width': 1.5, 'stroke-linejoin': 'round' }, P);
    el('path', { d: pth(bp), fill: 'rgba(29,106,66,.16)', stroke: '#1d6a42', 'stroke-width': 1.3, 'stroke-dasharray': '5 3' }, P);
    const bb = bbox(bp);
    // where a vertical line at x crosses a polygon (drawing units): min and max y, so labels sit between the real edges
    const ys = (poly, x) => {
      const out = [];
      poly.forEach((p, i) => {
        const q = poly[(i + 1) % poly.length], x1 = X(p[0]), x2 = X(q[0]);
        if ((x1 - x) * (x2 - x) <= 0 && x1 !== x2) out.push(Y(p[1]) + (Y(q[1]) - Y(p[1])) * (x - x1) / (x2 - x1));
      });
      return [Math.min(...out), Math.max(...out)];
    };
    const [lt, lb] = ys(lp, midx), [bt, bbm] = ys(bp, midx);
    txt(midx, (bbm + lb) / 2, `${D.rules.front} m`, { 'text-anchor': 'middle', dy: '.35em' });
    txt(midx, (lt + bt) / 2, `${D.rules.back} m`, { 'text-anchor': 'middle', dy: '.35em' });
    txt(midx, (Y(bb[1]) + Y(bb[3])) / 2, `${num(l.buildArea)} m²`, { 'text-anchor': 'middle', dy: '.35em', 'font-size': 15, 'font-weight': 600, fill: '#1d6a42' });
    // depth on the left (outside the side street when it is on the left)
    const dX = streetLeft ? lx0 - 50 : lx0 - 16;
    el('path', { d: `M${dX} ${ly0}V${ly1}M${dX - 4} ${ly0}h8M${dX - 4} ${ly1}h8`, stroke: '#434b44', 'stroke-width': 1, fill: 'none' }, P);
    txt(0, 0, `${num(l.depth, 1)} m`, { 'text-anchor': 'middle', fill: '#1b231e', transform: `translate(${dX - 10} ${(ly0 + ly1) / 2}) rotate(-90)` });
    // frontage, on the street band
    el('path', { d: `M${lx0} ${ly1 + 14}H${lx1}M${lx0} ${ly1 + 10}v8M${lx1} ${ly1 + 10}v8`, stroke: '#434b44', 'stroke-width': 1, fill: 'none' }, P);
    txt(midx, ly1 + 31, `${num(l.front, 1)} m`, { 'text-anchor': 'middle', fill: '#1b231e' });
    txt(VW - 8, ly1 + 31, l.street, { 'text-anchor': 'end' });
    // right column
    const tx = VW - RW + 12;
    const col = (y, a, v, color) => { txt(tx, y, a); txt(tx, y + 21, v, { 'font-size': 17, 'font-weight': 600, fill: color || '#1b231e' }); };
    col(T0 + 12, 'Lote', `${num(l.area)} m²`);
    col(T0 + 62, 'Dentro dos recuos', `${num(l.buildArea)} m²`, '#1d6a42');
    const na = el('g', { transform: `translate(${tx + 6} ${T0 + 124}) rotate(${flip ? 180 : 0})` }, P);
    el('path', { d: 'M0 -11L6 7L0 3L-6 7Z', fill: '#1b231e' }, na);
    txt(tx + 18, T0 + 124, 'Norte', { dy: '.35em' });
    P.setAttribute('aria-label', `Desenho do lote ${l.id}: ${num(l.front, 1)} m de frente para a ${l.street}, ${num(l.depth, 1)} m de profundidade, ${num(l.buildArea)} metros quadrados dentro dos recuos.`);
    $('#planCap').textContent = `Tracejado: onde a casa pode ficar, com recuos de ${D.rules.front} m na frente, ${num(D.rules.side, 1)} m nas laterais${l.corner ? ` (${D.rules.sideStreet} m do lado da rua)` : ''} e ${D.rules.back} m no fundo.`;
  }

  window.__espView = (x, y, w, hh) => setVB({ x, y, w, h: hh });  // evidence shots only
  /* ---------------- boot ---------------- */
  function setGeneralWA() {
    document.querySelectorAll('[data-wa="geral"]').forEach((a) => (a.href = waLink('Olá! Estou vendo o espelho de vendas do Vale do Araçá e quero falar com um corretor.')));
  }
  function resize() {
    kFit = kOf(fitBox());
    if (!vb) setVB(fitBox()); else setVB(vb);
  }
  fetch('data/vale-do-araca.json').then((r) => r.json()).then((data) => {
    D = data; lots = D.lots;
    for (const l of lots) byId[l.id] = l;
    buildMap();
    buildPanel();
    drawProfile();
    setGeneralWA();
    resize();
    render();
    new ResizeObserver(() => resize()).observe(svg);
    const hid = location.hash.slice(1).toUpperCase();
    if (byId[hid]) select(hid, { from: 'map' });
  });
})();
