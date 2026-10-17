#!/usr/bin/env python3
"""Gera o catalogo estatico da loja a partir de catalog.json.

Saida (raiz do projeto):
  index.html, produto/<slug>.html, 404.html, CNAME, .nojekyll,
  robots.txt, sitemap.xml, assets/css/style.css, assets/js/site.js
"""
import html
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "catalog.json")
DOMAIN = "loja.casadoshake.com.br"
SITE = f"https://{DOMAIN}"
WHATSAPP = "5522981757472"

ATTR_LABELS = {"pa_sabor": "Sabor", "pa_tamanho": "Tamanho"}


def esc(s):
    return html.escape(s or "", quote=True)


def nl2br(s):
    return esc(s).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>\n")


BLOCK_TAGS = re.compile(
    r"</?(div|p|h[1-6]|br|li|ul|ol|tr|td|th|table|section|article|span|strong|b|em|i|hr|figure|figcaption|img)[^>]*>",
    re.IGNORECASE,
)


def rich(s):
    """Sanitiza campos ACF que vieram com HTML bruto: remove tags, normaliza espacos."""
    if not s:
        return ""
    t = html.unescape(s)
    t = BLOCK_TAGS.sub("\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = t.replace("\xa0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n[ \t]*\n+", "\n\n", t)
    return nl2br(t.strip())


def attr_label(key):
    if key in ATTR_LABELS:
        return ATTR_LABELS[key]
    return key.replace("pa_", "").replace("_", " ").title()


def opt_label(val):
    return (val or "").replace("-", " ").replace("_", " ").strip().title()


CSS = """:root{
  --green:#236633; --green-dark:#1a4f27; --accent:#7cba46; --accent-dark:#5f9633;
  --bg:#f5f8f3; --card:#ffffff; --ink:#1f2a1d; --muted:#5b6b57; --line:#e0e7db;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:Montserrat,Arial,Helvetica,sans-serif;line-height:1.5}
a{color:var(--green)}
img{max-width:100%;height:auto;display:block}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
header.site{background:var(--green);color:#fff;padding:10px 0}
header.site .wrap{display:flex;align-items:center;gap:14px;justify-content:space-between}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:#fff;min-width:0}
.brand img{width:auto;height:52px;flex:0 0 auto}
.brand span{font-weight:600;font-size:1.15rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.head-wa{background:var(--accent);color:var(--ink);border:2px solid var(--accent);border-radius:10px;
  padding:9px 18px;font-weight:600;text-decoration:none;white-space:nowrap}
.head-wa:hover{background:var(--green);color:#fff}
.hero{background:var(--green);color:#fff;padding:34px 0 40px;text-align:center}
.hero h1{margin:0 0 8px;font-size:2rem}
.hero p{margin:0;opacity:.9}
.hero .logo{width:180px;height:auto;margin:0 auto 14px}
main{padding:26px 0 60px}
.toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:18px}
.search{flex:1 1 260px;min-width:220px;padding:11px 14px;border:2px solid var(--line);border-radius:10px;
  font:inherit;background:#fff}
.search:focus{outline:none;border-color:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{border:2px solid var(--accent);color:var(--green);background:#fff;border-radius:999px;
  padding:6px 14px;font:inherit;font-weight:600;font-size:.85rem;cursor:pointer;text-decoration:none}
.chip.active,.chip:hover{background:var(--accent);color:var(--ink)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;
  display:flex;flex-direction:column}
.card .thumb{position:relative;aspect-ratio:1/1;background:#eef3ea;overflow:hidden}
.card .thumb img{width:100%;height:100%;object-fit:cover}
.card .body{padding:12px 14px 16px;display:flex;flex-direction:column;gap:8px;flex:1}
.card h3{margin:0;font-size:1rem;line-height:1.3}
.card .cats{font-size:.72rem;letter-spacing:.03em;text-transform:uppercase;color:var(--green);font-weight:600}
.card .btn{margin-top:auto}
.btn{display:inline-block;text-align:center;font-weight:600;text-decoration:none;border-radius:10px;
  padding:11px 16px;border:2px solid var(--green);background:var(--green);color:#fff;cursor:pointer;font:inherit}
.btn:hover{background:var(--green-dark);border-color:var(--green-dark)}
.btn-outline{background:#fff;color:var(--green)}
.btn-outline:hover{background:var(--green);color:#fff;border-color:var(--green)}
.empty{color:var(--muted);padding:30px 0;text-align:center}
footer.site{background:var(--green-dark);color:#dfe9d8;padding:22px 0;font-size:.85rem;text-align:center}
footer.site a{color:#fff}
/* product page */
.breadcrumb{font-size:.85rem;color:var(--muted);margin-bottom:14px}
.product{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:32px}
@media(max-width:760px){.product{grid-template-columns:1fr}}
.gallery .main{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff}
.gallery .thumbs{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.gallery .thumbs img{height:64px;width:auto;object-fit:cover;border-radius:8px;border:2px solid var(--line);cursor:pointer}
.gallery .thumbs img.active{border-color:var(--accent)}
.pinfo h1{margin:0 0 6px;font-size:1.6rem}
.pinfo .cats{margin-bottom:16px}
.pinfo .cats a{color:var(--green);text-decoration:none;font-weight:600;font-size:.8rem;text-transform:uppercase;margin-right:8px}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.opt{margin:14px 0}
.opt h4{margin:0 0 8px;font-size:.85rem;text-transform:uppercase;letter-spacing:.03em;color:var(--muted)}
.opt .choices{display:flex;flex-wrap:wrap;gap:8px}
.opt label{border:2px solid var(--line);border-radius:8px;padding:7px 12px;cursor:pointer;font-size:.9rem}
.opt input{position:absolute;opacity:0;pointer-events:none}
.opt input:checked+span{color:var(--green)}
.opt label:has(input:checked){border-color:var(--accent);background:#eef7e7}
.sections{margin-top:28px}
.sections section{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}
.sections h2{margin:0 0 10px;font-size:1.1rem;color:var(--green)}
.sections p{margin:0}
.cta{position:sticky;bottom:0}
.product .btn-wa{font-size:1.05rem;padding:14px 20px}
@media(max-width:560px){
  .brand span{font-size:.95rem}
  .brand img{height:44px}
  .head-wa{padding:8px 12px;font-size:.85rem}
  .hero h1{font-size:1.6rem}
  .grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
}
"""

JS = """(function(){
  // Filtro da home
  var grid=document.getElementById('grid');
  if(grid){
    var cards=Array.prototype.slice.call(grid.querySelectorAll('.card'));
    var q=document.getElementById('q');
    var chips=Array.prototype.slice.call(document.querySelectorAll('.chip[data-cat]'));
    var active='all';
    function apply(){
      var t=(q&&q.value?q.value:'').toLowerCase().trim();
      cards.forEach(function(c){
        var okT=!t||c.dataset.title.indexOf(t)>=0;
        var okC=active==='all'||(' '+c.dataset.cats+' ').indexOf(' '+active+' ')>=0;
        c.style.display=(okT&&okC)?'':'none';
      });
    }
    function setCat(cat){
      active=cat||'all';
      chips.forEach(function(ch){ch.classList.toggle('active',ch.dataset.cat===active);});
      apply();
    }
    chips.forEach(function(ch){ch.addEventListener('click',function(e){e.preventDefault();setCat(ch.dataset.cat);history.replaceState(null,'','#anchor');});});
    if(q)q.addEventListener('input',apply);
    if(location.hash){setCat(location.hash.slice(1));}else{setCat('all');}
  }
  // Galeria do produto
  var main=document.getElementById('mainimg');
  if(main){
    document.querySelectorAll('.thumbs img').forEach(function(t){
      t.addEventListener('click',function(){
        main.src=t.dataset.full;
        document.querySelectorAll('.thumbs img').forEach(function(x){x.classList.remove('active');});
        t.classList.add('active');
      });
    });
  }
  // Variacoes -> mensagem WhatsApp
  var wa=document.getElementById('wa');
  if(wa){
    function build(){
      var parts=[];
      document.querySelectorAll('.opt input:checked').forEach(function(i){
        parts.push(i.dataset.label+': '+i.value.replace(/-/g,' '));
      });
      var msg='Ola! Tenho interesse no produto: '+wa.dataset.title;
      if(parts.length)msg+=' ('+parts.join(', ')+')';
      wa.href='https://wa.me/'+wa.dataset.phone+'?text='+encodeURIComponent(msg);
    }
    document.querySelectorAll('.opt input').forEach(function(i){i.addEventListener('change',build);});
    build();
  }
})();
"""


def head(title, desc, canonical, og_image):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}" />
<link rel="canonical" href="{canonical}" />
<meta property="og:locale" content="pt_BR" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:site_name" content="Loja Casa do Shake" />
<meta property="og:image" content="{og_image}" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" />
<link rel="icon" href="/assets/favicon-192.png" sizes="192x192" />
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css?family=Montserrat:400,600&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/css/style.css" />
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="/"><img src="/assets/logo-600.png" width="60" height="60" alt="Casa do Shake" /><span>Loja Casa do Shake</span></a>
    <a class="head-wa" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">WhatsApp</a>
  </div>
</header>
"""


FOOTER = f"""<footer class="site">
  <div class="wrap">
    <p>Casa do Shake &middot; Cabo Frio &middot; <a href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">WhatsApp</a> &middot; <a href="https://www.instagram.com/casadoshake.cabofrio/" target="_blank" rel="noopener">Instagram</a></p>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def build_home(data):
    cats = [c for c in data["categories"] if c["count_published"] > 0]
    cats.sort(key=lambda c: (-c["count_published"], c["name"]))
    chips = ['<a class="chip active" data-cat="all" href="#all">Todos</a>']
    for c in cats:
        chips.append(f'<a class="chip" data-cat="{esc(c["slug"])}" href="#{esc(c["slug"])}">{esc(c["name"])}</a>')

    cards = []
    for p in data["products"]:
        img = p["img"][0] if p.get("img") else None
        imgtag = ""
        if img:
            imgtag = (f'<img src="/{img["thumb"]}" width="{img["thumb_w"]}" height="{img["thumb_h"]}" '
                      f'alt="{esc(p["title"])}" loading="lazy" decoding="async" />')
        cat_slugs = " ".join(c["slug"] for c in p["categories"])
        cat_names = " &middot; ".join(esc(c["name"]) for c in p["categories"])
        cards.append(f"""  <article class="card" data-title="{esc(p['title'].lower())}" data-cats="{esc(cat_slugs)}">
    <a class="thumb" href="/produto/{esc(p['slug'])}.html">{imgtag}</a>
    <div class="body">
      <div class="cats">{cat_names}</div>
      <h3><a href="/produto/{esc(p['slug'])}.html" style="color:inherit;text-decoration:none">{esc(p['title'])}</a></h3>
      <a class="btn" href="/produto/{esc(p['slug'])}.html">Ver produto</a>
    </div>
  </article>""")

    body = f"""{head("Loja Casa do Shake - Catálogo", "Catálogo de produtos Casa do Shake - Cabo Frio. Shakes, chás, proteínas e mais. Peça pelo WhatsApp.", SITE + "/", SITE + "/assets/logo.png")}
<section class="hero">
  <div class="wrap">
    <img class="logo" src="/assets/logo-600.png" width="600" height="600" alt="Casa do Shake" />
    <h1>Catálogo de Produtos</h1>
    <p>Escolha seu produto e fale com a gente pelo WhatsApp.</p>
  </div>
</section>
<main>
  <div class="wrap">
    <h2 class="sr-only">Produtos</h2>
    <div class="toolbar">
      <input class="search" id="q" type="search" placeholder="Buscar produto..." aria-label="Buscar produto" />
      <div class="chips">{''.join(chips)}</div>
    </div>
    <div class="grid" id="grid">
{chr(10).join(cards)}
    </div>
    <p class="empty" id="empty" hidden>Nenhum produto encontrado.</p>
  </div>
</main>
{FOOTER}"""
    return body


def build_product(p, data, cat_by_slug):
    imgs = p.get("img") or []
    main = imgs[0] if imgs else None
    og_image = SITE + "/" + main["large"] if main else SITE + "/assets/logo.png"

    # galeria
    gallery = ""
    if imgs:
        maintag = (f'<img id="mainimg" src="/{main["large"]}" width="{main["large_w"]}" '
                   f'height="{main["large_h"]}" alt="{esc(p["title"])}" />')
        thumbs = ""
        if len(imgs) > 1:
            timgs = []
            for i, im in enumerate(imgs):
                cls = "active" if i == 0 else ""
                timgs.append(f'<img class="{cls}" src="/{im["thumb"]}" width="{im["thumb_w"]}" height="{im["thumb_h"]}" '
                             f'data-full="/{im["large"]}" alt="{esc(p["title"])} {i+1}" loading="lazy" />')
            thumbs = f'<div class="thumbs">{"".join(timgs)}</div>'
        gallery = f'<div class="gallery"><div class="main">{maintag}</div>{thumbs}</div>'

    # categorias
    catlinks = " ".join(f'<a href="/#{esc(c["slug"])}">{esc(c["name"])}</a>' for c in p["categories"])

    # variacoes
    opt_html = ""
    if p.get("variations"):
        by_attr = {}
        for v in p["variations"]:
            for k, val in v["attrs"].items():
                by_attr.setdefault(k, [])
                if val and val not in by_attr[k]:
                    by_attr[k].append(val)
        blocks = []
        for k in sorted(by_attr):
            choices = []
            for idx, val in enumerate(sorted(by_attr[k])):
                checked = "checked" if idx == 0 else ""
                choices.append(f'<label><input type="radio" name="{esc(k)}" value="{esc(val)}" '
                               f'data-label="{esc(attr_label(k))}" {checked} /><span>{esc(opt_label(val))}</span></label>')
            blocks.append(f'<div class="opt"><h4>{esc(attr_label(k))}</h4><div class="choices">{"".join(choices)}</div></div>')
        opt_html = "".join(blocks)

    # secoes ACF
    acf = p.get("acf") or {}
    secs = []
    if acf.get("visao_geral"):
        secs.append(f'<section><h2>Visão geral</h2><p>{rich(acf["visao_geral"])}</p></section>')
    if acf.get("beneficios"):
        secs.append(f'<section><h2>Benefícios e funcionalidades</h2><p>{rich(acf["beneficios"])}</p></section>')
    if acf.get("modo_de_uso"):
        secs.append(f'<section><h2>Modo de uso</h2><p>{rich(acf["modo_de_uso"])}</p></section>')
    if acf.get("nutricional"):
        secs.append(f'<section><h2>Informação nutricional</h2><p>{rich(acf["nutricional"])}</p></section>')
    sections = f'<div class="sections">{"".join(secs)}</div>' if secs else ""

    body = f"""{head(p['title'] + " - Loja Casa do Shake", (p.get('excerpt') or p['title'])[:160], f"{SITE}/produto/{p['slug']}.html", og_image)}
<main>
  <div class="wrap">
    <p class="breadcrumb"><a href="/">Catálogo</a> &rsaquo; {esc(p['title'])}</p>
    <div class="product">
      {gallery}
      <div class="pinfo">
        <h1>{esc(p['title'])}</h1>
        <div class="cats">{catlinks}</div>
        {opt_html}
        <a class="btn btn-wa" id="wa" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener"
           data-phone="{WHATSAPP}" data-title="{esc(p['title'])}">Falar no WhatsApp</a>
      </div>
    </div>
    {sections}
  </div>
</main>
{FOOTER}"""
    return body


def build_404():
    return f"""{head("Página não encontrada - Loja Casa do Shake", "Página não encontrada.", SITE + "/404.html", SITE + "/assets/logo.png")}
<main>
  <div class="wrap" style="text-align:center;padding:60px 0">
    <h1>Página não encontrada</h1>
    <p>O produto ou página que você procura não existe.</p>
    <p><a class="btn" href="/">Voltar ao catálogo</a></p>
  </div>
</main>
{FOOTER}"""


def main():
    with open(CATALOG, encoding="utf-8") as f:
        data = json.load(f)

    cat_by_slug = {c["slug"]: c for c in data["categories"]}

    os.makedirs(os.path.join(ROOT, "produto"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets", "js"), exist_ok=True)

    with open(os.path.join(ROOT, "assets", "css", "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    with open(os.path.join(ROOT, "assets", "js", "site.js"), "w", encoding="utf-8") as f:
        f.write(JS)

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_home(data))

    n = 0
    urls = [SITE + "/"]
    for p in data["products"]:
        with open(os.path.join(ROOT, "produto", p["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(build_product(p, data, cat_by_slug))
        urls.append(f"{SITE}/produto/{p['slug']}.html")
        n += 1

    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as f:
        f.write(build_404())

    with open(os.path.join(ROOT, "CNAME"), "w", encoding="utf-8") as f:
        f.write(DOMAIN + "\n")
    with open(os.path.join(ROOT, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")

    today = date.today().isoformat()
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            f.write(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n")
        f.write("</urlset>\n")

    print("index.html gerado | produtos:", n, "| urls no sitemap:", len(urls))


if __name__ == "__main__":
    main()
