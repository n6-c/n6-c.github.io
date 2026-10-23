# Builds the N6C site: pt-BR at /, English at /en/, plus 404, legacy redirects and sitemap.
# python3 tools/build.py            (from the repo root; no dependencies)
# Copy lives in tools/content.py. Assets: assets/ (site.css, site.js, fonts, img) and assets/tl/ (construction film).
import json, os, html, sys, re
sys.path.insert(0, os.path.dirname(__file__))
from content import PT, EN, wa, PHONE, EMAIL, SITE, PRICES_PUBLIC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = html.escape
A = '/assets/'
V = '24'  # bump to bust caches of site.css / site.js / tl.*
TL = json.load(open(os.path.join(ROOT, 'assets/tl/data.json')))
DATA = json.load(open(os.path.join(ROOT, 'demos/espelho-de-vendas/data/vale-do-araca.json')))
STEEL_T = '90'  # model.json q.steel_t of the construction study (timelapse/model in n6c-site-mockups)
OTHER = {'pt': EN, 'en': PT}


def facts(c):
    f = dict(TL['facts'][c['short']]); f['steel'] = STEEL_T
    return f


def fill(s, c):
    f = facts(c)
    return re.sub(r'\{(\w+)\}', lambda m: f.get(m.group(1), m.group(0)), s)


# ---------------------------------------------------------------- drawings (SVG, from the demo data)
X0, X1, Y0, Y1 = -10.0, 370.0, -2.0, 342.0
def pts(ring): return ' '.join(f'{x:.1f},{y:.1f}' for x, y in ring)
def drawing_svg(c):
    D = DATA
    bg, lot, quad, road, cont, txt, bnd = '#fbfaf7', '#1b2430', '#3567e0', '#7d8794', '#b9c4b2', '#1b2430', '#b5562e'
    o = [f'<svg viewBox="{X0} {Y0} {X1 - X0} {Y1 - Y0}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice" aria-hidden="true">',
         f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" fill="{bg}"/>']
    o.append(f'<g stroke="{cont}" stroke-width=".25" opacity=".55">' + ''.join(f'<line x1="{x}" y1="{Y0}" x2="{x}" y2="{Y1}"/>' for x in range(0, 371, 50)) +
             ''.join(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}"/>' for y in range(0, 342, 50)) + '</g>')
    o.append(f'<g fill="none" stroke="{cont}" stroke-width=".35">' + ''.join(f'<polyline points="{pts(k["pts"])}" stroke-width="{.6 if k["major"] else .3}"/>' for k in D['contours']) + '</g>')
    o.append(f'<g fill="none" stroke="{road}" stroke-width=".45">' + ''.join(f'<polygon points="{pts(r)}"/>' for p in D['asphalt'] for r in p) + '</g>')
    o.append(f'<polyline points="{pts(D["stream"])}" fill="none" stroke="{quad}" stroke-width=".9" stroke-dasharray="4 2"/>')
    o.append(f'<polygon points="{pts(D["boundary"])}" fill="none" stroke="{bnd}" stroke-width=".8" stroke-dasharray="6 2 1 2"/>')
    o.append(f'<g fill="none" stroke="{quad}" stroke-width=".7">' + ''.join(f'<polygon points="{pts(q["poly"])}"/>' for q in D['quadras']) + '</g>')
    o.append(f'<g fill="none" stroke="{lot}" stroke-width=".4">' + ''.join(f'<polygon points="{pts(l["poly"])}"/>' for l in D['lots']) + '</g>')
    o.append(f'<g fill="none" stroke="{lot}" stroke-width=".2" stroke-dasharray="1 1" opacity=".6">' + ''.join(f'<polygon points="{pts(l["build"])}"/>' for l in D['lots']) + '</g>')
    o.append(f'<g fill="{txt}" font-family="ui-monospace,Menlo,monospace" font-size="3.1" text-anchor="middle">' +
             ''.join(f'<text x="{l["cx"]}" y="{l["cy"] + 1}">{l["id"]}</text>' for l in D['lots']) + '</g>')
    o.append(f'<g fill="{quad}" font-family="ui-monospace,Menlo,monospace" font-size="9" text-anchor="middle" opacity=".9">' +
             ''.join(f'<text x="{q["cx"]}" y="{q["cy"] + 3}">{q["q"]}</text>' for q in D['quadras']) + '</g>')
    o.append(f'<g font-family="ui-monospace,Menlo,monospace" fill="{txt}"><rect x="262" y="318" width="102" height="20" fill="{bg}" stroke="{lot}" stroke-width=".4"/>'
             f'<text x="266" y="326" font-size="4.2">{E(c["draw_title"][0])}</text><text x="266" y="333.5" font-size="3.4" opacity=".75">{E(c["draw_title"][1])}</text></g>')
    o.append('</svg>')
    return ''.join(o)


def review_svg(c):
    ink, soft, paper, mark = '#1b2430', '#a9b0b8', '#fbfaf7', '#d4472a'
    t = c['review']['title']; p = c['plan']
    return f'''<svg viewBox="0 0 640 460" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{E(t)}">
<rect width="640" height="460" fill="{paper}"/>
<g stroke="{soft}" stroke-width=".5" opacity=".6">{''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="460"/>' for x in range(20, 640, 40))}{''.join(f'<line x1="0" y1="{y}" x2="640" y2="{y}"/>' for y in range(20, 460, 40))}</g>
<g fill="none" stroke="{ink}" stroke-linecap="square">
 <rect x="70" y="70" width="380" height="290" stroke-width="7"/>
 <line x1="250" y1="70" x2="250" y2="230" stroke-width="4"/><line x1="70" y1="230" x2="210" y2="230" stroke-width="4"/>
 <line x1="290" y1="230" x2="450" y2="230" stroke-width="4"/><line x1="340" y1="230" x2="340" y2="360" stroke-width="4"/>
 <line x1="250" y1="160" x2="330" y2="160" stroke-width="4"/>
 <path d="M210 230 A40 40 0 0 1 250 190" stroke-width="1.2"/><line x1="250" y1="190" x2="250" y2="230" stroke-width="1.2"/>
 <path d="M300 230 A38 38 0 0 0 338 268" stroke-width="1.2"/>
 <rect x="350" y="240" width="90" height="26" stroke-width="1.2"/><circle cx="395" cy="253" r="8" stroke-width="1"/>
 <rect x="90" y="250" width="120" height="16" stroke-width="1"/>
 <line x1="160" y1="360" x2="230" y2="360" stroke="{paper}" stroke-width="9"/><line x1="160" y1="356" x2="230" y2="356" stroke-width="1"/><line x1="160" y1="364" x2="230" y2="364" stroke-width="1"/>
</g>
<g stroke="{ink}" stroke-width=".8" fill="{ink}" font-family="ui-monospace,Menlo,monospace" font-size="11">
 <line x1="70" y1="398" x2="450" y2="398"/><line x1="70" y1="390" x2="70" y2="406"/><line x1="450" y1="390" x2="450" y2="406"/>
 <text x="246" y="392" stroke="none" text-anchor="middle">{E(p["dim1"])}</text>
 <line x1="492" y1="70" x2="492" y2="360"/><line x1="484" y1="70" x2="500" y2="70"/><line x1="484" y1="360" x2="500" y2="360"/>
 <text x="508" y="219" stroke="none">{E(p["dim2"])}</text>
 <text x="150" y="150" stroke="none" text-anchor="middle" opacity=".8">{E(p["sala"])}</text><text x="150" y="166" stroke="none" text-anchor="middle" opacity=".6" font-size="10">{E(p["area"])}</text>
 <text x="350" y="120" stroke="none" text-anchor="middle" opacity=".8">{E(p["quarto"])}</text>
 <text x="395" y="300" stroke="none" text-anchor="middle" opacity=".8">{E(p["bwc"])}</text>
 <text x="140" y="300" stroke="none" text-anchor="middle" opacity=".8">{E(p["coz"])}</text>
</g>
<g font-family="ui-sans-serif,system-ui,sans-serif" font-weight="600" font-size="14">
 <circle cx="492" cy="150" r="17" fill="none" stroke="{mark}" stroke-width="2.5"/><circle cx="530" cy="122" r="12" fill="{mark}"/><text x="530" y="127" text-anchor="middle" fill="#fff">1</text><line x1="505" y1="140" x2="521" y2="129" stroke="{mark}" stroke-width="2"/>
 <circle cx="372" cy="248" r="30" fill="none" stroke="{mark}" stroke-width="2.5"/><circle cx="416" cy="206" r="12" fill="{mark}"/><text x="416" y="211" text-anchor="middle" fill="#fff">2</text><line x1="394" y1="227" x2="408" y2="214" stroke="{mark}" stroke-width="2"/>
 <circle cx="150" cy="160" r="30" fill="none" stroke="{mark}" stroke-width="2.5"/><circle cx="110" cy="112" r="12" fill="{mark}"/><text x="110" y="117" text-anchor="middle" fill="#fff">3</text><line x1="130" y1="137" x2="118" y2="122" stroke="{mark}" stroke-width="2"/>
</g>
<g font-family="ui-monospace,Menlo,monospace" fill="{ink}" font-size="10.5">
 <rect x="70" y="18" width="380" height="30" fill="none" stroke="{ink}" stroke-width=".8"/>
 <text x="80" y="37">{E(t.upper())}</text>
</g>
</svg>'''


def security_svg(c):
    s = c['sec']; ink, ink3, rule, paper, ok, bad = '#1b2430', '#59616a', '#d9d5cc', '#fbfaf7', '#2f5fd0', '#b3361d'
    rows = []
    for k, (name, state, note) in enumerate(s['rows']):
        y = 150 + k * 62
        col = ok if state == 'ok' else bad
        mark = (f'<path d="M0 0 l6 6 l12 -13" transform="translate(73 {y - 6})" fill="none" stroke="{col}" stroke-width="2.6"/>' if state == 'ok'
                else f'<g transform="translate(76 {y - 9})" stroke="{col}" stroke-width="2.6"><line x1="0" y1="0" x2="14" y2="14"/><line x1="14" y1="0" x2="0" y2="14"/></g>')
        rows.append(f'<circle cx="82" cy="{y - 2}" r="17" fill="none" stroke="{col}" stroke-width="1.5"/>{mark}'
                    f'<text x="116" y="{y - 6}" font-size="15" font-weight="600" fill="{ink}">{E(name)}</text>'
                    f'<text x="116" y="{y + 13}" font-size="13" fill="{col if state != "ok" else ink3}">{E(note)}</text>'
                    f'<line x1="56" y1="{y + 30}" x2="584" y2="{y + 30}" stroke="{rule}"/>')
    return f'''<svg viewBox="0 0 640 460" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{E(s["title"])} · {E(s["domain"])}">
<rect width="640" height="460" fill="#ece9e2"/>
<rect x="36" y="30" width="568" height="404" fill="{paper}" stroke="{rule}"/>
<g font-family="ui-sans-serif,system-ui,sans-serif">
<text x="56" y="70" font-size="12" letter-spacing="1.2" fill="{ink3}">{E(s["title"].upper())}</text>
<text x="56" y="98" font-size="20" font-family="ui-monospace,Menlo,monospace" fill="{ink}">{E(s["domain"])}</text>
<line x1="56" y1="116" x2="584" y2="116" stroke="{ink}" stroke-width="1"/>
{''.join(rows)}
<rect x="56" y="392" width="528" height="28" fill="#f6e3de"/>
<text x="68" y="411" font-size="13" fill="{bad}">{E(s["fix"])}</text>
</g></svg>'''


# ---------------------------------------------------------------- pieces
def icon_wa(cls='ico'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.8-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.5-.2Z"/></svg>'

def icon_mail(cls='ico'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 5.5h17v13h-17z M3.5 6l8.5 7 8.5-7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>'

def arrow(): return '<svg class="arr" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12 12 4M5.5 4H12v6.5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
def down(): return '<svg class="arr" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2v11M3.5 8.5 8 13l4.5-4.5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'

def link(c, key):
    page, _, frag = key.partition('#')
    return c['pages'][page] + (('#' + frag) if frag else '')

def wa_btn(c, cls='btn btn-solid', label=None):
    return f'<a class="{cls}" href="{E(wa(c["wa_msg"]))}" target="_blank" rel="noopener">{icon_wa()}<span>{E(label or c["wa_cta"])}</span>{arrow()}<span class="vh"> ({E(c["new_tab"])})</span></a>'

def header(c, page, alt_href):
    CUR = ' aria-current="page"'; CT = ' aria-current="true"'
    nav = ''.join(f'<a href="{link(c, k)}"{CUR if k == page else ""}>{E(t)}</a>' for k, t in c['nav'])
    pt_on = c['short'] == 'pt'
    langs = (f'<div class="lang" role="group" aria-label="{E(c["lang_label"])}">'
             f'<a href="{PT["pages"][page] if not pt_on else "#"}" data-setlang="pt" lang="pt-BR" hreflang="pt-BR"{CT if pt_on else ""}>PT</a>'
             f'<a href="{EN["pages"][page] if pt_on else "#"}" data-setlang="en" lang="en" hreflang="en"{CT if not pt_on else ""}>EN</a></div>')
    return f'''<a class="skip" href="#main">{E(c["skip"])}</a>
<header class="top" data-top>
  <a class="brand" href="{c["pages"]["index"]}" aria-label="N6C, Node-Six Cybernetics"><img src="{A}img/n6c-mark-128.png" width="30" height="30" alt=""><span>N6C</span></a>
  <nav class="nav" aria-label="{E(c["nav_label"])}">{nav}</nav>
  <div class="top-r">{langs}{wa_btn(c, "btn btn-solid btn-sm top-wa")}<a class="top-wa-i" href="{E(wa(c["wa_msg"]))}" target="_blank" rel="noopener" aria-label="{E(c["wa_cta"])} ({E(c["new_tab"])})">{icon_wa()}</a>
    <button class="menu-b" type="button" data-menu aria-expanded="false" aria-controls="mnav"><span class="vh">{E(c["menu"])}</span><i></i><i></i></button></div>
  <nav class="mnav" id="mnav" hidden aria-label="{E(c["menu"])}">{nav}{wa_btn(c, "btn btn-solid")}</nav>
</header>'''

def footer(c):
    nav = ''.join(f'<li><a href="{link(c, k)}">{E(t)}</a></li>' for k, t in c['nav'])
    nav += f'<li><a href="{c["pages"]["privacidade"]}">{E(c["foot_privacy"])}</a></li>'
    return f'''<footer class="foot">
  <div class="wrap foot-g">
    <div class="foot-b"><a class="brand" href="{c["pages"]["index"]}"><img src="{A}img/n6c-mark-128.png" width="30" height="30" alt="" loading="lazy"><span>N6C</span></a>
      <p>{E(c["foot_tag"])}</p>
      <div class="ctas">{wa_btn(c, "btn btn-wa btn-sm")}</div></div>
    <nav aria-labelledby="fn-h"><h2 class="foot-h" id="fn-h">{E(c["foot_nav"])}</h2><ul>{nav}</ul></nav>
    <div><h2 class="foot-h">{E(c["foot_contact"])}</h2><ul>
      <li><a href="{E(wa(c["wa_msg"]))}" target="_blank" rel="noopener">WhatsApp <span class="nw">{E(c["phone"])}</span><span class="vh"> ({E(c["new_tab"])})</span></a></li>
      <li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
    <div><h2 class="foot-h">{E(c["foot_company"])}</h2><address>{"<br>".join(E(a) for a in c["address"])}</address></div>
  </div>
  <div class="wrap foot-l"><span>{E(c["rights"])}</span><span>{E(c["fictional_note"])}</span></div>
<a class="wa-float" data-wafloat href="{E(wa(c["wa_msg"]))}" target="_blank" rel="noopener" aria-label="{E(c["wa_float"])} ({E(c["new_tab"])})">{icon_wa()}</a>
</footer>'''

def chat(c):
    ch = c['chat']; rows = []
    for kind, txt in ch['msgs']:
        side = 'out' if kind.startswith('out') else 'in'
        if kind.endswith('audio'):
            bars = ''.join(f'<i style="--h:{h}"></i>' for h in (4, 7, 10, 6, 12, 9, 5, 11, 8, 13, 6, 9, 4, 10, 7, 12, 5, 8, 6, 4, 9, 7))
            body = f'<span class="aud"><b class="play" aria-hidden="true"></b><span class="wave" aria-hidden="true">{bars}</span><span class="t">{txt}</span></span>'
        elif kind.endswith('file'):
            n, m = txt.split('|')
            body = f'<span class="file"><b>PDF</b><span><span class="fn">{E(n)}</span><span class="fm">{E(m)}</span></span></span>'
        else:
            body = E(txt)
        rows.append(f'<div class="msg {side}">{body}</div>')
    return f'''<div class="chat" role="img" aria-label="{E(ch["name"])}: {E(ch["sub"])}">
  <div class="chat-h"><span class="av" aria-hidden="true">VA</span><span><b>{E(ch["name"])}</b><small>{E(ch["sub"])}</small></span></div>
  <div class="chat-b">{"".join(rows)}</div>
</div>'''

def picture(base, sizes, alt, cls='', w=None, h=None, lazy=True, sz='100vw'):
    srcset = ', '.join(f'{A}img/{base}-{s}.webp {s}w' for s in sizes)
    src = f'{A}img/{base}-{sizes[-1]}.webp'
    return (f'<img class="{cls}" src="{src}" srcset="{srcset}" sizes="{sz}" alt="{E(alt)}"'
            f'{f" width={w} height={h}" if w else ""}{" loading=lazy decoding=async" if lazy else " fetchpriority=high"}>')

def service_media(s, c):
    m = s['media']
    if m == 'render':
        return picture('maq-light-close', [800, 1600], s['cap'], 'cover', 1600, 1100, sz='(min-width: 901px) 50vw, 100vw')
    if m == 'chat':
        return f'<div class="media-chat">{chat(c)}</div>'
    if m == 'site':
        return picture('site-n6c', [900, 1800], s['cap'], 'cover', 1800, 1200, sz='(min-width: 901px) 50vw, 100vw')
    if m == 'review':
        items = ''.join(f'<li><b>{k + 1}</b>{E(t)}</li>' for k, t in enumerate(c['review']['items']))
        return f'<div class="media-review">{review_svg(c)}<ol class="rv-list">{items}</ol></div>'
    if m == 'security':
        return f'<div class="media-review">{security_svg(c)}</div>'

def slider(c):
    return f'''<div class="cmp" data-cmp style="--p:50%">
  <div class="cmp-model">{picture("maq-light-top", [950, 1900], "", "", 1900, 1720)}</div>
  <div class="cmp-draw">{drawing_svg(c)}</div>
  <span class="cmp-tag l">{E(c["dm_draw"])}</span><span class="cmp-tag r">{E(c["dm_model"])}</span>
  <span class="cmp-line" aria-hidden="true"><b></b></span>
  <input type="range" min="0" max="100" value="50" aria-label="{E(c["dm_slider"])}">
</div>'''

LEGACY = {'services': 'servicos', 'how': 'como', 'work': '@sobre#trabalhos', 'contact': '@contato', 'thesis': 'servicos'}

def head(c, page, extra='', noindex=False):
    other = OTHER[c['short']]
    url = SITE + c['pages'][page]
    alt = other['pages'][page]
    legacy = ''
    if page == 'index':
        m = {k: (c['pages'][v[1:].split('#')[0]] + '#' + v.split('#')[1] if '#' in v else c['pages'][v[1:]]) if v.startswith('@') else '#' + v for k, v in LEGACY.items()}
        legacy = "var L=" + json.dumps(m, separators=(',', ':')) + ",h=location.hash.slice(1);if(L[h]){if(L[h][0]==='#')history.replaceState(null,'',L[h]);else{location.replace(L[h]);return}}"
    detect = ("<script>(function(){var d=document.documentElement;d.className+=' js';" + legacy +
              "var cur=d.lang.slice(0,2),alt=d.getAttribute('data-alt'),s=null;"
              "try{s=localStorage.getItem('n6c-lang')}catch(_){}if(!s&&cur==='pt'&&!/bot|crawl|spider|slurp|lighthouse|headless/i.test(navigator.userAgent)){"
              "var ls=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||''];if(ls[0]&&!ls.some(function(l){return /^pt/i.test(l)}))s='en'}"
              "if(s&&s!==cur&&alt){location.replace(alt+location.hash)}})();</script>")
    return f'''<!doctype html>
<html lang="{c["lang"]}" data-alt="{alt}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(c["titles"][page])}</title>
<meta name="description" content="{E(c["descs"][page])}">
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{url}">'}
<link rel="alternate" hreflang="pt-BR" href="{SITE}{PT["pages"][page]}"><link rel="alternate" hreflang="en" href="{SITE}{EN["pages"][page]}"><link rel="alternate" hreflang="x-default" href="{SITE}{PT["pages"][page]}">
<meta property="og:title" content="{E(c["titles"][page])}"><meta property="og:description" content="{E(c["descs"][page])}"><meta property="og:type" content="website">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/brand/og.png"><meta property="og:locale" content="{c["lang"].replace("-", "_")}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f3f1ec">
<link rel="icon" href="{A}img/n6c-mark-128.png"><link rel="apple-touch-icon" href="{A}img/n6c-mark-128.png">
{detect}
<link rel="preload" href="{A}fonts/fraunces-normal-300-500-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{A}fonts/instrument-sans-normal-400-600-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{A}fonts/fraunces.css"><link rel="stylesheet" href="{A}fonts/instrument-sans.css">
<link rel="stylesheet" href="{A}site.css?v={V}">{extra}
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": "Node-Six Cybernetics", "alternateName": "N6C", "url": SITE + "/", "logo": SITE + "/assets/img/n6c-mark-128.png", "email": EMAIL, "telephone": "+55 11 92766-6162", "founder": {"@type": "Person", "name": "Anderson Silva"}, "address": {"@type": "PostalAddress", "streetAddress": "Paju tn 1a", "postalCode": "50603", "addressLocality": "Tartu", "addressCountry": "EE"}}, ensure_ascii=False) if page == 'index' else ''}</script>
</head>
<body class="v-maquete p-{page}">'''

def cta_band(c):
    return f'''<section class="cta-band" aria-labelledby="cta-h"><div class="wrap cta-in">
  <h2 id="cta-h" class="big">{E(c["cta_h"])}</h2>
  <div><p class="body-l">{E(c["cta_body"])}</p>
  <div class="ctas">{wa_btn(c)}<a class="btn btn-line" href="{c["pages"]["contato"]}">{E(c["cta_contact"])}</a></div>
  <p class="cta-mail">{E(c["cta_mail"])} <a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
</div></section>'''

# ---------------------------------------------------------------- home: the construction film is the hero
def tl_static(c):
    L = c['short']
    out = []
    s0 = TL['sheets'][0]
    out.append(f'<li><img class="sheet" src="{A}tl/{s0["src"]}" alt="" loading="lazy" width="1680" height="1188"><p class="t">{E(s0[L])}</p><p class="s">{E(s0["sub_" + L])}</p></li>')
    for key, n in (('piles', 40), ('frame', 89), ('masonry', 108), ('facade', 135), ('handover', 161)):
        st = next(s for s in TL['stages'] if s['key'] == key)
        out.append(f'<li><picture><source media="(max-aspect-ratio: 9/10)" srcset="{A}tl/frames/m/{n:04d}.webp"><img src="{A}tl/frames/d/{n:04d}.webp" alt="" loading="lazy" width="1600" height="900"></picture>'
                   f'<p class="t">{E(st[L])}</p><p class="s">{E(st["sub_" + L])}</p></li>')
    return ''.join(out)

def home(c):
    L = c['short']
    s0 = TL['sheets'][0]
    cards = ''.join(f'''<article class="svc" data-reveal>
      <a class="svc-a" href="{c["pages"]["servicos"]}#{s["id"]}">
        <div class="svc-m m-{s["media"]}">{service_media(s, c)}</div>
        <div class="svc-t"><span class="svc-n">{s["n"]}</span><h3>{E(s["name"])}</h3><p>{E(s["short"])}</p>
        <span class="status"><i></i>{E(s["status"])}</span><span class="more">{E(c["sv_more"])} {arrow()}</span></div></a></article>''' for s in c['services'])
    dfacts = ''.join(f'<div><dt>{E(a)}</dt><dd>{E(b)}</dd></div>' for a, b in c['dm_facts'])
    steps = ''.join(f'<li data-reveal><span class="st-n">0{k + 1}</span><h3>{E(t)}</h3><p>{E(b)}</p></li>' for k, (t, b) in enumerate(c['steps']))
    in_facts = ''.join(f'<li><b>{E(a)}</b><span>{E(b)}</span></li>' for a, b in c['facts'])
    af = ''.join(f'<li><b>{E(fill(a, c))}</b><span>{E(b)}</span></li>' for a, b in c['after_facts'])
    rv = next(s for s in c['services'] if s['id'] == 'revisao')
    d2 = ''.join(f'<li>{E(x)}</li>' for x in c['dm2_list'])
    rv_items = ''.join(f'<li><b>{k + 1}</b>{E(t)}</li>' for k, t in enumerate(c['review']['items']))
    n_stages = len(TL['stages'])
    return f'''<main id="main">
<section class="tl tl-hero" id="obra" aria-labelledby="hero-h">
  <div class="tl-intro" data-hero>
    <div class="wrap tl-intro-in"><div class="tl-copy" data-tl-copy>
      <p class="label">{E(c["hero_label"])}</p>
      <h1 class="d1" id="hero-h">{E(c["h1"])}</h1>
      <p class="lead">{E(c["lead"])}</p>
      <div class="ctas">{wa_btn(c)}<a class="btn btn-line" href="{c["pages"]["servicos"]}">{E(c["cta2"])}</a></div>
      <p class="tl-hint">{down()}<span>{E(c["hint"])}</span></p>
    </div></div>
  </div>
  <div class="tl-track" data-tl-track>
    <div class="tl-view paper intro">
      <canvas class="tl-canvas" role="img" aria-label="{E(("Sequência da obra em %d etapas; lista das etapas a seguir" if L == "pt" else "Construction sequence in %d stages; stage list follows") % n_stages)}"></canvas>
      <div class="tl-sheets" aria-hidden="true"><div class="tl-sheets-in" data-tl-sheets><img class="tl-sheet is-first" src="{A}tl/{s0["src"]}" alt="" width="1680" height="1188" fetchpriority="high" decoding="async"></div></div>
      <svg class="tl-overlay" aria-hidden="true"><g class="tl-ov-ink"></g><g class="tl-ov-white"></g></svg>
      <div class="tl-scrim" aria-hidden="true"></div>
      <div class="tl-cap" aria-hidden="true">
        <p class="tl-step"><span class="tl-step-n">01</span><span class="tl-step-of"></span></p>
        <p class="tl-title"></p>
        <p class="tl-sub"></p>
      </div>
      <div class="tl-bar" aria-hidden="true"><div class="tl-bar-fill"></div><div class="tl-ticks"></div></div>
      <p class="tl-loading" aria-hidden="true"></p>
      <a class="tl-skipv" href="#modelo">{E(c["tl_skip"])} {down()}</a>
    </div>
  </div>
  <ol class="tl-static">{tl_static(c)}</ol>
  <ol class="tl-sr" aria-label="{E("Etapas da obra" if L == "pt" else "Construction stages")}">{"".join(f"<li>{E(s[L])}: {E(s['sub_' + L])}</li>" for s in TL["stages"])}</ol>
</section>
<noscript><style>.tl .tl-track{{display:none}}.tl .tl-static{{display:grid}}.tl-hero .tl-intro{{position:static;height:auto}}.tl-hero .tl-copy{{padding:140px 0 56px;background:none}}</style></noscript>
<script>{INTRO_JS}</script>

<section class="after wrap" id="modelo" tabindex="-1" aria-labelledby="af-h">
  <p class="label">{E(c["after_label"])}</p>
  <div class="intro-g"><h2 id="af-h" class="big" data-reveal>{E(c["after_h"])}</h2><p class="body-l" data-reveal>{E(fill(c["after_body"], c))}</p></div>
  <ul class="facts">{af}</ul>
  <p class="cap">{E(c["after_note"])}</p>
</section>

<section class="intro wrap" aria-labelledby="in-h">
  <p class="label">{E(c["in_label"])}</p>
  <div class="intro-g"><h2 id="in-h" class="big" data-reveal>{E(c["in_h"])}</h2><p class="body-l" data-reveal>{E(c["in_body"])}</p></div>
  <ul class="facts">{in_facts}</ul>
</section>

<section class="services wrap" id="servicos" aria-labelledby="sv-h">
  <div class="sec-h"><p class="label">{E(c["sv_label"])}</p><h2 id="sv-h" class="h2">{E(c["sv_h"])}</h2>
    <a class="tlink" href="{c["pages"]["servicos"]}">{E(c["sv_all"])} {arrow()}</a></div>
  <div class="svc-g">{cards}</div>
</section>

<section class="demo" id="demos" aria-labelledby="dm-h">
  <div class="wrap">
    <div class="sec-h"><p class="label">{E(c["dm_label"])}</p><h2 id="dm-h" class="h2">{E(c["dm_h"])}</h2></div>
    <div class="demo-head"><span class="svc-n">{E(c["dm1_n"])}</span><h3 class="h2s">{E(c["dm1_h"])}</h3></div>
    {slider(c)}
    <p class="cap">{E(c["dm_key"])}</p>
    <div class="demo-g">
      <div class="demo-t"><p class="body-l">{E(c["dm_body"])}</p><dl class="sheet">{dfacts}</dl>
        <a class="btn btn-line" href="/demos/espelho-de-vendas/" target="_blank" rel="noopener">{E(c["dm_open"])} {arrow()}<span class="vh"> ({E(c["new_tab"])})</span></a></div>
      <figure class="demo-ph" data-reveal>{picture("espelho-phones", [800, 1600], c["dm_phones_alt"], "", 1600, 1000, sz="(min-width: 901px) 50vw, 100vw")}<figcaption class="cap">{E(c["dm_phones_cap"])}</figcaption></figure>
    </div>
    <div class="demo2">
      <div class="demo-head"><span class="svc-n">{E(c["dm2_n"])}</span><h3 class="h2s">{E(c["dm2_h"])}</h3></div>
      <div class="demo-g">
        <figure class="demo-rv" data-reveal>{review_svg(c)}<ol class="rv-list">{rv_items}</ol><figcaption class="cap">{E(c["dm2_note"])}</figcaption></figure>
        <div class="demo-t"><p class="body-l">{E(c["dm2_body"])}</p>
          <div class="lists one"><div><h4>{E(c["dm2_list_h"])}</h4><ul>{d2}</ul></div></div>
          <a class="btn btn-line" href="{c["pages"]["servicos"]}#{rv["id"]}">{E(c["dm2_cta"])} {arrow()}</a></div>
      </div>
    </div>
  </div>
</section>

<section class="how wrap" id="como" aria-labelledby="hw-h">
  <div class="sec-h"><p class="label">{E(c["hw_label"])}</p><h2 id="hw-h" class="h2">{E(c["hw_h"])}</h2></div>
  <ol class="steps">{steps}</ol>
</section>

<section class="team wrap" id="equipe" aria-labelledby="tm-h">
  <div class="sec-h"><p class="label">{E(c["tm_label"])}</p><h2 id="tm-h" class="h2">{E(c["tm_h"])}</h2></div>
  <div class="team-g">
    <figure class="founder" data-reveal><img src="{A}img/founder-768.webp" width="768" height="960" alt="{E(c["founder_alt"])}" loading="lazy" decoding="async">
      <figcaption><b>{E(c["founder_name"])}</b><span>{E(c["founder_role"])}</span></figcaption></figure>
    <div class="team-t"><p>{E(c["founder_short"])}</p><a class="tlink" href="{c["pages"]["sobre"]}">{E(c["tm_more"])} {arrow()}</a></div>
  </div>
</section>
{cta_band(c)}
</main>'''

# Runs inline right after the hero so the drawing sits beside (or under) the headline before the first paint.
INTRO_JS = r"""(function(){var v=document.querySelector('.tl-view'),w=document.querySelector('[data-tl-sheets]'),cp=document.querySelector('[data-tl-copy]'),im=w&&w.querySelector('.tl-sheet');if(!v||!w||!cp||!im)return;
function pose(){var vw=v.clientWidth,vh=innerHeight,r=cp.getBoundingClientRect(),sec=v.closest('.tl').getBoundingClientRect(),top=r.top-sec.top,bot=r.bottom-sec.top,m=Math.max(20,Math.min(72,vw*.042)),T;
var ar=1188/1680,desk=vw>=900&&vw/vh>=.9;
if(desk){var x0=Math.max(r.right+40,vw*.47),x1=vw-m,y0=88,y1=vh-40,tw=Math.min(x1-x0,(y1-y0)/ar);T={x:x0+(x1-x0-tw)/2,y:y0+(y1-y0-tw*ar)/2,w:tw}}
else{var tw2=vw-2*m;T={x:m,y:Math.max(bot+18,vh*.5),w:tw2}}
w.style.transform='none';var b=im.getBoundingClientRect(),vb=v.getBoundingClientRect();var s=T.w/b.width;
var P={s:s,x:T.x-s*(b.left-vb.left),y:T.y-s*(b.top-vb.top)};w._pose=P;window.__tlK=window.__tlK||0;apply(window.__tlK)}
function apply(k){var P=w._pose;if(!P)return;var e=1-k,s=1+(P.s-1)*e;w.style.transform='translate('+(P.x*e).toFixed(1)+'px,'+(P.y*e).toFixed(1)+'px) scale('+s.toFixed(4)+')'}
window.__tlIntro={pose:pose,apply:apply};pose();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(pose);addEventListener('resize',pose);if(!im.complete)im.addEventListener('load',pose)})();"""

# ---------------------------------------------------------------- services page
def price_block(s, c):
    if not s.get('prices'):
        return ''
    rows = []
    for name, val, note in s['prices']:
        v = val if (val and PRICES_PUBLIC) else c['on_request']
        n = note if (PRICES_PUBLIC or not val) else ''
        rows.append(f'<div><dt>{E(name)}</dt><dd><b>{E(v)}</b>{f"<span>{E(n)}</span>" if n else ""}</dd></div>')
    return f'<div class="prices"><h3>{E(c["price_h"])}</h3><dl>{"".join(rows)}</dl><p class="cap">{E(c["price_note"])}</p></div>'

def services_page(c):
    idx = ''.join(f'<li><a href="#{s["id"]}"><span>{s["n"]}</span>{E(s["name"])}</a></li>' for s in c['services'])
    rows = []
    for k, s in enumerate(c['services']):
        g = ''.join(f'<li>{E(x)}</li>' for x in s['get']); n = ''.join(f'<li>{E(x)}</li>' for x in s['need'])
        st = ''.join(f'<li><span>{j + 1:02d}</span>{E(x)}</li>' for j, x in enumerate(s['steps']))
        note = f'<p class="cap">{E(s["note"])}</p>' if s.get('note') else ''
        rows.append(f'''<article class="sv-row{" rev" if k % 2 else ""}" id="{s["id"]}" aria-labelledby="h-{s["id"]}">
  <figure class="sv-m m-{s["media"]}" data-reveal>{service_media(s, c)}<figcaption class="cap">{E(s["cap"])}</figcaption></figure>
  <div class="sv-t"><span class="svc-n">{s["n"]}</span><h2 id="h-{s["id"]}" class="h2s">{E(s["name"])}</h2>
    <span class="status"><i></i>{E(s["status"])}</span>
    <p class="body-l">{E(s["body"])}</p>
    <div class="lists"><div><h3>{E(c["get"])}</h3><ul>{g}</ul></div><div><h3>{E(c["need"])}</h3><ul>{n}</ul></div></div>
    <div class="tline"><h3>{E(c["steps_h"])}</h3><ol>{st}</ol><p class="cap">{E(c["steps_note"])}</p></div>
    {price_block(s, c)}{note}
  </div></article>''')
    faq = ''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in c['faq'])
    return f'''<main id="main">
<section class="page-h wrap" data-hero>
  <p class="label">{E(c["sp_label"])}</p><h1 class="d2">{E(c["sp_h"])}</h1><p class="lead">{E(c["sp_lead"])}</p>
  <ol class="sv-idx">{idx}</ol>
</section>
<div class="wrap sv-list">{"".join(rows)}</div>
<section class="faq wrap" id="perguntas" aria-labelledby="faq-h"><h2 id="faq-h" class="h2">{E(c["faq_h"])}</h2><div class="faq-l">{faq}</div></section>
{cta_band(c)}
</main>'''

# ---------------------------------------------------------------- about page
def about_page(c):
    idx = ''.join(f'<li><a href="#{i}"><span>0{k + 1}</span>{E(t)}</a></li>' for k, (i, t) in enumerate(c['ab_idx']))
    fb = ''.join(f'<p>{E(p)}</p>' for p in c['founder_body'])
    ff = ''.join(f'<li><b>{E(a)}</b><span>{E(b)}</span></li>' for a, b in c['founder_facts'])
    roles = ''.join(f'<li><span class="svc-n">{k + 1:02d}</span><h3>{E(t)}</h3><p>{E(b)}</p></li>' for k, (t, b) in enumerate(c['roles']))
    F = c['work_feat']
    flow = ''.join(f'<li>{E(x)}</li>' for x in F['flow'])
    items = ''.join(f'<li class="wk"><p class="svc-n">{E(m)}</p><h3>{E(t)}</h3><p>{E(b)}</p><p class="tags">{E(g)}</p></li>' for t, m, b, g in c['work_items'])
    co = ''.join(f'<div><dt>{E(a)}</dt><dd>{f"<a href=mailto:{EMAIL}>{EMAIL}</a>" if b == EMAIL else E(b)}</dd></div>' for a, b in c['co_rows'])
    return f'''<main id="main">
<section class="page-h wrap" data-hero>
  <p class="label">{E(c["ab_label"])}</p><h1 class="d2">{E(c["ab_h"])}</h1><p class="lead">{E(c["ab_lead"])}</p>
  <ol class="sv-idx four">{idx}</ol>
</section>

<section class="wrap ab-founder" id="anderson" aria-labelledby="an-h">
  <figure class="founder" data-reveal><img src="{A}img/founder-768.webp" width="768" height="960" alt="{E(c["founder_alt"])}" fetchpriority="high">
    <figcaption><b>{E(c["founder_name"])}</b><span>{E(c["founder_role"])}</span></figcaption></figure>
  <div class="team-t"><h2 class="vh" id="an-h">{E(c["founder_name"])}</h2>{fb}<ul class="facts three">{ff}</ul></div>
</section>

<section class="wrap ab-team" id="equipe" aria-labelledby="eq-h">
  <div class="sec-h"><p class="label">{E(c["team_label"])}</p><h2 id="eq-h" class="h2">{E(c["team_h"])}</h2><p class="body-l">{E(c["team_body"])}</p></div>
  <ul class="roles r3">{roles}</ul>
</section>

<section class="wrap ab-work" id="trabalhos" aria-labelledby="wk-h">
  <div class="sec-h"><p class="label">{E(c["work_label"])}</p><h2 id="wk-h" class="h2">{E(c["work_h"])}</h2><p class="body-l">{E(c["work_body"])}</p></div>
  <article class="wk-feat" data-reveal>
    <div class="wk-flow" aria-hidden="true"><ol>{flow}</ol></div>
    <div><p class="svc-n">{E(F["meta"])}</p><h3 class="h2s">{E(F["name"])}</h3><p class="body-l">{E(F["body"])}</p><p class="tags">{E(F["tags"])}</p></div>
  </article>
  <ul class="wk-g">{items}</ul>
</section>

<section class="wrap ab-co" id="empresa" aria-labelledby="co-h">
  <div class="sec-h"><p class="label">{E(c["co_label"])}</p><h2 id="co-h" class="h2">{E(c["co_h"])}</h2></div>
  <dl class="sheet">{co}</dl>
</section>
{cta_band(c)}
</main>'''

# ---------------------------------------------------------------- contact page
def contact_page(c):
    nx = ''.join(f'<li><span class="st-n">0{k + 1}</span><div><h3>{E(t)}</h3><p>{E(b)}</p></div></li>' for k, (t, b) in enumerate(c['next']))
    opts = ''.join(f'<option>{E(t)}</option>' for t in c['f_topics'])
    return f'''<main id="main">
<section class="page-h wrap contact-h" data-hero>
  <div><p class="label">{E(c["cp_label"])}</p><h1 class="d2">{E(c["cp_h"])}</h1><p class="lead">{E(c["cp_lead"])}</p></div>
  <div class="c-direct">
    <a class="c-big" href="{E(wa(c["wa_msg"]))}" target="_blank" rel="noopener"><span class="c-k">{icon_wa()} {E(c["cp_wa"])}</span><span class="c-v nw">{E(c["phone"])}</span>{arrow()}<span class="vh"> ({E(c["new_tab"])})</span></a>
    <a class="c-big" href="mailto:{EMAIL}"><span class="c-k">{icon_mail()} {E(c["cp_mail"])}</span><span class="c-v">{EMAIL}</span>{arrow()}</a>
  </div>
</section>
<figure class="band">{picture("maq-light-hero", [1200, 2400], "", "", 2400, 1350)}<figcaption class="wrap cap">{E(c["band_cap"])}</figcaption></figure>
<section class="wrap contact-g">
  <div class="c-next">
    <h2 class="h3">{E(c["next_h"])}</h2><ol class="next">{nx}</ol>
    <div class="c-co"><h2 class="h3">{E(c["company_h"])}</h2><address>{"<br>".join(E(a) for a in c["address"])}</address></div>
  </div>
  <form class="c-form" data-waform data-phone="{PHONE}" data-email="{EMAIL}" data-intro="{E(c["f_intro"])}" data-from="{E(c["f_from"])}" data-about="{E(c["f_about"])}" data-subject="{E(c["f_subject"])}" novalidate>
    <h2 class="h3">{E(c["f_h"])}</h2>
    <label for="f-name"><span>{E(c["f_name"])} <small>({E(c["req"])})</small></span></label><input id="f-name" name="name" autocomplete="name" required aria-describedby="e-name"><p class="f-err" id="e-name" hidden>{E(c["f_err_name"])}</p>
    <label for="f-co"><span>{E(c["f_company"])} <small>({E(c["f_company_ph"])})</small></span></label><input id="f-co" name="company" autocomplete="organization">
    <label for="f-topic">{E(c["f_topic"])}</label><select id="f-topic" name="topic">{opts}</select>
    <label for="f-msg"><span>{E(c["f_msg"])} <small>({E(c["req"])})</small></span></label><textarea id="f-msg" name="msg" rows="5" required placeholder="{E(c["f_msg_ph"])}" aria-describedby="e-msg"></textarea><p class="f-err" id="e-msg" hidden>{E(c["f_err_msg"])}</p>
    <div class="f-btns"><button class="btn btn-solid" type="submit" value="wa">{icon_wa()}<span>{E(c["f_send"])}</span>{arrow()}</button>
    <button class="btn btn-line" type="submit" value="mail" data-mail>{icon_mail()}<span>{E(c["f_send_mail"])}</span></button></div>
    <p class="f-note">{E(c["f_note"])}</p>
  </form>
</section>
</main>'''

# ---------------------------------------------------------------- privacy, 404
def privacy_page(c):
    body = ''.join(f'<section><h2 class="h3">{E(h)}</h2>{"".join(f"<p>{E(p)}</p>" for p in ps)}</section>' for h, ps in c['pv'])
    return f'''<main id="main">
<section class="page-h wrap" data-hero><p class="label">{E(c["pv_label"])}</p><h1 class="d2">{E(c["pv_h"])}</h1><p class="cap">{E(c["pv_updated"])}</p></section>
<div class="wrap prose">{body}</div>
{cta_band(c)}
</main>'''

def notfound_page():
    c = PT
    links = lambda cc: ''.join(f'<li><a href="{cc["pages"][k]}">{E(t)}</a></li>' for k, t in [("index", cc["nf_home"])] + [(k.split("#")[0], t) for k, t in cc["nav"] if "#" not in k])
    return f'''<main id="main">
<section class="page-h wrap nf" data-hero>
  <p class="label">404</p><h1 class="d2">{E(c["nf_h"])}</h1><p class="lead">{E(c["nf_body"])}</p>
  <ul class="nf-l">{links(PT)}</ul>
  <div lang="en" class="nf-en"><h2 class="h3">{E(EN["nf_h"])}</h2><p>{E(EN["nf_body"])}</p><ul class="nf-l">{links(EN)}</ul></div>
  <div class="ctas">{wa_btn(c)}</div>
</section>
</main>'''

# ---------------------------------------------------------------- legacy URLs -> new pages
REDIRECTS = {
    'pt/index.html': '/', 'pt/team.html': '/sobre#equipe', 'pt/portfolio.html': '/sobre#trabalhos',
    'team.html': '/en/about#equipe', 'founder.html': '/en/about#anderson', 'kestrel.html': '/en/about#trabalhos',
}
def redirect_page(to):
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>N6C</title><link rel="canonical" href="{SITE}{to.split('#')[0]}"><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={to}"><script>location.replace('{to}')</script></head>
<body style="font:16px/1.5 system-ui,sans-serif;background:#f3f1ec;color:#141c26;padding:2rem"><a href="{to}">N6C</a></body></html>
'''

# ---------------------------------------------------------------- write
def page(c, key, fn, extra=''):
    tl = key == 'index'
    ex = (f'<link rel="stylesheet" href="{A}tl/tl.css?v={V}"><link rel="preload" href="{A}tl/data.json" as="fetch" crossorigin>'
          f'<link rel="preload" as="image" href="{A}tl/{TL["sheets"][0]["src"]}" fetchpriority="high">') if tl else ''
    js = f'<script src="{A}site.js?v={V}" defer></script>' + (f'<script src="{A}tl/tl.js?v={V}" defer></script>' if tl else '')
    return head(c, key, ex) + header(c, key, OTHER[c['short']]['pages'][key]) + fn(c) + footer(c) + js + '\n</body>\n</html>\n'

def build():
    written = []
    def w(rel, s):
        p = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(s); written.append(rel)
    for c in (PT, EN):
        for key, fn in (('index', home), ('servicos', services_page), ('sobre', about_page), ('contato', contact_page), ('privacidade', privacy_page)):
            w(c['files'][key], page(c, key, fn))
    nf = head(PT, 'index', noindex=True).replace(f'<title>{E(PT["titles"]["index"])}</title>', f'<title>{E(PT["nf_title"])}</title>')
    nf = re.sub(r'<script>\(function\(\)\{var d=.*?</script>', "<script>document.documentElement.className+=' js'</script>", nf, flags=re.S)
    nf = nf.replace('data-alt="/en/"', '')
    w('404.html', nf + header(PT, 'index', '/en/').replace(' aria-current="page"', '') + notfound_page() + footer(PT) + f'<script src="{A}site.js?v={V}" defer></script>\n</body>\n</html>\n')
    for src, to in REDIRECTS.items():
        w(src, redirect_page(to))
    urls = []
    for key in ('index', 'servicos', 'sobre', 'contato', 'privacidade'):
        for c in (PT, EN):
            alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{cc["lang"]}" href="{SITE}{cc["pages"][key]}"/>' for cc in (PT, EN))
            urls.append(f'<url><loc>{SITE}{c["pages"][key]}</loc>{alts}<lastmod>2026-10-23</lastmod></url>')
    w('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(urls) + '\n</urlset>\n')
    print('built', len(written), 'files')

if __name__ == '__main__':
    build()
