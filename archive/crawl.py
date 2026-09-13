#!/usr/bin/env python3
"""Archive www.sketchbot.tv (Squarespace) — pages, JSON, images, text."""
import re, json, os, sys, html, time, hashlib, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
BASE="https://www.sketchbot.tv"
UA={'User-Agent':'Mozilla/5.0 (Macintosh) ArchiveBot/1.0'}
os.makedirs('raw/html',exist_ok=True); os.makedirs('raw/json',exist_ok=True); os.makedirs('images',exist_ok=True); os.makedirs('pages',exist_ok=True)
def get(url,binary=False,tries=3):
    for i in range(tries):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40)
            d=r.read(); return d if binary else d.decode('utf-8','replace')
        except Exception as e:
            time.sleep(1+i)
    print("FAIL",url,file=sys.stderr); return None
# 1. sitemap
sm=get(BASE+'/sitemap.xml'); ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','i':'http://www.google.com/schemas/sitemap-image/1.1'}
root=ET.fromstring(sm); urls=[]; imgs={}
for u in root.findall('s:url',ns):
    loc=u.find('s:loc',ns).text.replace('http://','https://')
    urls.append(loc)
    for im in u.findall('i:image',ns):
        l=im.find('i:loc',ns).text; t=im.find('i:title',ns); c=im.find('i:caption',ns)
        imgs[l]={'page':loc,'title':t.text if t is not None else '','caption':c.text if c is not None else ''}
# add nav pages from home
home=get(BASE+'/')
for p in set(re.findall(r'href="(/[a-z0-9_\-]+)"',home)):
    if BASE+p not in urls and p not in ('/cart',): urls.append(BASE+p)
urls=sorted(set(urls)); print(len(urls),"pages")
def slug(u):
    p=urllib.parse.urlparse(u).path.strip('/') or 'home'; return p.replace('/','__')
pages={}
def fetch_page(u):
    s=slug(u); h=get(u); 
    if h: open(f'raw/html/{s}.html','w').write(h)
    j=get(u+('&' if '?' in u else '?')+'format=json-pretty')
    data=None
    if j:
        try: data=json.loads(j); open(f'raw/json/{s}.json','w').write(json.dumps(data,indent=1))
        except Exception: pass
    return u,h,data
with ThreadPoolExecutor(6) as ex:
    for u,h,d in ex.map(fetch_page,urls): pages[u]=(h,d)
# 2. collect images from html + json
imgre=re.compile(r'(https://(?:images|static1)\.squarespace(?:-cdn)?\.com/[^"\' )\\?]+)')
for u,(h,d) in pages.items():
    for m in imgre.findall(h or ''):
        imgs.setdefault(m,{'page':u,'title':'','caption':''})
    if d:
        for m in imgre.findall(json.dumps(d)):
            m=m.replace('\\/','/'); imgs.setdefault(m,{'page':u,'title':'','caption':''})
imgs={k:v for k,v in imgs.items() if re.search(r'\.(jpe?g|png|gif|webp|svg)$',k,re.I) or 'image-asset' in k}
print(len(imgs),"images")
def dl(item):
    url,meta=item
    name=hashlib.md5(url.encode()).hexdigest()[:8]+'_'+os.path.basename(urllib.parse.urlparse(url).path)
    if not re.search(r'\.\w{3,4}$',name): name+='.jpg'
    path='images/'+name
    if not os.path.exists(path):
        d=get(url+'?format=2500w',binary=True) or get(url,binary=True)
        if d: open(path,'wb').write(d)
    meta['file']=path; return url,meta
with ThreadPoolExecutor(8) as ex:
    imgs=dict(ex.map(dl,imgs.items()))
json.dump(imgs,open('images/manifest.json','w'),indent=1)
# 3. text extraction per page → markdown
def strip(hh):
    t=re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>','',hh,flags=re.S)
    t=re.sub(r'<(h[1-6])[^>]*>','\n## ',t); t=re.sub(r'</h[1-6]>','\n',t)
    t=re.sub(r'<(p|div|li|br)[^>]*>','\n',t); t=re.sub(r'<[^>]+>','',t)
    t=html.unescape(t); t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n\n',t); return t.strip()
inv=[]
for u,(h,d) in sorted(pages.items()):
    if not h: continue
    s=slug(u); title=re.search(r'<title>(.*?)</title>',h,re.S); title=html.unescape(title.group(1).strip()) if title else s
    desc=re.search(r'name="description" content="([^"]*)"',h); desc=html.unescape(desc.group(1)) if desc else ''
    body=re.search(r'<main[^>]*>(.*?)</main>',h,re.S) or re.search(r'<div[^>]*id="content"[^>]*>(.*)',h,re.S)
    txt=strip(body.group(1) if body else h)
    vids=sorted(set(re.findall(r'(https?://(?:vimeo\.com|player\.vimeo\.com|www\.youtube\.com|youtu\.be)/[^"\'&\s<]+)',h)))
    ext=sorted(set(e for e in re.findall(r'href="(https?://[^"]+)"',h) if 'squarespace' not in e and 'sketchbot.tv' not in e and 'sqspcdn' not in e))
    pimgs=[k for k,v in imgs.items() if v['page']==u]
    md=f"# {title}\n\n**URL:** {u}\n\n**Description:** {desc}\n\n"
    if vids: md+="**Videos:**\n"+"\n".join(f"- {v}" for v in vids)+"\n\n"
    if ext: md+="**External links:**\n"+"\n".join(f"- {e}" for e in ext)+"\n\n"
    md+="## Page text\n\n"+txt+"\n\n"
    if pimgs: md+="## Images\n\n"+"\n".join(f"- {imgs[k].get('file')} — {imgs[k]['caption'] or imgs[k]['title']} ({k})" for k in pimgs)+"\n"
    open(f'pages/{s}.md','w').write(md)
    inv.append({'url':u,'title':title,'description':desc,'words':len(txt.split()),'images':len(pimgs),'videos':vids,'file':f'pages/{s}.md'})
json.dump(inv,open('inventory.json','w'),indent=1)
print("done",len(inv),"pages")
