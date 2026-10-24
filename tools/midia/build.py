# Builds n6c.org/midia/: the sales-kit hub, one folder per seller, the pieces (9:16 + 4:5) with that seller's WhatsApp, and a zip per campaign.
# python3 tools/midia/build.py            (from the repo root; needs node + Playwright, see render.cjs)
# python3 tools/midia/build.py --capture  (also re-captures the espelho de vendas screens from the local server, tools/serve.py on :4747)
# Sellers and campaigns live in config.py. Everything under midia/ is generated: it is wiped and rewritten on every run.
import html, json, os, re, shutil, subprocess, sys, unicodedata, zipfile
sys.path.insert(0, os.path.dirname(__file__))
from config import SELLERS, PARTNER_PHONE, PARTNER_NAME, PARTNER_ROLE, CAMPAIGNS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(HERE, 'src')
WORK = os.path.join(HERE, '_work')
OUT = os.path.join(ROOT, 'midia')
E = html.escape
V = '1'
FMTS = [('9x16', 'story', 1080, 1920, '9:16', 'status e stories'), ('4x5', 'feed', 1080, 1350, '4:5', 'feed')]
WA_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.8-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.5-.2Z"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h17M14 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2"/></svg>'


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-') or 'parceiro'

def fmt_phone(d):
    # 5511927666162 -> (11) 92766-6162
    n = d[2:] if d.startswith('55') else d
    return f'({n[:2]}) {n[2:-4]}-{n[-4:]}'

def sellers():
    out = [dict(s, live=True) for s in SELLERS]
    phone = re.sub(r'\D', '', PARTNER_PHONE)
    if len(phone) in (10, 11): phone = '55' + phone  # typed without the country code
    name = PARTNER_NAME.strip()
    if phone:
        out.append(dict(slug=slugify(name) if name else 'parceiro', name=name or PARTNER_ROLE, first=name.split()[0] if name else '', role=PARTNER_ROLE, phone=phone, live=True))
    else:
        out.append(dict(slug=None, name=PARTNER_ROLE, first='', role='', phone='', live=False))
    return out

def fname(camp, k, f):
    return f'n6c-{camp["id"]}-{k + 1}-{f[0]}.jpg'


# ---------------------------------------------------------------- pieces
def src(name):
    if name.endswith('.svg'):
        return 'file://' + os.path.join(ROOT, 'assets/tl/sheets', name)
    return 'file://' + os.path.join(SRC, name)

def chat_html(ch):
    rows = []
    for kind, txt, t in ch['msgs']:
        side = 'out' if kind.startswith('out') else 'in'
        if kind.endswith('audio'):
            bars = ''.join(f'<i style="--h:{h}"></i>' for h in (4, 7, 10, 6, 12, 9, 5, 11, 8, 13, 6, 9, 4, 10, 7, 12, 5, 8, 6, 4, 9, 7, 10, 5, 8))
            body = f'<span class="aud"><b class="play"></b><span class="wave">{bars}</span><span class="t">{txt}</span></span>'
        elif kind.endswith('file'):
            n, m = txt.split('|')
            body = f'<span class="file"><b>PDF</b><span><span class="fn">{E(n)}</span><span class="fm">{E(m)}</span></span></span>'
        else:
            body = E(txt)
        rows.append(f'<div class="msg {side}">{body}<time>{t}</time></div>')
    return (f'<div class="chat"><div class="chat-h"><span class="av">{E(ch["av"])}</span><span><b>{E(ch["name"])}</b><small>{E(ch["sub"])}</small></span>'
            f'<span class="ex">exemplo</span></div><div class="chat-b">{"".join(rows)}</div></div>')

def media(p, f):
    L = p['layout']
    if L == 'photo':
        return f'<div class="media ph"><img src="{src(p["img"])}" style="object-position:{p.get("pos", "50% 50%")}" alt=""></div>'
    if L == 'sheet':
        img, (fx, fy), z, tag = p['sheets'][f[1]]
        return (f'<div class="media sheet" data-fx="{fx}" data-fy="{fy}" data-z="{z}"><img src="{src(img)}" alt="">'
                f'<span class="tag">{E(tag)}</span></div>')
    if L == 'seq':
        figs = ''.join(f'<figure><img src="{src(i)}" alt=""><figcaption><span>0{k + 1}</span>{E(t)}</figcaption></figure>' for k, (i, t) in enumerate(p['imgs']))
        return f'<div class="media seq">{figs}</div>'
    if L == 'type':
        return '<ol class="media list">' + ''.join(f'<li>{E(t)}</li>' for t in p['items']) + '</ol>'
    if L == 'compare':
        (a, at), (b, bt) = p['imgs']
        return (f'<div class="media cmp"><figure><figcaption>{E(at)}</figcaption><img src="{src(a)}" alt=""></figure>'
                f'<span class="arw">{ARROW}</span><figure><figcaption>{E(bt)}</figcaption><img src="{src(b)}" alt=""></figure></div>')
    if L == 'chat':
        return f'<div class="media chatbox">{chat_html(p["chat"])}</div>'
    if L == 'summary':
        s = p['summary']
        rows = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in s['rows'])
        return (f'<div class="media sumbox"><div class="sum"><div class="sum-h"><span>{E(s["title"])}</span><span class="ex">exemplo</span></div>'
                f'<dl>{rows}</dl><p class="act"><i></i>Próximo passo: {E(s["action"][0].lower() + s["action"][1:])}</p></div></div>')
    if L == 'phone':
        return f'<div class="media phone"><div class="dev"><img src="{src(p["img"])}" alt=""></div></div>'
    raise ValueError(L)

SHEET_JS = '''<script>
document.querySelectorAll('.sheet').forEach(function (b) {
  var img = b.querySelector('img'), W = b.clientWidth, H = b.clientHeight, z = +b.dataset.z, fx = +b.dataset.fx, fy = +b.dataset.fy;
  var w = Math.max(W, H * 420 / 297) * z, h = w * 297 / 420;
  var x = Math.min(0, Math.max(W - w, W / 2 - fx * w)), y = Math.min(0, Math.max(H - h, H / 2 - fy * h));
  img.style.width = w + 'px'; img.style.left = x + 'px'; img.style.top = y + 'px';
});
</script>'''

# shrink the chat until every message fits: a half-cut bubble at the top looks broken
FIT_JS = '''<script>
document.fonts.ready.then(function () { document.querySelectorAll('.chat').forEach(function (c) {
  var b = c.querySelector('.chat-b'), s = parseFloat(getComputedStyle(c).getPropertyValue('--s')) || 1;
  // the messages hang from the bottom, so an overflow shows up as the first bubble starting above the box
  function cut() { return b.firstElementChild.getBoundingClientRect().top < b.getBoundingClientRect().top + 10; }
  for (var i = 0; i < 40 && cut(); i++) { s -= .02; c.style.setProperty('--s', s); }
}); document.body.dataset.fit = 1; });
</script>'''

def piece_html(p, f, seller):
    fonts = 'file://' + os.path.join(ROOT, 'assets/fonts')
    line = f'<p class="line">{E(p["line"])}</p>' if p.get('line') else ''
    txt = f'<div class="txt"><h1>{E(p["head"])}</h1>{line}</div>'
    body = media(p, f)
    who = f'Fale com {seller["first"]}' if seller['first'] else 'Fale com a gente'
    core = f'<div class="pc-body">{txt}{body}</div>' if (p['layout'] == 'phone' and f[1] == 'feed') else (txt + body if p['layout'] == 'type' else body + txt)
    note = f'<p class="note">{E(p["note"])}</p>' if p.get('note') else ''
    dark = ' t-dark' if p['layout'] == 'type' else ''
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link rel="stylesheet" href="{fonts}/fraunces.css"><link rel="stylesheet" href="{fonts}/instrument-sans.css"><link rel="stylesheet" href="file://{HERE}/piece.css">
</head><body class="{dark.strip()}"><div class="pc f-{f[1]} l-{p["layout"]} t-{p["layout"]}{dark}">
<div class="top"><img src="file://{ROOT}/assets/img/n6c-mark-128.png" alt=""><span class="b">N6C</span><span class="kick">{E(p["kicker"])}</span></div>
{core}{note}
<div class="foot"><div class="who"><small>{E(who)} no WhatsApp</small><b>{WA_ICON}{fmt_phone(seller["phone"])}</b></div><span class="site">n6c.org</span></div>
</div>{SHEET_JS if p["layout"] == "sheet" else ""}{FIT_JS if p["layout"] == "chat" else ""}</body></html>'''


# ---------------------------------------------------------------- hub pages
def head(title, depth):
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#f3f1ec">
<link rel="icon" href="/assets/img/n6c-mark-128.png">
<link rel="preload" href="/assets/fonts/fraunces-normal-300-500-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/instrument-sans-normal-400-600-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/fonts/fraunces.css"><link rel="stylesheet" href="/assets/fonts/instrument-sans.css">
<link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/midia/midia.css?v={V}">
<script>document.documentElement.className+=' js'</script>
</head>
<body class="v-maquete p-midia">
<a class="skip" href="#main">Pular para o conteúdo</a>
<header class="mtop"><div class="wrap mtop-in"><a class="brand" href="/midia/"><img src="/assets/img/n6c-mark-128.png" width="30" height="30" alt=""><span>N6C</span></a><span class="mtop-t">Mídia</span>
{'<a class="mtop-back" href="/midia/">Todas as pastas</a>' if depth else '<span class="mtop-note">Uso interno do time comercial</span>'}</div></header>
<main id="main">'''

FOOT = f'''</main>
<footer class="mfoot"><div class="wrap"><p>N6C · material de uso interno do time comercial. Esta página fica fora do menu do site e dos buscadores.</p></div></footer>
<div class="toast" role="status" aria-live="polite" data-toast></div>
<script src="/midia/midia.js?v={V}" defer></script>
</body>
</html>
'''

def steps():
    items = [('Abra a sua pasta', 'Cada pessoa do time tem a sua. As peças já saem com o seu WhatsApp e o endereço n6c.org.'),
             ('Escolha o formato', '9:16 para status do WhatsApp e stories; 4:5 para o feed do Instagram e para mandar numa conversa.'),
             ('Toque em Compartilhar', 'No celular abre a lista de apps: escolha WhatsApp ou Instagram. No computador, a peça é baixada.'),
             ('Escreva uma linha sua', 'Use o texto sugerido da campanha ou o seu jeito de falar. Mande para quem faz sentido, sem disparo em massa.')]
    li = ''.join(f'<li><span class="st-n">0{k + 1}</span><h3>{E(t)}</h3><p>{E(d)}</p></li>' for k, (t, d) in enumerate(items))
    return f'''<section class="how m-how" aria-labelledby="how-h"><div class="wrap">
<div class="sec-h"><p class="label">Como compartilhar</p><h2 class="h2s" id="how-h">Quatro passos, do celular.</h2></div>
<ol class="steps">{li}</ol>
<p class="cap m-how-cap">Para mandar tudo de uma vez ou subir no computador, baixe o .zip da campanha: dentro vêm as duas pastas, 9x16 e 4x5.</p>
</div></section>'''

def thumb(slug, camp, k, f):
    return f'/midia/{slug}/{camp["id"]}/t/{fname(camp, k, f)}'

def hub(ss):
    n_pieces = sum(len(c['pieces']) for c in CAMPAIGNS) * len(FMTS)
    cards = []
    for s in ss:
        if s['live']:
            covers = ''.join(f'<img src="{thumb(s["slug"], c, 0, FMTS[0])}" alt="" width="180" height="320" loading="lazy">' for c in CAMPAIGNS[:3])
            ini = ''.join(w[0] for w in s['name'].split()[:2]).upper()
            cards.append(f'''<li class="sc"><a class="sc-cov" href="/midia/{s["slug"]}/" tabindex="-1" aria-hidden="true">{covers}</a>
<div class="sc-b"><div class="sc-who"><span class="sc-av" aria-hidden="true">{E(ini)}</span><span><h3>{E(s["name"])}</h3><span class="sc-role">{E(s["role"])}</span></span></div>
<a class="sc-wa" href="https://wa.me/{s["phone"]}" target="_blank" rel="noopener">{WA_ICON}<span>{fmt_phone(s["phone"])}</span></a>
<p class="sc-n">{len(CAMPAIGNS)} campanhas · {n_pieces} peças</p>
<a class="btn btn-solid" href="/midia/{s["slug"]}/">Abrir a pasta</a></div></li>''')
        else:
            ghosts = '<span></span>' * 3
            cards.append(f'''<li class="sc sc-off"><div class="sc-cov" aria-hidden="true">{ghosts}</div>
<div class="sc-b"><div class="sc-who"><span class="sc-av" aria-hidden="true">+</span><span><h3>{E(s["name"])}</h3><span class="sc-role">Pasta em preparação</span></span></div>
<p class="sc-off-t">As mesmas campanhas, com o WhatsApp dele em cada peça. A pasta abre assim que o número entrar no cadastro.</p></div></li>''')
    return head('Mídia · N6C', 0) + f'''
<section class="m-hero"><div class="wrap">
<p class="label">Mídia · kit de vendas</p>
<h1 class="d2">Peças prontas para compartilhar.</h1>
<p class="lead">Cada pessoa do time comercial tem a sua pasta. As campanhas são as mesmas para todos; o que muda é o WhatsApp impresso em cada peça, para o contato chegar direto em quem mandou.</p>
</div></section>
<section class="m-sellers" aria-labelledby="sel-h"><div class="wrap">
<h2 class="vh" id="sel-h">Pastas</h2>
<ul class="sc-g">{"".join(cards)}</ul>
</div></section>
{overview(ss)}
{steps()}''' + FOOT

def overview(ss):
    s = next(x for x in ss if x['live'])
    items = ''.join(f'''<li><figure><img src="{thumb(s["slug"], c, 0, FMTS[1])}" alt="" width="540" height="675" loading="lazy" decoding="async"></figure>
<p class="cv-n">0{k + 1} · para {E(c["who"][0].lower() + c["who"][1:])}</p><h3>{E(c["title"])}</h3><p>{E(c["about"])}</p>
<p class="cv-c">{len(c["pieces"])} peças em 9:16 e em 4:5</p></li>''' for k, c in enumerate(CAMPAIGNS))
    return f'''<section class="m-cv" aria-labelledby="cv-h"><div class="wrap">
<div class="sec-h"><p class="label">O que tem em cada pasta</p><h2 class="h2s" id="cv-h">{len(CAMPAIGNS)} campanhas, cada uma para um tipo de cliente.</h2></div>
<ul class="cv-g">{items}</ul></div></section>'''

def seller_page(s):
    nav = ''.join(f'<a href="#{c["id"]}"><span>0{k + 1}</span>{E(c["title"])}</a>' for k, c in enumerate(CAMPAIGNS))
    secs = []
    for k, c in enumerate(CAMPAIGNS):
        grids = []
        for f in FMTS:
            items = []
            for j, p in enumerate(c['pieces']):
                fn = fname(c, j, f)
                url = f'/midia/{s["slug"]}/{c["id"]}/{fn}'
                alt = f'{p["head"]} ({f[4]})'
                items.append(f'''<li class="pz"><figure><img src="{thumb(s["slug"], c, j, f)}" alt="{E(alt)}" width="540" height="{960 if f[1] == "story" else 675}" loading="lazy" decoding="async"></figure>
<div class="pz-a"><button class="btn btn-solid btn-sm" type="button" data-share="{url}" data-name="{fn}" aria-label="Compartilhar a peça {j + 1}, {f[4]}">{share_ico()}<span>Compartilhar</span></button>
<a class="btn btn-line btn-sm pz-dl" href="{url}" download="{fn}" aria-label="Baixar a peça {j + 1}, {f[4]}" title="Baixar">{down_ico()}<span>Baixar</span></a></div></li>''')
            grids.append(f'<ul class="pz-g pz-{f[1]}" data-fmt="{f[0]}">{"".join(items)}</ul>')
        z = f'/midia/{s["slug"]}/n6c-{c["id"]}-{s["slug"]}.zip'
        zsize = os.path.getsize(os.path.join(ROOT, z.lstrip('/'))) / 1e6
        secs.append(f'''<section class="cp" id="{c["id"]}" aria-labelledby="{c["id"]}-h" data-caption="{E(c["caption"])}"><div class="wrap">
<div class="cp-h"><p class="label">Campanha 0{k + 1} · para {E(c["who"].lower() if not c["who"].startswith("Quem") else c["who"][0].lower() + c["who"][1:])}</p>
<h2 class="h2s" id="{c["id"]}-h">{E(c["title"])}</h2><p class="body-l">{E(c["about"])}</p></div>
<div class="cp-g"><div class="cp-side">
<div class="cap-box"><p class="cap-l">Texto sugerido</p><p class="cap-t">{E(c["caption"])}</p>
<button class="btn btn-line btn-sm" type="button" data-copy>{copy_ico()}<span>Copiar o texto</span></button></div>
<a class="btn btn-line cp-zip" href="{z}" download>{down_ico()}<span>Baixar a campanha</span><small>.zip · {len(c["pieces"]) * len(FMTS)} peças · {zsize:.1f} MB</small></a>
</div><div class="cp-pz">{"".join(grids)}</div></div>
</div></section>''')
    fmt_ctl = ''.join(f'<label><input type="radio" name="fmt" value="{f[0]}"{" checked" if i == 0 else ""}><span><b>{f[4]}</b> {f[5]}</span></label>' for i, f in enumerate(FMTS))
    return head(f'Mídia · {s["name"]} · N6C', 1) + f'''
<section class="m-hero m-hero-s"><div class="wrap">
<p class="label">Pasta de {E(s["name"])}</p>
<h1 class="d2">Peças com o seu WhatsApp.</h1>
<p class="lead">Todas saem com <span class="nw">{fmt_phone(s["phone"])}</span> e n6c.org impressos. Escolha o formato, toque em Compartilhar e mande para quem faz sentido.</p>
</div></section>
<div class="m-bar" data-bar><div class="wrap m-bar-in">
<fieldset class="fmt"><legend class="vh">Formato das peças</legend>{fmt_ctl}</fieldset>
<nav class="cp-nav" aria-label="Campanhas">{nav}</nav></div></div>
<div class="cps">{"".join(secs)}</div>
{steps()}''' + FOOT

def share_ico(): return '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7 8l5-5 5 5M5 13v7h14v-7" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
def down_ico(): return '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7 10l5 5 5-5M5 20h14" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
def copy_ico(): return '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 8h11v12H8zM5 16V4h11" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'


# ---------------------------------------------------------------- build
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stdout + r.stderr)
    return r.stdout

def build():
    if '--capture' in sys.argv:
        jobs = [dict(url='http://127.0.0.1:4747/demos/espelho-de-vendas/', out=os.path.join(SRC, 'espelho-mapa.png'), w=390, h=844, dsf=3, wait=1200),
                dict(url='http://127.0.0.1:4747/demos/espelho-de-vendas/#E13', out=os.path.join(SRC, 'espelho-lote.png'), w=390, h=844, dsf=3, wait=1500)]
        os.makedirs(WORK, exist_ok=True); json.dump(jobs, open(os.path.join(WORK, 'cap.json'), 'w'))
        run(['node', os.path.join(HERE, 'render.cjs'), os.path.join(WORK, 'cap.json')])
    ss = sellers()
    if '--pages' in sys.argv:  # rewrite the hub and folder pages only (pieces and zips must exist)
        write_pages(ss); return
    only = [x for a in sys.argv if a.startswith('--only=') for x in a.split('=', 1)[1].split(',')]  # --only=obra-1 re-renders one design, nothing else
    keep = {'midia.css', 'midia.js'}
    if os.path.isdir(OUT) and not only:
        for n in os.listdir(OUT):
            if n not in keep:
                p = os.path.join(OUT, n); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    shutil.rmtree(WORK, ignore_errors=True); os.makedirs(WORK)
    jobs = []
    for s in ss:
        if not s['live']: continue
        for c in CAMPAIGNS:
            os.makedirs(os.path.join(OUT, s['slug'], c['id'], 't'), exist_ok=True)
            for k, p in enumerate(c['pieces']):
                if only and f'{c["id"]}-{k + 1}' not in only: continue
                for f in FMTS:
                    fn = fname(c, k, f)
                    h = os.path.join(WORK, f'{s["slug"]}-{fn}.html')
                    open(h, 'w').write(piece_html(p, f, s))
                    jobs.append(dict(url='file://' + h, out=os.path.join(OUT, s['slug'], c['id'], fn), w=f[2], h=f[3], quality=90, wait=120))
    json.dump(jobs, open(os.path.join(WORK, 'jobs.json'), 'w'))
    print(run(['node', os.path.join(HERE, 'render.cjs'), os.path.join(WORK, 'jobs.json')]).strip())
    for j in jobs:
        t = os.path.join(os.path.dirname(j['out']), 't', os.path.basename(j['out']))
        run(['sips', '-Z', '960' if j['h'] == 1920 else '675', '-s', 'format', 'jpeg', '-s', 'formatOptions', '78', j['out'], '--out', t])
    if only:
        print('pieces only (--only): pages and zips not rewritten'); return
    for s in ss:
        if not s['live']: continue
        for c in CAMPAIGNS:
            z = os.path.join(OUT, s['slug'], f'n6c-{c["id"]}-{s["slug"]}.zip')
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_STORED) as zf:
                for k in range(len(c['pieces'])):
                    for f in FMTS:
                        zf.write(os.path.join(OUT, s['slug'], c['id'], fname(c, k, f)), f'n6c-{c["id"]}/{f[0]}/{fname(c, k, f)}')
    write_pages(ss)
    print('midia:', ', '.join(s['slug'] for s in ss if s['live']), '| pieces', len(jobs))

def write_pages(ss):
    for s in ss:
        if s['live']:
            open(os.path.join(OUT, s['slug'], 'index.html'), 'w').write(seller_page(s))
    open(os.path.join(OUT, 'index.html'), 'w').write(hub(ss))

if __name__ == '__main__':
    build()
