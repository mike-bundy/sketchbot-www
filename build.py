#!/usr/bin/env python3
"""Sketchbot Studios — static site generator (stdlib only).

Reads:  content/*.json, archive/projects.json, archive/posts.json, archive/raw/json/blog__*.json
Writes: site/**  (open site/index.html or `python3 -m http.server -d site`)
"""
import json, os, re, html, datetime, shutil, glob, pathlib

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / 'site'
BASE_URL = os.environ.get('SITE_BASE_URL', 'https://www.sketchbot.tv').rstrip('/')
BASE_PATH = re.sub(r'^https?://[^/]+', '', BASE_URL)  # '' at the root, '/sketchbot-www' on a project Pages URL
NOW = datetime.date.today().isoformat()
ASSET_V = str(int(max(os.path.getmtime(ROOT / f) for f in ('site/assets/css/site.css', 'site/assets/js/site.js', 'site/assets/js/spatial.js'))))

projects_cur = json.load(open(ROOT / 'content/projects.json'))
archive_projects = json.load(open(ROOT / 'archive/projects.json'))
posts = json.load(open(ROOT / 'archive/posts.json'))
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location('newposts', ROOT / 'content/posts_2016_2026.py'); _mod = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_mod)
site_cfg = json.load(open(ROOT / 'content/site.json'))

# ----------------------------------------------------------------------------- helpers
def esc(s): return html.escape(s or '', quote=True)

def img(file, size='full'):
    """archive image path -> derived web path (root-relative)."""
    if not file: return ''
    b = os.path.basename(file); base, ext = os.path.splitext(b)
    ext = '.png' if ext.lower() == '.png' else '.jpg'
    return f'/assets/img/{size}/{base}{ext}'

OG_W, OG_H = 1200, 630
_og_cache = {}
def og_card(web_path):
    """Return a 1200x630 share-card path for a site image (root-relative web path). Falls back to the image itself."""
    if not web_path or not web_path.startswith('/assets/img/'): return web_path
    if web_path in _og_cache: return _og_cache[web_path]
    src = SITE / web_path.lstrip('/'); name = os.path.splitext(os.path.basename(web_path))[0] + '.jpg'
    out = SITE / 'assets/og' / name; out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() and src.exists() and shutil.which('sips'):
        import subprocess
        info = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', str(src)], capture_output=True, text=True).stdout
        try:
            w = int(re.search(r'pixelWidth: (\d+)', info).group(1)); h = int(re.search(r'pixelHeight: (\d+)', info).group(1))
        except Exception: w, h = 0, 0
        if w and h:
            tmp = out.with_suffix('.tmp.jpg')
            # scale so the image covers 1200x630, then centre-crop
            if w / h >= OG_W / OG_H: args = ['--resampleHeight', str(OG_H)]
            else: args = ['--resampleWidth', str(OG_W)]
            subprocess.run(['sips', *args, '-s', 'format', 'jpeg', '-s', 'formatOptions', '85', str(src), '--out', str(tmp)], capture_output=True)
            subprocess.run(['sips', '-c', str(OG_H), str(OG_W), str(tmp), '--out', str(out)], capture_output=True)
            tmp.unlink(missing_ok=True)
    _og_cache[web_path] = f'/assets/og/{name}' if out.exists() else web_path
    return _og_cache[web_path]

SITE_KEYWORDS = ['Sketchbot', 'Sketchbot Studios', 'Steve Talkowski', 'character design', '3D animation', 'robot designer toy', 'Apple Vision Pro', 'visionOS', 'spatial computing', 'USDZ', 'Maya', 'ZBrush', 'KeyShot', 'Los Angeles 3D artist']

def slugify(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-'); return s[:80] or 'post'

def write(path, content):
    if BASE_PATH:
        # Rewrite root-relative URLs for a sub-path deployment (GitHub project Pages preview).
        content = re.sub(r'((?:href|src|data-usdz|data-poster|data-env|data-backdrop|data-audio|data-full|content|start_url)=\")/(?!/)', r'\1' + BASE_PATH + '/', content)
        content = re.sub(r'(srcset=\"[^\"]*?)(?<=[\", ])/(?!/)', lambda m: m.group(1) + BASE_PATH + '/', content)
        content = re.sub(r'(srcset=\"[^\"]*?, )/(?!/)', r'\1' + BASE_PATH + '/', content)
        content = content.replace('"start_url": "/"', f'"start_url": "{BASE_PATH}/"').replace("'/assets/", f"'{BASE_PATH}/assets/")
        content = content.replace('"href_matches":"/*"', f'"href_matches":"{BASE_PATH}/*"').replace('"href_matches":"/*\\\\?*"', f'"href_matches":"{BASE_PATH}/*\\\\?*"')
    p = SITE / path.lstrip('/'); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding='utf-8')

def date_of(ms): return datetime.datetime.utcfromtimestamp(ms / 1000) if ms else None

ICONS = {
  'cube': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 3 3 7.5v9L12 21l9-4.5v-9L12 3Z"/><path d="M3 7.5 12 12l9-4.5M12 12v9"/></svg>',
  'hand': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 13V5.5a1.5 1.5 0 0 1 3 0V12M11 5.5v-1a1.5 1.5 0 0 1 3 0V12M14 6a1.5 1.5 0 0 1 3 0v6M17 8.5a1.5 1.5 0 0 1 3 0V15a6 6 0 0 1-6 6h-2a6 6 0 0 1-5-2.7L4.2 14A1.6 1.6 0 0 1 6.8 12l1.2 1.6"/></svg>',
  'eye': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>',
  'layers': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/></svg>',
  'users': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.5a3.5 3.5 0 0 1 0 7M21.5 20a6.5 6.5 0 0 0-4.5-6.2"/></svg>',
  'box': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 9h18M9 21V9"/></svg>',
  'spark': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 2l1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8L12 2ZM19 16l.9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9L19 16Z"/></svg>',
  'globe': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>',
  'pen': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="m4 20 4-1 11-11-3-3L5 16l-1 4Z"/><path d="m13 8 3 3"/></svg>',
  'play': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>',
  'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
  'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m3 7 9 6 9-6"/></svg>',
  'radial': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="2.2"/><circle cx="12" cy="4" r="1.8"/><circle cx="19" cy="8" r="1.8"/><circle cx="19" cy="16" r="1.8"/><circle cx="12" cy="20" r="1.8"/><circle cx="5" cy="16" r="1.8"/><circle cx="5" cy="8" r="1.8"/></svg>',
  'wand': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="m4 20 11-11M15 4l.8 1.7 1.7.8-1.7.8L15 9l-.8-1.7-1.7-.8 1.7-.8L15 4ZM20 11l.5 1 1 .5-1 .5-.5 1-.5-1-1-.5 1-.5.5-1Z"/></svg>',
  'flask': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3"/></svg>',
}
def ic(n): return ICONS[n]

SB_MARK = '''<svg viewBox="0 0 64 64" aria-hidden="true"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffb457"/><stop offset="1" stop-color="#f5921f"/></linearGradient></defs><rect x="8" y="10" width="48" height="44" rx="12" fill="url(#g)"/><circle cx="32" cy="30" r="13" fill="#fff"/><circle cx="32" cy="30" r="7" fill="#0184ff"/><circle cx="32" cy="30" r="3.2" fill="#062a4a"/><circle cx="29.5" cy="27.5" r="1.6" fill="#fff"/><rect x="24" y="48" width="16" height="3" rx="1.5" fill="#1a0d00" opacity=".45"/></svg>'''

SOCIAL = site_cfg['social']

# ----------------------------------------------------------------------------- layout
def layout(*, title, desc, body, path, section='', og_image=None, jsonld=None, extra_head='', wide=True, kind='website', keywords=None, og_alt=None, published=None, modified=None):
    nav = ''
    for n in site_cfg['nav']:
        cur = ' aria-current="page"' if n['key'] == section else ''
        cls = ''
        nav += f'<a href="{n["href"]}"{cur}{cls}>{n["label"]}</a>'
    og = og_card(og_image) if og_image else '/assets/og/default.jpg'
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ''
    canonical = BASE_URL + path
    kw = ', '.join(dict.fromkeys([*(keywords or []), *SITE_KEYWORDS]))
    og_alt = og_alt or title
    og_dims = '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">' if og.startswith('/assets/og/') else ''
    og_type = '<meta property="og:image:type" content="image/jpeg">' if og.endswith('.jpg') else ('<meta property="og:image:type" content="image/png">' if og.endswith('.png') else '')
    article_meta = ''
    if kind == 'article':
        article_meta = '<meta property="article:author" content="Steve Talkowski">' + (f'<meta property="article:published_time" content="{published}">' if published else '') + (f'<meta property="article:modified_time" content="{modified}">' if modified else '')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="keywords" content="{esc(kw)}">
<meta name="author" content="Steve Talkowski">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#0b0b0e" media="(prefers-color-scheme: dark)"><meta name="theme-color" content="#f6f3ee" media="(prefers-color-scheme: light)">
<meta property="og:site_name" content="Sketchbot Studios"><meta property="og:locale" content="en_US"><meta property="og:type" content="{kind}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE_URL}{og}"><meta property="og:image:secure_url" content="{BASE_URL}{og}">{og_dims}{og_type}<meta property="og:image:alt" content="{esc(og_alt)}">{article_meta}
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@stevetalkowski"><meta name="twitter:creator" content="@stevetalkowski"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{BASE_URL}{og}"><meta name="twitter:image:alt" content="{esc(og_alt)}">
<link rel="icon" href="/assets/brand/favicon-96.png" type="image/png" sizes="96x96"><link rel="icon" href="/assets/brand/favicon-48.png" type="image/png" sizes="48x48"><link rel="icon" href="/assets/brand/favicon-32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Sketchbot Studios News" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_V}">
<script type="importmap">{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.186.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.186.0/examples/jsm/"}}}}</script>
<script type="speculationrules">{{"prerender":[{{"where":{{"and":[{{"href_matches":"/*"}},{{"not":{{"href_matches":"/*\\\\?*"}}}}]}},"eagerness":"moderate"}}]}}</script>
{ld}{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap"><div class="bar">
  <a class="brand" href="/" aria-label="Sketchbot Studios home"><img src="/assets/brand/logo-64.png" srcset="/assets/brand/logo-64.png 1x, /assets/brand/logo-round.png 2x" width="30" height="30" alt=""><span>Sketchbot<small>Studios</small></span></a>
  <button class="nav-toggle" aria-expanded="false" aria-controls="nav" aria-label="Menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  <nav class="nav" id="nav" aria-label="Primary">{nav}
    <button class="theme-toggle" aria-label="Toggle light/dark theme"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>
  </nav>
</div></div></header>
<main id="main">
{body}
</main>
<footer class="site-footer"><div class="wrap">
  <div class="cols">
    <div><h4>Sketchbot Studios</h4><p class="small">Design. Create. Animate.<br>Now in your space.</p><p class="small mt-1">Los Angeles, CA<br><a href="mailto:steve@sketchbot.tv">steve@sketchbot.tv</a></p></div>
    <div><h4>Spatial</h4><ul role="list"><li><a href="/spatial/">Spatial computing</a></li><li><a href="/spatial/quads/">Quads for Vision Pro</a></li><li><a href="/spatial/environments/">Immersive environments</a></li><li><a href="/spatial/assets/">USDZ asset pipeline</a></li><li><a href="/spatial/radial-menu/">Radial Menu (open source)</a></li><li><a href="/spatial/services/">Services</a></li></ul></div>
    <div><h4>Studio</h4><ul role="list"><li><a href="/work/">Work</a></li><li><a href="/reel/">Demo reel</a></li><li><a href="/about/">About</a></li><li><a href="/news/">News</a></li><li><a href="/shop/">Shop</a></li><li><a href="/contact/">Contact</a></li></ul></div>
    <div><h4>Elsewhere</h4><ul role="list">{''.join(f'<li><a href="{s["href"]}" rel="me noopener" target="_blank">{s["label"]}</a></li>' for s in SOCIAL)}</ul></div>
  </div>
  <div class="legal"><span>© <span data-year>2026</span> Sketchbot Studios · Steve Talkowski. Sketchbot™ and the Eye Pilots are trademarks of Sketchbot Studios.</span><span><a href="/feed.xml">RSS</a> · <a href="/llms.txt">llms.txt</a> · <a href="/sitemap.xml">Sitemap</a></span></div>
</div></footer>
<script src="/assets/js/site.js?v={ASSET_V}" defer></script>
<script type="module" src="/assets/js/spatial.js?v={ASSET_V}"></script>
</body>
</html>'''

# ----------------------------------------------------------------------------- data prep
by_slug = {}
for p in projects_cur:
    a = archive_projects[p['src']]
    items = [i for i in a['items'] if i.get('file')]
    p['items'] = items
    p['hero_img'] = items[p.get('hero', 0)] if items else None
    p['url'] = f'/work/{p["slug"]}/'
    by_slug[p['slug']] = p

def _render_new_post(np):
    parts = []; first_img = None
    for blk in np['blocks']:
        if isinstance(blk, str): parts.append(f'<p>{blk}</p>'); continue
        kind = blk[0]
        if kind == 'img':
            it = archive_projects[blk[1]]['items'][blk[2]]; src = img(it['file']); cap = blk[3]
            parts.append(f'<figure><img src="{src}" width="{it.get("w") or 1600}" height="{it.get("h") or 900}" alt="{esc(cap)}" loading="lazy" decoding="async"><figcaption class="dim small">{esc(cap)}</figcaption></figure>')
            first_img = first_img or it['file']
        elif kind == 'url':
            parts.append(f'<figure><img src="{blk[1]}" alt="{esc(blk[2])}" loading="lazy" decoding="async"><figcaption class="dim small">{esc(blk[2])}</figcaption></figure>')
    text = re.sub(r'<[^>]+>', '', next(x for x in np['blocks'] if isinstance(x, str)))
    dt = datetime.datetime.strptime(np['date'], '%Y-%m-%d')
    return {'title': np['title'], 'url': BASE_URL + f'/news/{slugify(np["title"])}/', 'date': int(dt.timestamp() * 1000), 'excerpt': text[:400], 'body': text, 'image': first_img, 'tags': np['tags'], 'categories': [], 'html': ''.join(parts), 'new': True}

def _clean_excerpt(t):
    t = re.sub(r'#block-[\w-]+[^{]*\{[^}]*\}', ' ', t or ''); t = re.sub(r'@media[^{]*\{.*', ' ', t, flags=re.S); t = re.sub(r'[#.][\w-]+\s*\{[^}]*\}', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()
for _p in posts: _p['excerpt'] = _clean_excerpt(_p['excerpt']) or _clean_excerpt(_p['body'])[:300]
for _np in _mod.POSTS: posts.append(_render_new_post(_np))
posts.sort(key=lambda p: p['date'] or 0, reverse=True)
_seen = {}
for _p in posts:
    _p['slug'] = slugify(_p['title']); _p['dt'] = date_of(_p['date'])
    if _p['slug'] in _seen: _seen[_p['slug']] += 1; _p['slug'] += f'-{_seen[_p["slug"]]}'
    else: _seen[_p['slug']] = 1

def picture(item, cls='', sizes='(max-width: 700px) 100vw, 50vw', lazy=True, alt=None):
    if not item: return ''
    w, h = item.get('w') or 4, item.get('h') or 3
    a = esc(alt if alt is not None else (item.get('caption') or item.get('alt') or ''))
    load = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ''
    return (f'<img src="{img(item["file"])}" srcset="{img(item["file"],"thumb")} 720w, {img(item["file"])} 1800w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{a}"{load}{c}>')

def work_card(p, wide=False, eager=False):
    it = p['hero_img']
    badge = '<span class="chip chip--orange badge">Spatial</span>' if p.get('spatial') else ''
    return (f'<a class="work-card{" work-card--wide" if wide else ""} reveal" href="{p["url"]}" data-cat="{esc(p["category"])}|{"Spatial" if p.get("spatial") else ""}">'
            f'{picture(it, sizes="(max-width: 700px) 100vw, 33vw", alt=p["title"], lazy=not eager)}{badge}'
            f'<span class="meta"><strong>{esc(p["title"])}</strong><span>{esc(p["category"])} · {esc(p["year"])}</span></span></a>')

def gallery(items, title):
    figs = []
    for i, it in enumerate(items):
        w, h = it.get('w') or 4, it.get('h') or 3
        land = 'landscape' if w / h > 1.45 else ''
        cap = f'<figcaption>{esc(it["caption"])}</figcaption>' if it.get('caption') else ''
        figs.append(f'<figure class="{land}" style="--ar:{w}/{h}" data-full="{img(it["file"])}">'
                    f'<img src="{img(it["file"],"thumb")}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{esc(it.get("caption") or it.get("alt") or f"{title} — image {i+1}")}">{cap}</figure>')
    return f'<div class="gallery">{"".join(figs)}</div>'

def stage(usdz, poster, name, env='', cls='', poster_alt=''):
    e = f' data-env="{env}"' if env else ''
    return (f'<div class="stage {cls}" data-usdz="{usdz}" data-poster="{poster}" data-name="{esc(name)}"{e}>'
            f'<img class="poster" src="{poster}" alt="{esc(poster_alt or name)}" loading="lazy">'
            f'<div class="hud"><span class="status" data-tier="poster">{esc(name)}</span></div></div>')

def section_head(eyebrow, h2, p='', cls='', eb_cls=''):
    sub = f'<p class="muted" style="font-size:1.1rem">{p}</p>' if p else ''
    return f'<div class="stack reveal {cls}" style="--stack:.6rem"><p class="eyebrow {eb_cls}">{eyebrow}</p><h2>{h2}</h2>{sub}</div>'

def crumbs(*pairs):
    lis = ''.join(f'<li><a href="{h}">{esc(t)}</a></li>' if h else f'<li>{esc(t)}</li>' for t, h in pairs)
    return f'<nav aria-label="Breadcrumb"><ol class="crumbs" role="list">{lis}</ol></nav>'

# ----------------------------------------------------------------------------- HOME
def page_home():
    hero = {'file': 'archive/images/5d625869_DAY_04_KS_V2_for_coverPage.jpg', 'w': 2500, 'h': 1668, 'caption': ''}  # the original sketchbot.tv cover banner (placeholder until the new asset lands)
    featured = [by_slug[s] for s in ['tron-immersive', 'afternoon-at-the-museum', 'autodesk-maya-m4y4', 'sketchbot', 'adobe-vr-bot', 'scoob-concept-art', 'jammin-alpacas', 'gibco-cells', 'keyshot-6-avatar']]
    cards = ''.join(work_card(p, wide=(i == 0), eager=(i < 3)) for i, p in enumerate(featured))
    beat_items = [
        ('Dream it.', 'Every robot starts in the sketchbook.', '/work/', 'archive/images/0598d387_sketchbotPilotClipboard.png', 'Eye Pilot with a clipboard'),
        ('Build it.', 'Modeled, sculpted and 3D printed.', '/work/sketchbot/', 'archive/images/0e67720c_image-asset.jpg', 'A freshly printed OctoBot in the palm of a hand'),
        ('Grow it.', 'One robot became a whole world.', '/news/', 'archive/images/d1d128da_image.jpg', 'ResinBot prototype at the printer'),
        ('Sell it.', 'Designer toys, prints and editions.', '/shop/', 'archive/images/9464698a_Sketchbot_V1_w_Box.jpg', 'Sketchbot V1 with its box'),
        ('Space it.', 'Now living on Apple Vision Pro.', '/spatial/', 'archive/images/e1be299a_VR_eyePilot.0002.jpg', 'Eye Pilot wearing a VR headset'),
    ]
    beats = ''.join(f'<li><a href="{href}" class="beat{" beat--o" if i == 4 else ""}"><img src="{img(f)}" srcset="{img(f,"thumb")} 720w, {img(f)} 1800w" sizes="(max-width:700px) 50vw, 20vw" alt="{esc(alt)}" decoding="async"><span class="beat-text"><strong>{word}</strong><span>{line}</span></span></a></li>' for i, (word, line, href, f, alt) in enumerate(beat_items))
    latest = posts[:5]
    def _short(t, n=150):
        t = t.strip()
        if len(t) <= n: return t
        cut = t[:n].rsplit(' ', 1)[0].rstrip(',;:')
        return cut + '…'
    news = ''.join(f'<a class="post-row" href="/news/{p["slug"]}/"><time datetime="{p["dt"].date().isoformat()}">{p["dt"].strftime("%d %b %Y")}</time><span><strong>{esc(p["title"])}</strong><p>{esc(_short(p["excerpt"]))}</p></span></a>' for p in latest)
    groups = site_cfg['client_groups']
    def lane(label, names, rev=False):
        items = ''.join(f'<li>{esc(n)}</li>' for n in names + names)
        return f'<div class="lane{" lane--rev" if rev else ""}"><span class="lane-label">{esc(label)}</span><div class="marquee" aria-hidden="true"><ul role="list">{items}</ul></div></div>'
    lanes = ''.join(lane(g['label'], g['names'], rev=(i % 2 == 1)) for i, g in enumerate(groups))
    body = f'''
<section class="hero hero--cover">
  <div class="hero-media">{picture(hero, lazy=False, sizes="100vw", alt="A Sketchbot explorer robot inspecting a pinecone on a sunny path")}</div>
  <div class="wrap hero-inner">
    <span class="chip chip--orange"><span class="dot"></span>Now building for Apple Vision Pro</span>
    <h1>Design. Create. Animate.<br><span class="o">Now in your space.</span></h1>
    <p class="lede">Sketchbot Studios is the character-driven 3D studio of Steve Talkowski: thirty years of animation for brands and film, a designer-toy icon, and now professional work for Apple Vision Pro.</p>
    <div class="cluster">
      <a class="btn btn--orange" href="/spatial/">Spatial computing {ic('arrow')}</a>
      <a class="btn btn--ghost" href="/work/">See the work</a>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <ol class="beats" role="list" aria-label="Dream it. Build it. Grow it. Sell it. Space it.">{beats}</ol>
  </div>
</section>

<section class="section">
  <div class="wrap">
    {section_head('Latest', 'What’s new from <span class="o">the studio</span>', 'Fresh from the workbench: apps, environments and services.', eb_cls='eyebrow--orange')}
    <div class="grid grid--3 mt-3">
      <a class="card card--pad card--blue reveal" href="/spatial/quads/"><div class="icon">{ic('cube')}</div><h3>Quads</h3><p>A spatial box-modeler for Apple Vision Pro. Hands-first, Logitech Muse stylus support, Catmull-Clark subdivision, sculpt, remesh, USDZ export and SharePlay co-modeling.</p><p class="mt-1 b" style="font-weight:700">Coming soon to the App Store →</p></a>
      <a class="card card--pad card--orange reveal" href="/spatial/environments/"><div class="icon">{ic('globe')}</div><h3>Immersive web environments</h3><p>Websites you can step into. TRON: The Grid and the Backrooms are full-immersion Safari environments with spatial audio, built from USDZ.</p><p class="mt-1 o" style="font-weight:700">Enter The Grid →</p></a>
      <a class="card card--pad card--orange reveal" href="/spatial/services/"><div class="icon">{ic('wand')}</div><h3>Studio services</h3><p>Spatial character and mascot design, visionOS app design and prototyping, USDZ and Reality Composer Pro pipelines, spatial UX consulting.</p><p class="mt-1 o" style="font-weight:700">Work with the studio →</p></a>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap"><p class="statement reveal">Characters that <em>live</em> in your room, not behind glass. Everything the studio has learned about appeal, weight and timing, brought to <span class="o">spatial computing</span>.</p></div>
</section>

<section class="section">
  <div class="wrap">
    <div class="cluster" style="justify-content:space-between;align-items:end">{section_head('Selected work', 'Robots, mascots and worlds')}<a class="btn btn--ghost" href="/work/">All projects {ic('arrow')}</a></div>
    <div class="work-grid mt-3">{cards}</div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap clients">
    <div class="clients-intro reveal">
      <p class="eyebrow eyebrow--orange">Trusted by</p>
      <h2>Thirty years of<br>brands, studios<br>and film.</h2>
      <dl class="stats">
        <div><dt>Years in animation</dt><dd>30<span>+</span></dd></div>
        <div><dt>National spots</dt><dd>100<span>s</span></dd></div>
        <div><dt>Feature films</dt><dd>4</dd></div>
        <div><dt>Academy Award short</dt><dd>1<span class="small-note">Bunny, 1998</span></dd></div>
      </dl>
    </div>
    <div class="lanes" aria-label="Clients and credits">
      {lanes}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="stack reveal">
      {section_head('About', 'Steve Talkowski')}
      <p class="muted">A veteran of the computer animation scene: Art Director, Animation Director, character designer and animator on hundreds of national brands, senior animator at Blue Sky Studios on <em>Ice Age</em>, <em>Joe's Apartment</em>, <em>Alien Resurrection</em> and the Academy Award-winning short <em>Bunny</em>. Founded Sketchbot Studios in 2008 and self-produced the Sketchbot designer toy.</p>
      <div class="cluster"><a class="btn" href="/about/">Read the story</a><a class="btn btn--ghost" href="/reel/">{ic('play')} Watch the reel</a></div>
    </div>
    <div class="rounded reveal" style="box-shadow:var(--shadow)">{picture(archive_projects['about']['items'][0], sizes="(max-width:700px) 100vw, 40vw", alt="Steve Talkowski in front of a giant Sketchbot eye")}</div>
  </div>
</section>

<section class="section">
  <div class="wrap grid grid--2" style="align-items:start">
    <div class="stack">{section_head('News', 'From the studio blog')}<div class="post-list mt-2">{news}</div><a class="btn btn--ghost mt-2" href="/news/">All {len(posts)} posts, back to 2007 {ic('arrow')}</a></div>
    <div class="contact-card reveal"><p class="eyebrow eyebrow--orange">Upcoming gig?</p><h2>Let's talk.</h2><p class="muted">Available for art direction, animation direction, character and concept design, 3D modeling, and spatial computing projects for Apple Vision Pro.</p><div class="cluster"><a class="btn btn--orange" href="mailto:steve@sketchbot.tv">{ic('mail')} steve@sketchbot.tv</a><a class="btn btn--ghost" href="/contact/">Contact page</a></div></div>
  </div>
</section>'''
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": BASE_URL + "/#org", "name": "Sketchbot Studios", "url": BASE_URL, "logo": BASE_URL + "/assets/quads/icon-front.png", "founder": {"@id": BASE_URL + "/#steve"}, "sameAs": [s['href'] for s in SOCIAL], "email": "steve@sketchbot.tv", "address": {"@type": "PostalAddress", "addressLocality": "Los Angeles", "addressRegion": "CA", "addressCountry": "US"}},
        {"@type": "Person", "@id": BASE_URL + "/#steve", "name": "Steve Talkowski", "jobTitle": "Creative Director, Character Designer, Animator", "worksFor": {"@id": BASE_URL + "/#org"}, "url": BASE_URL + "/about/", "sameAs": [s['href'] for s in SOCIAL]},
        {"@type": "WebSite", "url": BASE_URL, "name": "Sketchbot Studios", "publisher": {"@id": BASE_URL + "/#org"}}]}
    write('index.html', layout(title='Sketchbot Studios — Design. Create. Animate. Now in your space.', desc='The character-driven 3D studio of Steve Talkowski: animation for brands and film, the Sketchbot designer toy, and professional tools and services for Apple Vision Pro.', body=body, path='/', section='home', og_image='/assets/img/full/9d642038_backrooms_SB-03.png', jsonld=ld, keywords=['3D character studio', 'animation director', 'designer toys', 'Vision Pro apps', 'Quads'], og_alt='Sketchbot in the Backrooms. Design. Create. Animate. Now in your space.'))

# ----------------------------------------------------------------------------- SPATIAL
SPATIAL_LD = {"@context": "https://schema.org", "@type": "Service", "name": "Sketchbot Studios spatial computing", "provider": {"@id": BASE_URL + "/#org"}, "serviceType": "Spatial computing design and development for Apple Vision Pro", "areaServed": "Worldwide", "url": BASE_URL + "/spatial/"}

def page_spatial():
    museum = by_slug['afternoon-at-the-museum']['items'][5]
    body = f'''
<section class="hero" style="min-height:min(80dvh,820px)">
  <div class="hero-media">{picture(museum, lazy=False, sizes="100vw", alt="Sketchbot characters in a neon-lit museum corridor")}</div>
  <div class="wrap hero-inner">
    {crumbs(('Home','/'),('Spatial',None))}
    <span class="chip chip--orange"><span class="dot"></span>Apple Vision Pro · visionOS 27</span>
    <h1>Spatial <span class="o">computing</span></h1>
    <p class="lede">Professional tools for work in spatial computing. A shipping modeling app, immersive web environments, production-grade USDZ pipelines and open-source UI, from a studio that has spent thirty years making characters people want to touch.</p>
    <div class="cluster"><a class="btn btn--orange" href="/spatial/quads/">Meet Quads {ic('arrow')}</a><a class="btn btn--ghost" href="/spatial/services/">Services</a><a class="btn btn--ghost" href="/spatial/environments/">Enter The Grid</a></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="spatial-hint mb-2" data-for="any">{ic('eye')}<span>This browser can show spatial content: 3D models on this site render natively and can be pinched out of the page.</span></div>
    {section_head('What the studio makes', 'Six ways in', 'Each is a real thing you can use today, not a slide.', eb_cls='eyebrow--orange')}
    <div class="grid grid--2 mt-3">
      <a class="card card--pad card--blue reveal" href="/spatial/quads/"><div class="icon">{ic('cube')}</div><h3>Quads — spatial box modeler</h3><p>Model with your hands in a mixed-immersion workspace. Object · Edit · Sculpt · Create modes, Catmull-Clark subdivision, voxel remesh, semi-sharp creases, symmetry, .quads projects, USDZ and OBJ export, SharePlay co-modeling and a community gallery at quads.vision.</p><span class="chip chip--blue mt-1">Coming soon</span></a>
      <a class="card card--pad card--orange reveal" href="/spatial/environments/"><div class="icon">{ic('globe')}</div><h3>Immersive website environments</h3><p>TRON: The Grid and the Backrooms: full-immersion Safari environments with looping spatial audio and inline stereoscopic models, using the <code>&lt;model&gt;</code> element and <code>requestImmersive()</code> on visionOS 27.</p><span class="chip mt-1">Live on this site</span></a>
      <a class="card card--pad card--orange reveal" href="/spatial/assets/"><div class="icon">{ic('layers')}</div><h3>USDZ asset production</h3><p>Characters, props, vehicles and whole environments authored in Maya and Substance, assembled in Reality Composer Pro, validated with usdchecker, and optimised for RealityKit, Quick Look and Safari. See the Recognizer and Tank in 3D right here.</p><span class="chip mt-1">Pipeline</span></a>
      <a class="card card--pad card--orange reveal" href="/spatial/radial-menu/"><div class="icon">{ic('radial')}</div><h3>Radial Menu — open source</h3><p>A tunable radial, vertical and horizontal menu for visionOS, macOS, iPadOS and iOS. One Swift file, no dependencies, plus the tuning app with live sliders, measure guides, synthesised audio cues and code export.</p><span class="chip mt-1">MIT · GitHub</span></a>
      <a class="card card--pad card--orange reveal" href="/spatial/services/"><div class="icon">{ic('wand')}</div><h3>Studio services</h3><p>Spatial character and mascot design, visionOS app design and prototyping, immersive brand environments, USDZ and RCP pipeline consulting, SharePlay experiences and team training.</p><span class="chip chip--orange mt-1">Available</span></a>
      <a class="card card--pad card--orange reveal" href="/spatial/lab/"><div class="icon">{ic('flask')}</div><h3>The Lab</h3><p>Experiments and research: the VR navigation sandbox, Muse stylus input probes, the Museum of Untold Possibilities, and notes from building for visionOS 27.</p><span class="chip mt-1">Research</span></a>
    </div>
  </div>
</section>

<section class="section section--tight"><div class="wrap">
  <p class="statement reveal">The hard part of spatial isn't the rendering. It's <em>appeal</em>: making a thing you want to reach for. That's what a character studio brings to a <span class="o">headset</span>.</p>
</div></section>

<section class="section"><div class="wrap">
  {section_head('How the studio works', 'From sketch to your room')}
  <ol class="steps mt-3" role="list">
    <li><h3>Sketch &amp; appeal</h3><p>Silhouette, proportion and personality on paper first. Spatial exposes bad design from every angle, so the drawing has to survive a walk-around.</p></li>
    <li><h3>Model in quads</h3><p>Clean, animatable topology in Maya or directly in Quads on the headset. Subdivision-ready, crease-tagged, real-world scale from the start.</p></li>
    <li><h3>Surface &amp; light</h3><p>Substance Painter PBR, baked where it counts, authored for RealityKit's PBR and Quick Look, not just an offline render.</p></li>
    <li><h3>Assemble &amp; ship</h3><p>Reality Composer Pro scenes, USDZ packaging that passes usdchecker, size budgets for Safari and the App Store, and a test pass on real hardware.</p></li>
  </ol>
</div></section>

<section class="section"><div class="wrap contact-card reveal">
  <p class="eyebrow eyebrow--orange">Bring a project</p><h2>Building for Vision Pro?</h2>
  <p class="muted">Whether you need a mascot that reads at arm's length, an app that feels native to visionOS, or a website your customers can step into, the studio is taking spatial work now.</p>
  <div class="cluster"><a class="btn btn--orange" href="mailto:steve@sketchbot.tv?subject=Spatial%20project">{ic('mail')} steve@sketchbot.tv</a><a class="btn btn--ghost" href="/spatial/services/">See services &amp; process</a></div>
</div></section>'''
    write('spatial/index.html', layout(title='Spatial computing — Sketchbot Studios', desc='Quads, immersive website environments, USDZ asset pipelines, an open-source radial menu and studio services for spatial computing on Apple Vision Pro.', body=body, path='/spatial/', section='spatial', og_image=img(museum['file']), jsonld=SPATIAL_LD, keywords=['Apple Vision Pro development', 'visionOS design', 'immersive website environments', 'USDZ pipeline', 'RealityKit', 'Reality Composer Pro', 'spatial UX'], og_alt='Sketchbot characters in a neon-lit museum corridor'))

def page_quads():
    feats = [
        ('hand', 'Hands first, stylus welcome', 'Model with gaze and pinch in a mixed-immersion workspace. The Logitech Muse stylus is tracked at 90 Hz through ARKit accessory tracking for precise placement, and never required.'),
        ('cube', 'Real box modeling', 'Vertices, edges, faces and n-gons with stable IDs. Extrude, inset, bevel, loop cut, slide, merge and bridge, with Maya-style Y-up tumble navigation.'),
        ('layers', 'Catmull-Clark subdivision', 'Live SubD preview with semi-sharp Pixar creases (0–10), bake to cage when you want to sculpt, and quads stay quads on export.'),
        ('wand', 'Sculpt & voxel remesh', 'Grab with falloff, push, flatten and smooth with your fingertips, then remesh to an all-quad surface and keep going. Clay flow: primitive → SubD → bake → sculpt → remesh.'),
        ('users', 'SharePlay co-modeling', 'Model together over FaceTime with Personas, live cursors, host-granted editing, late-joiner catch-up and conflict-free IDs per participant.'),
        ('box', 'Files that travel', '.quads projects open in place from Files. Export USDZ with subdivision baked for Quick Look, or OBJ with the editable cage. Share to the community gallery at quads.vision.'),
        ('radial', 'Native visionOS UI', 'Glass tool palette, radial hold-menus, channel box, outliner and a navCube. Windows for anything you type in, spatial panels for anything you glance at.'),
        ('globe', 'Universal links', 'Every shared model has a page at quads.vision/m/… that opens straight into the app, and the same USDZ renders in the browser.'),
    ]
    fhtml = ''.join(f'<div class="feature reveal"><div class="icon">{ic(i)}</div><div><h3>{t}</h3><p>{d}</p></div></div>' for i, t, d in feats)
    body = f'''<div class="accent-blue">
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Spatial','/spatial/'),('Quads',None))}
  <div class="split mt-2">
    <div class="stack" style="--stack:1.2rem">
      <span class="chip chip--blue"><span class="dot"></span>Coming soon to the App Store · visionOS 27</span>
      <h1>Quads</h1>
      <p class="lede" style="font-size:1.3rem;color:var(--fg-2)">A spatial box modeler for Apple Vision Pro. Model with your hands, subdivide with Catmull-Clark, sculpt, remesh, and export USDZ that looks right in Quick Look. Built for visionOS.</p>
      <div class="cluster"><a class="btn btn--blue" href="https://quads.vision" target="_blank" rel="noopener">quads.vision {ic('arrow')}</a><a class="btn btn--ghost" href="https://quads.vision/gallery" target="_blank" rel="noopener">Community gallery</a><a class="btn btn--ghost" href="mailto:steve@sketchbot.tv?subject=Quads%20TestFlight">Request TestFlight</a></div>
      <p class="dim small">Requires Apple Vision Pro. Logitech Muse stylus supported, not required.</p>
    </div>
    <div class="app-icon" role="img" aria-label="Quads app icon"><div class="coin"><div class="layer back"></div><div class="layer front"></div><div class="glare"></div></div></div>
  </div>
</div></section>

<section class="section section--tight"><div class="wrap">
  <div class="spatial-hint mb-2" data-for="model">{ic('eye')}<span>You're on Vision Pro: the logo below is a live spatial model. Pinch to orbit, or drag it out into your room.</span></div>
  <div class="grid grid--2">
    {stage('/assets/quads/QuadsLogo.usdz','/assets/quads/logo.png','Quads logo (USDZ)', cls='stage--tall')}
    {stage('/assets/quads/navCube.usdz','/assets/quads/icon-back.png','navCube — the in-app view cube', cls='stage--tall')}
  </div>
  <p class="dim small mt-1">Both models are the app's own USDZ assets, rendered natively in Safari on visionOS, with three.js elsewhere.</p>
</div></section>

<section class="section"><div class="wrap">
  {section_head('What it does', 'A real modeler, not a demo', 'Quads is an authoritative editable-topology model with stable IDs, deltas for undo and collaboration, creases and true symmetry. The headset is the viewport.', eb_cls='eyebrow--blue')}
  <div class="grid grid--2 mt-3" style="gap:2rem">{fhtml}</div>
</div></section>

<section class="section"><div class="wrap grid grid--2" style="align-items:start">
  <div class="card card--pad"><p class="eyebrow eyebrow--blue">Pipeline</p><h3>Interchange that DCCs can read</h3><p>USDZ export authors real <code>faceVertexCounts</code> with subdivision baked per object, UsdPreviewSurface materials and normals, and passes Pixar's <code>usdchecker</code>. Packages open in Maya, Blender, Reality Composer Pro and Quick Look. OBJ export carries the editable cage for round-trips.</p></div>
  <div class="card card--pad"><p class="eyebrow eyebrow--blue">Community</p><h3>Share to quads.vision</h3><p>Sign in with Apple, upload a model with one tap, and it appears in the gallery with a live USDZ preview. Browse Newest, Popular and Featured feeds, favourite models, and open any shared model straight into the app with a universal link.</p></div>
</div></section>

<section class="section"><div class="wrap">
  {section_head('Under the hood', 'Built for visionOS 27')}
  <div class="table-wrap mt-2"><table>
    <tr><th>Input</th><td>ARKit hand tracking, gaze + pinch, ARKit AccessoryTrackingProvider for Logitech Muse (buttons and pressure via GameController)</td></tr>
    <tr><th>Rendering</th><td>RealityKit, PhysicallyBasedMaterial and ShaderGraph materials, per-element cage entities with a CPU budget</td></tr>
    <tr><th>Geometry</th><td>Boundary representation with stable site-namespaced IDs; Catmull-Clark; surface-nets voxel remesh; semi-sharp creases; symmetry twins</td></tr>
    <tr><th>Collaboration</th><td>GroupActivities / SharePlay, reliable + unreliable messengers, Lamport-versioned deltas, spatial Persona seating</td></tr>
    <tr><th>Files</th><td>.quads (JSON, opens in place), USDZ (SuiteUSD / USDKit), OBJ; universal links from quads.vision</td></tr>
    <tr><th>Backend</th><td>Laravel API at quads.vision with Sign in with Apple, community feeds, favourites and a curated showcase</td></tr>
  </table></div>
</div></section>

<section class="section"><div class="wrap contact-card reveal"><p class="eyebrow eyebrow--orange">Beta</p><h2>Want early access?</h2><p class="muted">Quads is in its final stretch before the App Store. Modelers, educators and studios can request a TestFlight seat.</p><div class="cluster"><a class="btn btn--orange" href="mailto:steve@sketchbot.tv?subject=Quads%20TestFlight">{ic('mail')} Request TestFlight</a><a class="btn btn--ghost" href="https://quads.vision" target="_blank" rel="noopener">quads.vision</a></div></div></section></div>'''
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Quads", "applicationCategory": "DesignApplication", "operatingSystem": "visionOS 27", "url": "https://quads.vision", "author": {"@id": BASE_URL + "/#org"}, "description": "A spatial box modeler for Apple Vision Pro with Catmull-Clark subdivision, sculpting, voxel remesh, USDZ export and SharePlay co-modeling.", "offers": {"@type": "Offer", "availability": "https://schema.org/PreOrder", "price": "0", "priceCurrency": "USD"}}
    write('spatial/quads/index.html', layout(title='Quads — spatial box modeler for Apple Vision Pro — Sketchbot Studios', desc='Quads is a spatial box modeler for Apple Vision Pro: hands-first modeling, Logitech Muse stylus support, Catmull-Clark subdivision, sculpt and remesh, USDZ export and SharePlay co-modeling.', body=body, path='/spatial/quads/', section='spatial', og_image=img(by_slug['afternoon-at-the-museum']['items'][5]['file']), jsonld=ld, keywords=['Quads app', 'Vision Pro 3D modeling', 'box modeler', 'Catmull-Clark subdivision', 'Logitech Muse', 'SharePlay', 'USDZ export', 'quads.vision'], og_alt='Quads, a spatial box modeler for Apple Vision Pro'))

def page_environments():
    tron = by_slug['tron-immersive']; back = by_slug['backrooms']
    GH = 'https://stevetalkowski.github.io/spatial-assets/'
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Spatial','/spatial/'),('Immersive environments',None))}
  <div class="page-head"><p class="eyebrow eyebrow--orange">Immersive website environments</p><h1>Websites you can <span class="o">step into</span></h1><p>On Apple Vision Pro, Safari can replace your room with a scene served by the page. The studio builds those scenes: modeled, lit, scored and optimised as USDZ, wired with the <code>&lt;model&gt;</code> element and <code>requestImmersive()</code> on visionOS 27.</p></div>

  <div class="immersive reveal" data-backdrop="{GH}theGrid_full_V3.usdz" data-audio="/assets/spatial/recognizer_clip2.m4a" data-env="/assets/spatial/black_env.exr">
    <img class="bg" src="{img(tron['items'][2]['file'])}" alt="TRON light-cycle grid environment in Maya" loading="lazy">
    <div class="panel"><span class="chip chip--orange">TRON · The Grid</span><h2>Enter The Grid</h2><p>An homage to the 1982 original. Full immersion, looping Recognizer audio, a Digital Crown away from 360°. Press the button in Safari on Apple Vision Pro.</p>
    <div class="cluster"><button class="btn btn--orange" data-enter="Enter The Grid" data-exit="Exit The Grid">Enter The Grid</button><a class="btn btn--ghost" href="/work/tron-immersive/">Project page</a></div><p class="small" data-status style="color:rgba(255,255,255,.7)"></p></div>
  </div>

  <div class="spatial-hint mt-2" data-for="model">{ic('eye')}<span>Spatial rendering is active in this browser. The models below are true stereoscopic USDZ; pinch and drag them out of the page.</span></div>
  <div class="grid grid--2 mt-2">
    {stage(GH+'recognizer_V2_2k.usdz','/assets/spatial/recognizer_SS-03.png','Recognizer', env='/assets/spatial/black_env.exr', cls='stage--grid')}
    {stage(GH+'tank_V2_2k.usdz','/assets/spatial/tank_SS_V2.jpg','Tank', env='/assets/spatial/black_env.exr', cls='stage--grid')}
  </div>

  <div class="immersive mt-3 reveal" data-backdrop="{GH}backrooms_env_V4_optimized.usdz">
    <img class="bg" src="{img(back['items'][0]['file'])}" alt="Sketchbot in the Backrooms" loading="lazy">
    <div class="panel"><span class="chip chip--orange">Backrooms</span><h2>Lost in the Backrooms</h2><p>Sketchbot wanders the liminal office. A baked-lighting USDZ environment optimised to 20 MB for Safari, assembled in Reality Composer Pro.</p>
    <div class="cluster"><button class="btn btn--orange" data-enter="Enter the Backrooms" data-exit="Exit the Backrooms">Enter the Backrooms</button><a class="btn btn--ghost" href="/work/backrooms/">Project page</a></div><p class="small" data-status style="color:rgba(255,255,255,.7)"></p></div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  {section_head('How it works', 'One page, every device', 'The same HTML serves every visitor; the browser picks the richest experience it can render.', eb_cls='eyebrow--orange')}
  <div class="grid grid--2 mt-3">
    <div class="card card--pad"><p class="eyebrow eyebrow--orange">Apple Vision Pro · visionOS 27</p><h3>Full immersion from Safari</h3><p>The page holds a <code>&lt;model&gt;</code> pointed at the environment USDZ. When it's ready, a button calls <code>model.requestImmersive()</code>; Web Audio starts the loop; <code>onimmersivechange</code> keeps the UI honest. Inline models render stereoscopically and can be pinched out of the page.</p></div>
    <div class="card card--pad"><p class="eyebrow">Everywhere else</p><h3>Graceful flat</h3><p>Desktop and phones get the poster, the copy and three.js-rendered models. Nothing breaks, nothing is hidden behind a device check.</p></div>
  </div>
  <pre class="mt-3"><code>&lt;div class="immersive" data-backdrop="theGrid_full_V3.usdz" data-audio="recognizer_clip2.m4a"&gt;
  &lt;button data-enter="Enter The Grid" data-exit="Exit The Grid"&gt;Enter The Grid&lt;/button&gt;
&lt;/div&gt;
&lt;script type="module" src="/assets/js/spatial.js"&gt;&lt;/script&gt;</code></pre>
  <p class="dim small mt-1">The environment USDZ files are served from Steve's public <a href="https://github.com/stevetalkowski/spatial-assets" target="_blank" rel="noopener">spatial-assets</a> repository.</p>
</div></section>

<section class="section"><div class="wrap contact-card reveal"><p class="eyebrow eyebrow--orange">For brands</p><h2>Your showroom, in their living room.</h2><p class="muted">Product launches, film tie-ins, museum previews, retail concepts: an immersive environment is the most memorable thing a website can do on Vision Pro, and it ships as a single file.</p><div class="cluster"><a class="btn btn--orange" href="mailto:steve@sketchbot.tv?subject=Immersive%20environment">{ic('mail')} Commission an environment</a><a class="btn btn--ghost" href="/spatial/services/">Services</a></div></div></section>'''
    write('spatial/environments/index.html', layout(title='Immersive website environments for Apple Vision Pro — Sketchbot Studios', desc='Full-immersion Safari website environments built from USDZ: TRON The Grid and the Backrooms, with spatial audio and stereoscopic inline models, for visionOS 27.', body=body, path='/spatial/environments/', section='spatial', og_image='/assets/spatial/tank_SS_V2.jpg', jsonld=SPATIAL_LD, keywords=['website environment', 'Safari immersive', 'TRON', 'Backrooms', 'requestImmersive', 'model element', 'spatial audio'], og_alt='TRON Tank rendered on The Grid'))

def page_assets():
    GH = 'https://stevetalkowski.github.io/spatial-assets/'
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Spatial','/spatial/'),('USDZ asset pipeline',None))}
  <div class="page-head"><p class="eyebrow eyebrow--orange">USDZ asset production</p><h1>Assets that <span class="o">ship</span></h1><p>Characters, props, vehicles and environments authored for RealityKit, Quick Look, Safari and the App Store. Quads-clean topology, PBR surfacing, real-world scale, validated packaging.</p></div>
  <div class="spatial-hint mb-2" data-for="any">{ic('eye')}<span>Spatial preview active: these are the delivered USDZ files, not screenshots.</span></div>
  <div class="grid grid--2">
    {stage(GH+'recognizer_V2_2k.usdz','/assets/spatial/recognizer_SS-03.png','Recognizer · 2K textures · 0.5 MB', env='/assets/spatial/black_env.exr', cls='stage--grid')}
    {stage(GH+'tank_V2_2k.usdz','/assets/spatial/tank_SS_V2.jpg','Tank · 2K textures · 0.7 MB', env='/assets/spatial/black_env.exr', cls='stage--grid')}
    {stage('/assets/quads/demo.usdz','/assets/quads/icon-back.png','Quads export sample · UsdPreviewSurface')}
    {stage('/assets/quads/QuadsLogo.usdz','/assets/quads/logo.png','Quads logo · animated USDZ')}
  </div>
</div></section>

<section class="section"><div class="wrap">
  {section_head('Deliverables', 'What a spatial asset package contains', eb_cls='eyebrow--orange')}
  <div class="table-wrap mt-2"><table>
    <tr><th>Geometry</th><td>All-quad subdivision cages with creases, plus baked SubD meshes at the level each target needs. Named, grouped, pivots at the floor, metres.</td></tr>
    <tr><th>Materials</th><td>UsdPreviewSurface for Quick Look and Safari; OpenPBR / RealityKit PBR variants where they matter. 2K textures by default, 4K on request, KTX2/ASTC on delivery.</td></tr>
    <tr><th>Animation</th><td>Skeletal or transform animation in the USD stage, loop-clean, with idle and hero clips. Audio embedded where visionOS supports it.</td></tr>
    <tr><th>Packaging</th><td>USDZ packages validated with usdchecker, size-budgeted per target (Safari inline, website environment, RealityKit app, Quick Look AR). Source USDA and Maya scenes included.</td></tr>
    <tr><th>Environments</th><td>Full-immersion scenes with baked GI, HDR environment maps, spatial audio loops and a lowered/scaled variant set for headset comfort.</td></tr>
    <tr><th>Preview kit</th><td>A drop-in web viewer (the code running on this page) with native <code>&lt;model&gt;</code>, three.js fallback and AR Quick Look links.</td></tr>
  </table></div>
</div></section>

<section class="section"><div class="wrap grid grid--3">
  <div class="card card--pad"><div class="icon">{ic('pen')}</div><h3>Authoring</h3><p>Autodesk Maya, ZBrush, Adobe Substance 3D Painter, Reality Composer Pro, Quads on device.</p></div>
  <div class="card card--pad"><div class="icon">{ic('layers')}</div><h3>Validation</h3><p>Pixar USD tools, usdchecker, RealityKit and Quick Look passes on real Vision Pro hardware, Safari desktop and iOS.</p></div>
  <div class="card card--pad"><div class="icon">{ic('spark')}</div><h3>Appeal</h3><p>Thirty years of character work: silhouettes that read at a glance, materials that invite touch, scale that feels right in a room.</p></div>
</div></section>

<section class="section"><div class="wrap contact-card reveal"><p class="eyebrow eyebrow--orange">Need assets?</p><h2>Send the brief.</h2><p class="muted">A single hero prop or a whole cast, for an app, a store listing, an ad or a website environment. Include a description, budget and deadline.</p><div class="cluster"><a class="btn btn--orange" href="mailto:steve@sketchbot.tv?subject=USDZ%20assets">{ic('mail')} steve@sketchbot.tv</a></div></div></section>'''
    write('spatial/assets/index.html', layout(title='USDZ asset production for Apple Vision Pro — Sketchbot Studios', desc='Production-grade USDZ characters, props and environments for RealityKit, Quick Look and Safari: quad topology, PBR materials, validated packaging, spatial preview kit.', body=body, path='/spatial/assets/', section='spatial', og_image='/assets/spatial/tank_SS_V2.jpg', jsonld=SPATIAL_LD, keywords=['USDZ assets', 'USDZ production', 'Quick Look AR', 'RealityKit assets', 'usdchecker', 'OpenPBR', '3D asset pipeline'], og_alt='TRON Tank USDZ asset'))

def page_radial():
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Spatial','/spatial/'),('Radial Menu',None))}
  <div class="split">
    <div class="page-head"><p class="eyebrow eyebrow--orange">Open source · Swift · MIT</p><h1>Radial Menu</h1><p>A tunable radial, vertical and horizontal menu for visionOS, macOS, iPadOS and iOS. One Swift file with no dependencies, plus the app you tune it in: live sliders, draggable measure guides, synthesised audio cues and code export.</p>
    <div class="cluster"><a class="btn btn--orange" href="https://github.com/stevetalkowski/radial-menu" target="_blank" rel="noopener">GitHub {ic('arrow')}</a><a class="btn btn--ghost" href="/spatial/quads/">Born in Quads</a></div></div>
    <div class="card card--pad" style="font-family:var(--mono);font-size:.9rem;line-height:1.7"><p class="eyebrow eyebrow--orange mb-1">The packing rule</p>
<pre style="background:transparent;border:0;padding:0"><code>R = pitch / (2·sin(step/2))
pitch = iconSize × (1 + gutter)</code></pre><p class="muted mt-1">One base unit, one constraint. Change the icon size, the item count or the arc and the spacing re-solves. Nothing overlaps because nothing can.</p></div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  {section_head('Why it exists', 'Radial menus are easy to draw and hard to get right')}
  <div class="grid grid--3 mt-3">
    <div class="card card--pad"><h3>Parametric geometry</h3><p>Spacing, hit targets and the distance a hand travels before a sub-menu opens are all numbers, and every number is wrong until you've felt it on a device. So the geometry is parametric and the export ships ratios, not points.</p></div>
    <div class="card card--pad"><h3>It does not scroll</h3><p>Every item is on screen. Eight is comfortable, twelve is the ceiling. A radial menu's whole value is spatial constancy: Delete is at 7 o'clock, always, and your hand learns it in a week.</p></div>
    <div class="card card--pad"><h3>Four platforms, real hardware</h3><p>One target runs on visionOS, macOS, iPadOS and iOS, and all four have been run on real devices rather than only a simulator, which is where the more interesting bugs in DESIGN.md came from.</p></div>
  </div>
  <div class="split mt-3">
    <div class="stack"><h3>The tuning app</h3><p class="muted">Load your own menu, adjust icon size, gutter, arc, ring radius, sub-menu slide and easing with live sliders. Switch on measure guides to see the ring and the gutter it was solved for. Synthesised audio cues give each hover and commit a sound. When it feels right, export the ratios as Swift you can paste into your project.</p></div>
    <div class="stack"><h3>Designed for pinch</h3><p class="muted">Long pinch opens the dial, slide highlights, sub-items slide outward from their parent, release commits, and a short ease in and out keeps it from feeling jarring. It is the same interaction model that drives Quads' hold-menus in mid-air.</p></div>
  </div>
</div></section>'''
    ld = {"@context": "https://schema.org", "@type": "SoftwareSourceCode", "name": "Radial Menu", "codeRepository": "https://github.com/stevetalkowski/radial-menu", "programmingLanguage": "Swift", "runtimePlatform": "visionOS, macOS, iPadOS, iOS", "author": {"@id": BASE_URL + "/#steve"}, "license": "https://opensource.org/licenses/MIT"}
    write('spatial/radial-menu/index.html', layout(title='Radial Menu — open-source tunable menu for visionOS — Sketchbot Studios', desc='A tunable radial, vertical and horizontal menu for visionOS, macOS, iPadOS and iOS. One Swift file, no dependencies, plus a tuning app with live sliders and code export.', body=body, path='/spatial/radial-menu/', section='spatial', og_image=img(by_slug['afternoon-at-the-museum']['items'][5]['file']), jsonld=ld, keywords=['radial menu', 'SwiftUI', 'visionOS UI', 'open source Swift', 'pie menu', 'GitHub'], og_alt='Radial Menu, open-source tunable menu for visionOS'))

def page_services():
    svcs = [
        ('spark', 'Spatial character & mascot design', 'Original characters and brand mascots designed to read at arm’s length, hold up from every angle and feel right in a room. Delivered as animatable USDZ with idle and hero clips.'),
        ('cube', 'visionOS app design & prototyping', 'Concept, interaction model and glass-native UI for Vision Pro apps, prototyped in SwiftUI and RealityKit. Windows for typing, panels for glancing, hands first.'),
        ('globe', 'Immersive brand environments', 'Website environments and in-app immersive spaces: modeled, lit, scored and optimised for Safari and RealityKit, with the three-tier web code included.'),
        ('layers', 'USDZ & Reality Composer Pro pipelines', 'Set up or rescue a pipeline from Maya, Blender or ZBrush into validated USDZ. Naming, scale, materials, animation and size budgets that pass on device.'),
        ('users', 'SharePlay & multi-user experiences', 'Design and build shared spatial sessions with Personas, live cursors and conflict-free state, drawing on the co-modeling system inside Quads.'),
        ('pen', 'Training & advisory', 'Workshops for teams moving from 2D and desktop 3D into spatial: appeal, scale, comfort, input and the visionOS 27 toolchain. Fractional creative direction for spatial products.'),
    ]
    s_html = ''.join(f'<div class="card card--pad card--orange reveal"><div class="icon">{ic(i)}</div><h3>{t}</h3><p>{d}</p></div>' for i, t, d in svcs)
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Spatial','/spatial/'),('Services',None))}
  <div class="page-head"><p class="eyebrow eyebrow--orange">Studio services</p><h1>Professional spatial work, <span class="o">end to end</span></h1><p>Sketchbot Studios takes projects from the first sketch to a build running on Apple Vision Pro. Art direction, character design, modeling, animation, spatial UX and the engineering to make it real.</p></div>
  <div class="grid grid--3">{s_html}</div>
</div></section>

<section class="section"><div class="wrap">
  {section_head('Engagement', 'How a project runs')}
  <ol class="steps mt-3" role="list">
    <li><h3>Brief</h3><p>Description, estimated budget and deadline. NDAs, boards and references by email.</p></li>
    <li><h3>Discovery sprint</h3><p>One to two weeks: sketches, a scale and interaction test on the headset, a written plan with a fixed quote.</p></li>
    <li><h3>Build</h3><p>Weekly on-device builds or asset drops. You see it in your own Vision Pro, not in a render.</p></li>
    <li><h3>Ship &amp; support</h3><p>App Store or web delivery, source files and a pipeline handbook. A support window for the launch.</p></li>
  </ol>
</div></section>

<section class="section"><div class="wrap grid grid--2" style="align-items:start">
  <div class="card card--pad"><p class="eyebrow eyebrow--orange">Also available</p><h3>The classic studio</h3><p>Art direction, animation directing, character and concept design and 3D modeling in Maya and ZBrush for commercials, film and toys. See the <a href="/work/">work</a> and the <a href="/reel/">reel</a>.</p></div>
  <div class="card card--pad"><p class="eyebrow eyebrow--orange">Tooling</p><h3>Stack</h3><p>visionOS 27 SDK, SwiftUI, RealityKit, ARKit, GroupActivities, Reality Composer Pro, USDKit, Pixar USD, Maya, ZBrush, Substance 3D, Unreal Engine, Laravel for backends.</p></div>
</div></section>

<section class="section"><div class="wrap contact-card reveal"><p class="eyebrow eyebrow--orange">Upcoming gig?</p><h2>Let's talk.</h2><p class="muted">Please include a short description, estimated budget and deadline. Storyboards, supporting imagery and NDAs can be emailed directly.</p><div class="cluster"><a class="btn btn--orange" href="mailto:steve@sketchbot.tv?subject=Spatial%20project">{ic('mail')} steve@sketchbot.tv</a><a class="btn btn--ghost" href="/contact/">Contact page</a></div></div></section>'''
    ld = {"@context": "https://schema.org", "@type": "Service", "name": "Sketchbot Studios spatial services", "provider": {"@id": BASE_URL + "/#org"}, "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Spatial computing services", "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t}} for _, t, _ in svcs]}}
    write('spatial/services/index.html', layout(title='Spatial computing services for Apple Vision Pro — Sketchbot Studios', desc='Spatial character and mascot design, visionOS app design and prototyping, immersive brand environments, USDZ pipelines, SharePlay experiences and training from Sketchbot Studios.', body=body, path='/spatial/services/', section='spatial', og_image=img(by_slug['adobe-vr-bot']['items'][1]['file']), jsonld=ld, keywords=['spatial computing services', 'Vision Pro app design', 'mascot design', 'immersive brand environments', 'SharePlay development', 'spatial training'], og_alt='Adobe VR Bot sculpting light in a neon warehouse'))

def page_lab():
    m = by_slug['museum-of-untold-possibilities']
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Spatial','/spatial/'),('Lab',None))}
  <div class="page-head"><p class="eyebrow eyebrow--orange">The Lab</p><h1>Experiments &amp; research</h1><p>Spikes, sandboxes and pitches that feed the shipping work. Some are public repositories, some are notes; all of them taught the studio something about building for a headset.</p></div>
  <div class="grid grid--2">
    <div class="card card--pad"><p class="eyebrow eyebrow--orange">GitHub</p><h3>VRNavDemo</h3><p>A VR navigation sandbox for Vision Pro: testing tumble, orbit and fly navigation models against comfort. The Maya-style Y-up tumble with two scalar rotation states that Quads uses came out of this.</p><a class="btn btn--ghost mt-1" href="https://github.com/stevetalkowski/VRNavDemo" target="_blank" rel="noopener">Repository</a></div>
    <div class="card card--pad"><p class="eyebrow eyebrow--orange">Input research</p><h3>Muse stylus &amp; pointer probes</h3><p>Instrumented test targets for Logitech Muse accessory tracking, GameController button and pressure channels, and pointer input inside RealityKit's ManipulationComponent. Findings filed as Apple Feedback and folded into Quads.</p></div>
    <div class="card card--pad"><p class="eyebrow eyebrow--orange">Pitch</p><h3>The Museum of Untold Possibilities</h3><p>An Epic MegaGrant proposal for a non-game VR museum in the World of Sketchbot, with timed exhibitions, an AI robot docent and an Art Lab where visitors build and 3D-print their own robots.</p><a class="btn btn--ghost mt-1" href="/work/museum-of-untold-possibilities/">Read the pitch</a></div>
    <div class="card card--pad"><p class="eyebrow eyebrow--orange">Sketchfab</p><h3>ZBrush for iPad tests</h3><p>Alien Head V2, sculpted entirely on iPad and published as an interactive model.</p><a class="btn btn--ghost mt-1" href="https://sketchfab.com/stevetalkowski" target="_blank" rel="noopener">Sketchfab</a></div>
  </div>
  <div class="rounded mt-3 reveal" style="box-shadow:var(--shadow)">{picture(m['items'][0], sizes="100vw")}</div>
</div></section>

<section class="section"><div class="wrap">
  {section_head('Field notes', 'Things learned building for visionOS 27')}
  <div class="grid grid--2 mt-3">
    <div class="card card--pad"><h3>Interactive UI lives in windows</h3><p>Typing, scrubbing, popovers and dialogs need an OS window. Spatial panels get no keyboard and no presentations; keep them for glanceable, tap-only content.</p></div>
    <div class="card card--pad"><h3>ARKit needs an ImmersiveSpace</h3><p>Hand and accessory tracking only run in an immersive space, so a serious modeling workspace can't live in a volume. Volumes are for viewing, not for making.</p></div>
    <div class="card card--pad"><h3>Budget your entities</h3><p>Every per-element handle is a RealityKit entity. Past a couple of thousand, the CPU watchdog wins. Dense meshes want collider tools, not handles.</p></div>
    <div class="card card--pad"><h3>Small mesh files aren't free</h3><p>Apple's proprietary mesh codec halves a USDZ but locks out Maya, Blender and Pixar's tools. Ship standard packages when the file has to travel.</p></div>
  </div>
</div></section>'''
    write('spatial/lab/index.html', layout(title='The Lab — spatial computing experiments — Sketchbot Studios', desc='Experiments and research from Sketchbot Studios: VR navigation sandbox, stylus input probes, the Museum of Untold Possibilities pitch, and field notes from building for visionOS 27.', body=body, path='/spatial/lab/', section='spatial', og_image=img(m['items'][0]['file']), jsonld=SPATIAL_LD, keywords=['VR research', 'VRNavDemo', 'stylus input', 'Museum of Untold Possibilities', 'visionOS 27 notes'], og_alt='Eye Pilot wearing a VR headset'))

# ----------------------------------------------------------------------------- WORK
def page_work_index():
    cats = sorted({p['category'] for p in projects_cur})
    fl = '<button data-filter="all" aria-pressed="true">All</button><button data-filter="Spatial">Spatial</button>' + ''.join(f'<button data-filter="{esc(c)}">{esc(c)}</button>' for c in cats)
    cards = ''.join(work_card(p, wide=(i in (0, 7, 14)), eager=(i < 3)) for i, p in enumerate(projects_cur))
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Work',None))}
  <div class="page-head"><p class="eyebrow eyebrow--orange">Work</p><h1>Robots, mascots, worlds</h1><p>{len(projects_cur)} projects spanning designer toys, brand mascots, feature-film concept art, real-time worlds and spatial environments for Apple Vision Pro.</p><div class="filters" role="group" aria-label="Filter projects">{fl}</div></div>
  <div class="work-grid">{cards}</div>
</div></section>'''
    write('work/index.html', layout(title='Work — Sketchbot Studios', desc='Portfolio of Sketchbot Studios: the Sketchbot designer toy, mascots for Autodesk and KeyShot, concept art for SCOOB!, Unreal worlds, and spatial environments for Apple Vision Pro.', body=body, path='/work/', section='work', og_image=img(by_slug['sketchbot']['hero_img']['file']), keywords=['portfolio', 'character design portfolio', 'mascot design', 'concept art', 'Unreal Engine', 'designer vinyl toy'], og_alt='Sketchbot designer vinyl toy with pencil'))

def page_project(p, prev, nxt):
    facts = f'''<dl class="facts"><div><dt>Year</dt><dd>{esc(p["year"])}</dd></div><div><dt>Category</dt><dd>{esc(p["category"])}</dd></div><div><dt>Roles</dt><dd>{esc(", ".join(p["roles"]))}</dd></div><div><dt>Tools</dt><dd>{esc(", ".join(p["tools"]))}</dd></div></dl>'''
    paras = ''.join(f'<p>{esc(x)}</p>' for x in p.get('body', []))
    video = f'<div class="video mt-3 reveal"><iframe src="{p["video"]}" title="{esc(p["title"])} video" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>' if p.get('video') else ''
    spatial_cta = ''
    if p.get('spatial'):
        spatial_cta = f'<div class="card card--pad card--orange mt-3"><p class="eyebrow eyebrow--orange">Spatial</p><h3>Step inside on Vision Pro</h3><p>This project is a full-immersion website environment. Open it from the Immersive environments page in Safari on Apple Vision Pro.</p><a class="btn btn--orange mt-1" href="/spatial/environments/">Enter {ic("arrow")}</a></div>'
    related = ''
    if p.get('related') and p['related'] in by_slug:
        r = by_slug[p['related']]; related = f'<p class="mt-2">Related: <a href="{r["url"]}">{esc(r["title"])}</a></p>'
    tags = ''.join(f'<span class="chip">{esc(t)}</span>' for t in p.get('tags', []))
    body = f'''
<article>
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem);padding-bottom:0"><div class="wrap project-hero">
  {crumbs(('Home','/'),('Work','/work/'),(p['title'],None))}
  <div class="cluster"><span class="chip chip--orange">{esc(p['category'])}</span>{tags}</div>
  <h1>{esc(p['title'])}</h1>
  <p class="lede" style="font-size:1.25rem;color:var(--fg-2)">{esc(p['blurb'])}</p>
  <div class="media hero-media" style="position:relative;inset:auto;z-index:auto">{picture(p['hero_img'], lazy=False, sizes="100vw", alt=p['title'])}</div>
</div></section>
<section class="section section--tight"><div class="wrap split" style="align-items:start">
  <div class="stack prose">{paras}{related}{spatial_cta}</div>
  <div>{facts}</div>
</div></section>
<section class="section section--tight"><div class="wrap">{video}<h2 class="mb-2 mt-2">Gallery <span class="dim" style="font-size:.6em;font-weight:600">{len(p['items'])} images</span></h2>{gallery(p['items'], p['title'])}</div></section>
<section class="section section--tight"><div class="wrap pager">
  <a class="card card--pad" href="{prev['url']}"><p class="eyebrow">← Previous</p><h3>{esc(prev['title'])}</h3></a>
  <a class="card card--pad" href="{nxt['url']}" style="text-align:right"><p class="eyebrow">Next →</p><h3>{esc(nxt['title'])}</h3></a>
</div></section>
</article>'''
    ld = {"@context": "https://schema.org", "@type": "CreativeWork", "name": p['title'], "url": BASE_URL + p['url'], "description": p['blurb'], "creator": {"@id": BASE_URL + "/#steve"}, "image": BASE_URL + img(p['hero_img']['file']), "keywords": ", ".join(p.get('tags', [])), "dateCreated": p['year'][:4]}
    write(p['url'] + 'index.html', layout(title=f'{p["title"]} — Sketchbot Studios', desc=p['blurb'], body=body, path=p['url'], section='work', og_image=img(p['hero_img']['file']), jsonld=ld, kind='article', keywords=[p['title'], p['category'], *p.get('tags', []), *p.get('tools', [])], og_alt=p['title'], published=f"{p['year'][:4]}-01-01"))

# ----------------------------------------------------------------------------- REEL / ABOUT / CONTACT / SHOP
def page_reel():
    breakdown = open(ROOT / 'docs/APPENDIX-C-reel.md').read().split('Shot Breakdown:')[1]
    rows = ''.join(f'<tr><td><strong>{esc(a.strip())}</strong></td><td>{esc(b.strip())}</td></tr>' for line in breakdown.strip().splitlines() if ' – ' in line for a, b in [line.split(' – ', 1)])
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Demo reel',None))}
  <div class="page-head"><p class="eyebrow eyebrow--orange">Demo reel</p><h1>Thirty years of motion</h1><p>Spots for TruGreen, Cocoa Puffs, Honey Nut Cheerios, SanDisk, TheraFlu, Efficiency Vermont, Sticker Book Inc., Yoplait, Capital Cube and many more, alongside feature work at Blue Sky Studios.</p></div>
  <div class="video reveal"><iframe src="https://player.vimeo.com/video/{site_cfg['reel_vimeo_id']}?title=0&byline=0&portrait=0&dnt=1" title="Steve Talkowski demo reel" loading="lazy" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>
  <p class="dim small mt-1">Can't see the player? <a href="https://vimeo.com/stevetalkowski" target="_blank" rel="noopener">Watch on Vimeo</a>.</p>
</div></section>
<section class="section"><div class="wrap">{section_head('Shot breakdown', 'Who did what')}<div class="table-wrap mt-2"><table><thead><tr><th>Shot</th><th>Contribution</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>'''
    write('reel/index.html', layout(title='Demo reel — Steve Talkowski | Sketchbot Studios', desc='Demo reel and full shot breakdown: modeling, rigging, animation, lighting and VFX supervision for national brands and feature films.', body=body, path='/reel/', section='reel', og_image=img(by_slug['3d-misc']['items'][20]['file']), keywords=['demo reel', 'animation reel', 'commercial animation', 'VFX supervisor', 'character animator'], og_alt='Steve Talkowski demo reel'))

def page_about():
    portrait = archive_projects['about']['items'][0]
    clients = ''.join(f'<li>{esc(c)}</li>' for c in site_cfg['clients'])
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap split" style="align-items:start">
  <div class="stack" style="--stack:1.2rem">
    {crumbs(('Home','/'),('About',None))}
    <p class="eyebrow eyebrow--orange">About</p><h1>Steve Talkowski</h1>
    <div class="prose">
      <p>A veteran of the computer animation scene, I have worked as an Art Director, Animation Director, Character Designer/Modeler and Animator on hundreds of national brands ranging from Beats by Dre, BMW, Pepsi, General Mills, Target, Reese's and M&amp;M's, to the feature films <em>Joe's Apartment</em>, <em>Ice Age</em>, <em>Alien Resurrection</em> and the 1998 Academy Award-winning short, <em>Bunny</em>, during a most productive stint as senior animator at Blue Sky Studios.</p>
      <p>In 2008, I launched Sketchbot Studios and self-produced my first foray into the designer toy scene: the retro-styled, pencil-wielding robot, Sketchbot. In 2010, the Sketchbot platform served as the basis for two highly successful DIY custom shows held in NYC and LA.</p>
      <p>Based in Los Angeles, CA, I design original characters for toy and branding properties, freelance on film and commercials, and keep developing my world of robots into an animated series. Since 2024 the studio's centre of gravity has moved to spatial computing: I'm shipping <a href="/spatial/quads/">Quads</a>, a modeling app for Apple Vision Pro, building <a href="/spatial/environments/">immersive website environments</a>, and offering <a href="/spatial/services/">professional spatial services</a> to brands and studios.</p>
      <p>The original TRON ignited my passion for computer animation when I first saw it at 16 in 1982. Forty-odd years later I'm building The Grid you can stand in. That feels about right.</p>
    </div>
    <div class="cluster"><a class="btn btn--orange" href="/contact/">Get in touch</a><a class="btn btn--ghost" href="/reel/">{ic('play')} Demo reel</a><a class="btn btn--ghost" href="https://www.linkedin.com/in/stevetalkowski" target="_blank" rel="me noopener">LinkedIn</a></div>
  </div>
  <div class="stack">
    <div class="rounded" style="box-shadow:var(--shadow)">{picture(portrait, sizes="(max-width:700px) 100vw, 45vw", alt="Steve Talkowski", lazy=False)}</div>
    <div class="card card--pad"><p class="eyebrow mb-1">Clients &amp; credits</p><ul role="list" class="cluster small muted">{clients}</ul></div>
    <div class="card card--pad"><p class="eyebrow mb-1">Press</p><p class="small muted">3D World Magazine #191 (BuddhaBot cover) and #198 (KeyShot 6 tutorial) · Nuthin' But Mech Vol. 3 &amp; 4, Design Studio Press · Creative Bloq</p></div>
  </div>
</div></section>
<section class="section"><div class="wrap">{section_head('Timeline', 'Milestones')}<div class="table-wrap mt-2"><table>
<tr><th>1982</th><td>Sees TRON at 16. Decides on computer animation.</td></tr>
<tr><th>1990s</th><td>Senior animator at Blue Sky Studios: <em>Joe's Apartment</em>, <em>Alien Resurrection</em>, <em>Bunny</em> (Academy Award, 1998), <em>Ice Age</em> (3D layout).</td></tr>
<tr><th>2000s</th><td>Animation director and VFX supervisor on hundreds of national commercials in New York.</td></tr>
<tr><th>2007</th><td>Starts the Sketchbot blog; attends Pictoplasma Berlin.</td></tr>
<tr><th>2008</th><td>Founds Sketchbot Studios. Sketchbot prototype sculpted, 3D-printed and molded.</td></tr>
<tr><th>2010</th><td>Sketchbot vinyl figure released; Sketchbot Custom Shows in NYC and LA.</td></tr>
<tr><th>2011</th><td>Relocates to Los Angeles. Variants 3, 4 and 5; DesignerCon resin editions.</td></tr>
<tr><th>2014–2016</th><td>BuddhaBot on the cover of 3D World; KeyShot 6 avatar; Autodesk Maya M4Y4 mascot; March of Robots.</td></tr>
<tr><th>2020–2021</th><td>Afternoon At The Museum in Unreal; Museum of Untold Possibilities MegaGrant pitch; SCOOB! concept art.</td></tr>
<tr><th>2024–2026</th><td>Spatial computing: Quads for Apple Vision Pro, TRON and Backrooms immersive environments, open-source Radial Menu.</td></tr>
</table></div></div></section>'''
    ld = {"@context": "https://schema.org", "@type": "Person", "@id": BASE_URL + "/#steve", "name": "Steve Talkowski", "image": BASE_URL + img(portrait['file']), "jobTitle": "Creative Director", "worksFor": {"@id": BASE_URL + "/#org"}, "sameAs": [s['href'] for s in SOCIAL], "knowsAbout": ["Character design", "3D animation", "Apple Vision Pro", "visionOS", "USDZ", "Maya", "ZBrush", "Unreal Engine"]}
    write('about/index.html', layout(title='About Steve Talkowski — Sketchbot Studios', desc='Steve Talkowski: animation director, character designer and creator of the Sketchbot designer toy, now building professional tools for Apple Vision Pro.', body=body, path='/about/', section='about', og_image=img(portrait['file']), jsonld=ld, kind='profile', keywords=['Steve Talkowski bio', 'Blue Sky Studios', 'Ice Age animator', 'Bunny Academy Award', 'Sketchbot creator'], og_alt='Steve Talkowski in front of a giant Sketchbot eye'))

def page_contact():
    hero = archive_projects['contact']['items'][0]
    tiles = [
        (hero, 'The workshop', 'c-a'),
        (by_slug['sketchbot']['items'][0], 'Sketchbot V1 with pencil', 'c-b'),
        (by_slug['afternoon-at-the-museum']['items'][5], 'Sketchbot on display in the museum', 'c-c'),
        (by_slug['3d-misc']['items'][5], 'Eye Pilot in a VR headset', 'c-e'),
    ]
    collage = ''.join(f'<figure class="{cls}">{picture(it, sizes="(max-width:700px) 50vw, 20vw", alt=alt, lazy=False)}</figure>' for it, alt, cls in tiles)
    soc = ''.join(f'<a href="{s["href"]}" target="_blank" rel="me noopener">{s["label"]}</a>' for s in SOCIAL)
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Contact',None))}
  <div class="split" style="align-items:start">
    <div class="contact-card"><p class="eyebrow eyebrow--orange">Upcoming gig?</p><h1 style="font-size:clamp(2.4rem,5vw,4rem)">Let's talk.</h1>
      <p class="muted">Feel free to contact me regarding any upcoming projects. Please include a short description, estimated budget and deadline.</p>
      <p class="muted">I'm currently available for <strong>art direction, animation directing, character and concept design, 3D modeling (Maya, ZBrush)</strong> and <strong>spatial computing work for Apple Vision Pro</strong>: app design, USDZ assets and immersive environments.</p>
      <p class="muted">Additional storyboards, supporting imagery and NDAs can be emailed directly.</p>
      <div class="cluster"><a class="btn btn--orange" href="mailto:steve@sketchbot.tv">{ic('mail')} steve@sketchbot.tv</a></div>
      <div class="socials mt-1">{soc}</div>
      <p class="dim small">Los Angeles, CA · Pacific time</p>
    </div>
    <div class="collage" aria-label="Studio work">{collage}</div>
  </div>
</div></section>'''
    ld = {"@context": "https://schema.org", "@type": "ContactPage", "url": BASE_URL + "/contact/", "mainEntity": {"@id": BASE_URL + "/#org"}}
    write('contact/index.html', layout(title='Contact — Sketchbot Studios', desc='Contact Steve Talkowski at Sketchbot Studios for art direction, character design, 3D modeling and Apple Vision Pro spatial computing projects.', body=body, path='/contact/', section='contact', og_image=img(hero['file']), jsonld=ld, keywords=['hire 3D artist', 'hire character designer', 'art direction', 'Vision Pro developer for hire', 'steve@sketchbot.tv'], og_alt='Resin robot prototypes in the Sketchbot workshop'))

def page_shop():
    sb = by_slug['sketchbot']
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('Shop',None))}
  <div class="split">
    <div class="page-head"><p class="eyebrow eyebrow--orange">Shop</p><h1>Sketchbot, the designer vinyl toy</h1><p>The 5.5-inch retro robot with a removable pencil, produced by Sketchbot Studios since 2010. Colourway variants, resin exclusives and 3D-printable robots have shipped through My Plastic Heart, Crewest, DesignerCon and Mold3D.</p>
      <div class="cluster"><a class="btn btn--orange" href="mailto:steve@sketchbot.tv?subject=Sketchbot%20availability">{ic('mail')} Ask about availability</a><a class="btn btn--ghost" href="/work/sketchbot/">Project page</a></div>
      <p class="dim small">The online store is being rebuilt. Email for current stock, commissions and custom-show blanks.</p></div>
    <div class="rounded" style="box-shadow:var(--shadow)">{picture(sb['items'][2], sizes="(max-width:700px) 100vw, 45vw", alt="Sketchbot vinyl figure with box", lazy=False)}</div>
  </div>
</div></section>
<section class="section"><div class="wrap">{section_head('Editions', 'Releases so far')}<div class="table-wrap mt-2"><table><thead><tr><th>Edition</th><th>Year</th><th>Notes</th></tr></thead><tbody>
<tr><td>Sketchbot V1 (orange)</td><td>2010</td><td>Launch colourway with pencil accessory. Release signings at My Plastic Heart NYC and Crewest LA.</td></tr>
<tr><td>Variant 3 (magenta)</td><td>2011</td><td>Semi-translucent magenta vinyl, ink-pen accessory and matching sticker. Debuted at TOYSTREET NYC.</td></tr>
<tr><td>Variant 4</td><td>2011</td><td>San Diego Comic-Con 2011.</td></tr>
<tr><td>Variant 5</td><td>2011</td><td>New York Comic-Con pre-release with My Plastic Heart, booth 879.</td></tr>
<tr><td>DesignerCon resin</td><td>2011</td><td>Resin casts by Pretty In Plastic, six colours, edition of 30.</td></tr>
<tr><td>Mold3D robots</td><td>2015</td><td>3D-printable robot files as a launch artist on the Mold3D shop.</td></tr>
</tbody></table></div><div class="gallery mt-3">{gallery(sb['items'][:8], 'Sketchbot')[len('<div class="gallery">'):-6]}</div></div></section>'''
    ld = {"@context": "https://schema.org", "@type": "Product", "name": "Sketchbot designer vinyl toy", "brand": {"@type": "Brand", "name": "Sketchbot Studios"}, "image": BASE_URL + img(sb['items'][2]['file']), "description": "5.5-inch retro-styled pencil-wielding robot vinyl figure by Steve Talkowski."}
    write('shop/index.html', layout(title='Shop — Sketchbot designer vinyl toy | Sketchbot Studios', desc='The Sketchbot designer vinyl toy by Steve Talkowski: editions, variants and how to get one.', body=body, path='/shop/', section='shop', og_image=img(sb['items'][2]['file']), jsonld=ld, keywords=['Sketchbot vinyl toy', 'designer toy', 'art toy', 'vinyl figure', 'My Plastic Heart', 'DesignerCon'], og_alt='Sketchbot V1 vinyl figure with its box'))

# ----------------------------------------------------------------------------- NEWS
man = json.load(open(ROOT / 'archive/images/manifest.json'))
man_by_base = {k.split('?')[0]: v['file'] for k, v in man.items()}

def post_html(p):
    """Original Squarespace body HTML with images re-pointed at local derivatives."""
    if p.get('html'): return p['html']
    key = p['url'].replace('https://www.sketchbot.tv/', '').strip('/').replace('/', '__')
    raw = ROOT / f'archive/raw/json/{key}.json'
    body = ''
    if raw.exists():
        try: body = (json.load(open(raw)).get('item') or {}).get('body') or ''
        except Exception: body = ''
    if not body:
        body = ''.join(f'<p>{esc(x)}</p>' for x in p['body'].split('\n') if x.strip())
    body = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', body, flags=re.S)
    body = re.sub(r'\sdata-(?:src|image)="[^"]*"', '', body)
    body = re.sub(r'<button\b.*?</button>', '', body, flags=re.S)
    body = re.sub(r'<a[^>]*>\s*View fullsize\s*</a>|View fullsize', '', body)
    body = re.sub(r'\n\s*\n+', '\n', body)
    def fix(m):
        u = m.group(1).split('?')[0]
        loc = man_by_base.get(u)
        return f'src="{img(loc)}"' if loc else m.group(0)
    body = re.sub(r'(?:data-src|src)="(https://(?:images|static1)\.squarespace(?:-cdn)?\.com/[^"]+)"', fix, body)
    body = re.sub(r'<img(?![^>]*loading=)', '<img loading="lazy" decoding="async"', body)
    body = re.sub(r'\s(?:data-[a-z\-]+|class|id|style|srcset|sizes|onload|elementtiming)(?:="[^"]*")?', '', body)  # strip Squarespace attrs
    body = re.sub(r'<a[^>]*>\s*View fullsize\s*</a>', '', body)
    body = re.sub(r'<div[^>]*>|</div>', '', body)
    return body

def page_news():
    years = sorted({p['dt'].year for p in posts if p['dt']}, reverse=True)
    ynav = ''.join(f'<a href="#y{y}">{y}</a>' for y in years)
    rows = ''
    for y in years:
        rows += f'<h2 id="y{y}" class="mt-3 mb-1">{y}</h2>'
        for p in [x for x in posts if x['dt'] and x['dt'].year == y]:
            rows += f'<a class="post-row" href="/news/{p["slug"]}/"><time datetime="{p["dt"].date().isoformat()}">{p["dt"].strftime("%d %b %Y")}</time><span><strong>{esc(p["title"])}</strong><p>{esc(p["excerpt"][:160])}</p></span></a>'
    body = f'''
<section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap">
  {crumbs(('Home','/'),('News',None))}
  <div class="page-head"><p class="eyebrow eyebrow--orange">News</p><h1>The studio blog</h1><p>{len(posts)} posts since November 2007: the making of Sketchbot, custom shows, conventions, tutorials, studio life, and the move into spatial computing. <a href="/feed.xml">RSS</a>.</p><div class="year-nav">{ynav}</div></div>
  <div class="post-list">{rows}</div>
</div></section>'''
    write('news/index.html', layout(title='News — Sketchbot Studios blog', desc=f'The Sketchbot Studios blog: {len(posts)} posts on the making of the Sketchbot designer toy, custom shows, conventions, 3D tutorials and Apple Vision Pro work.', body=body, path='/news/', section='news', og_image=img(by_slug['sketchbot']['items'][0]['file']), keywords=['Sketchbot blog', 'studio news', 'designer toy blog', '3D tutorials', 'custom toy shows'], og_alt='Sketchbot designer vinyl toy with pencil'))
    for i, p in enumerate(posts):
        prev = posts[i + 1] if i + 1 < len(posts) else None; nxt = posts[i - 1] if i > 0 else None
        pager = '<div class="pager mt-3">' + (f'<a class="card card--pad" href="/news/{prev["slug"]}/"><p class="eyebrow">← Older</p><h3>{esc(prev["title"])}</h3></a>' if prev else '<span></span>') + (f'<a class="card card--pad" href="/news/{nxt["slug"]}/" style="text-align:right"><p class="eyebrow">Newer →</p><h3>{esc(nxt["title"])}</h3></a>' if nxt else '') + '</div>'
        tags = ''.join(f'<span class="chip">{esc(t.strip(chr(34)))}</span>' for t in p['tags'][:8])
        d = p['dt'].strftime('%d %B %Y') if p['dt'] else ''
        body = f'''
<article><section class="section" style="padding-top:clamp(1.25rem,3vw,2rem)"><div class="wrap--narrow">
  {crumbs(('Home','/'),('News','/news/'),(p['title'],None))}
  <div class="page-head" style="padding-top:1.5rem"><p class="eyebrow eyebrow--orange"><time datetime="{p['dt'].date().isoformat() if p['dt'] else ''}">{d}</time></p><h1 style="font-size:clamp(2rem,4.5vw,3.4rem)">{esc(p['title'])}</h1><div class="cluster">{tags}</div></div>
  <div class="prose">{post_html(p)}</div>
  {'' if p.get('new') else f'<p class="dim small mt-3">Originally published at <a href="{p["url"]}" rel="nofollow">{p["url"].replace("https://www.","")}</a>.</p>'}
  {pager}
</div></section></article>'''
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p['title'], "datePublished": p['dt'].isoformat() if p['dt'] else None, "author": {"@id": BASE_URL + "/#steve"}, "publisher": {"@id": BASE_URL + "/#org"}, "url": BASE_URL + f'/news/{p["slug"]}/', "image": BASE_URL + img(p['image']) if p.get('image') else None}
        write(f'news/{p["slug"]}/index.html', layout(title=f'{p["title"]} — Sketchbot Studios', desc=p['excerpt'][:200], body=body, path=f'/news/{p["slug"]}/', section='news', og_image=img(p['image']) if p.get('image') else None, jsonld={k: v for k, v in ld.items() if v}, kind='article', keywords=[p['title'], *[t.strip(chr(34)) for t in p['tags']]], og_alt=p['title'], published=p['dt'].date().isoformat() if p['dt'] else None))

# ----------------------------------------------------------------------------- misc files
def page_404():
    body = f'<section class="section center"><div class="wrap--narrow stack"><p class="eyebrow eyebrow--orange">404</p><h1>END OF LINE</h1><p class="muted">That page derezzed. Try the <a href="/">home page</a>, the <a href="/work/">work</a>, or the <a href="/spatial/">spatial computing</a> pages.</p></div></section>'
    write('404.html', layout(title='Not found — Sketchbot Studios', desc='Page not found.', body=body, path='/404.html'))

def misc(urls):
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n')
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{BASE_URL}{u}</loc><lastmod>{NOW}</lastmod></url>\n' for u in urls) + '</urlset>\n')
    items = ''.join(f'<item><title>{esc(p["title"])}</title><link>{BASE_URL}/news/{p["slug"]}/</link><guid>{BASE_URL}/news/{p["slug"]}/</guid><pubDate>{p["dt"].strftime("%a, %d %b %Y %H:%M:%S GMT") if p["dt"] else ""}</pubDate><description>{esc(p["excerpt"][:300])}</description></item>' for p in posts[:50])
    write('feed.xml', f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Sketchbot Studios — News</title><link>{BASE_URL}/news/</link><description>The Sketchbot Studios blog.</description>{items}</channel></rss>')
    write('manifest.webmanifest', json.dumps({"name": "Sketchbot Studios", "short_name": "Sketchbot", "start_url": "/", "display": "standalone", "background_color": "#0b0b0e", "theme_color": "#f5921f", "icons": [{"src": "/assets/brand/logo-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "/assets/brand/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}]}))
    shutil.copy(SITE / 'assets/brand/favicon-32.png', SITE / 'favicon.png')
    write('llms.txt', f'''# Sketchbot Studios

> The character-driven 3D studio of Steve Talkowski (Los Angeles). Thirty years of animation for brands and film, creator of the Sketchbot designer toy, and professional tools and services for Apple Vision Pro.

Contact: steve@sketchbot.tv

## Spatial computing (Apple Vision Pro)
- [Overview](/spatial/): the studio's Apple Vision Pro work
- [Quads](/spatial/quads/): spatial box modeler for Apple Vision Pro (coming soon; https://quads.vision)
- [Immersive website environments](/spatial/environments/): TRON The Grid and the Backrooms, full-immersion Safari environments
- [USDZ asset production](/spatial/assets/): characters, props and environments for RealityKit, Quick Look and Safari
- [Radial Menu](/spatial/radial-menu/): open-source tunable menu for visionOS/macOS/iPadOS/iOS (https://github.com/stevetalkowski/radial-menu)
- [Services](/spatial/services/): spatial character design, visionOS app design, environments, pipelines, SharePlay, training
- [Lab](/spatial/lab/): experiments and field notes

## Studio
- [Work](/work/): {len(projects_cur)} projects
{''.join(f"- [{p['title']}]({p['url']}): {p['blurb']}" + chr(10) for p in projects_cur)}- [Demo reel](/reel/)
- [About](/about/)
- [News](/news/): {len(posts)} blog posts, 2007–2015
- [Shop](/shop/): the Sketchbot vinyl toy
- [Contact](/contact/)
''')
    # tiny service worker: cache shell assets, network-first pages
    write('sw.js', '''const C='sb-v1';const SHELL=['/assets/css/site.css','/assets/js/site.js','/assets/js/spatial.js'];
self.addEventListener('install',e=>e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(u.origin!==location.origin||e.request.method!=='GET')return;
if(u.pathname.startsWith('/assets/'))e.respondWith(caches.open(C).then(async c=>{const h=await c.match(e.request);if(h)return h;const r=await fetch(e.request);if(r.ok)c.put(e.request,r.clone());return r;}));});''')

# ----------------------------------------------------------------------------- run
def main():
    for d in ['index.html', 'spatial', 'work', 'news', 'about', 'contact', 'shop', 'reel', '404.html']:
        p = SITE / d
        if p.is_dir(): shutil.rmtree(p)
        elif p.exists(): p.unlink()
    page_home(); page_spatial(); page_quads(); page_environments(); page_assets(); page_radial(); page_services(); page_lab()
    page_work_index()
    for i, p in enumerate(projects_cur):
        page_project(p, projects_cur[i - 1], projects_cur[(i + 1) % len(projects_cur)])
    page_reel(); page_about(); page_contact(); page_shop(); page_news(); page_404()
    urls = ['/', '/spatial/', '/spatial/quads/', '/spatial/environments/', '/spatial/assets/', '/spatial/radial-menu/', '/spatial/services/', '/spatial/lab/', '/work/', '/reel/', '/about/', '/contact/', '/shop/', '/news/'] + [p['url'] for p in projects_cur] + [f'/news/{p["slug"]}/' for p in posts]
    misc(urls)
    # OG default
    og = SITE / 'assets/og'; og.mkdir(parents=True, exist_ok=True)
    card = og_card('/assets/img/full/9d642038_backrooms_SB-03.png')
    if card.startswith('/assets/og/'): shutil.copy(SITE / card.lstrip('/'), og / 'default.jpg')
    n = sum(1 for _ in SITE.rglob('*.html'))
    print(f'built {n} pages → {SITE}')

if __name__ == '__main__':
    main()
