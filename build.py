from pathlib import Path
import os
from urllib.parse import unquote
import json, re, shutil, subprocess, html as htmlmod
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
import mistune
from PIL import Image

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'site_src'
DIST=ROOT/'dist'
if DIST.exists(): shutil.rmtree(DIST)
DIST.mkdir(parents=True)
DATA=json.loads((SRC/'data/pages.json').read_text())
SITE=json.loads((SRC/'data/site.json').read_text())
NAV=SITE['nav']
section_home={k: {'The Club':'oucc/about.html','Play':'coaching/howtoplay.html','Cuppers':'college/cuppersintro.html','Varsity':'varsity/index.html','Fixtures':'fixtures/index.html','More':'members.html'}[k] for k in NAV}
env=Environment(loader=FileSystemLoader(str(SRC/'templates')),autoescape=select_autoescape(['html']))
md=mistune.create_markdown(escape=False, plugins=['strikethrough','table'])
used_images=set()

# copy non-content public assets needed by all pages
for rel in ['OUCC_CREST.png','favico.ico','images/partners/sipsmith-small.png']:
    s=SRC/'assets'/rel; t=DIST/rel; t.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(s,t)
for rel in ['ouacc-modern.css','ouacc.js']:
    s=SRC/'static'/rel; t=DIST/rel; t.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(s,t)

# render content pages
for pg in DATA:
    path=pg['path']
    out=Path(path)
    out.parent and (DIST/out.parent).mkdir(parents=True,exist_ok=True)
    if path=='index.html': continue
    cpath=SRC/'content'/out.with_suffix('.md')
    raw=cpath.read_text(errors='replace') if cpath.exists() else ''
    body=md(raw)
    # fix internal links in content to maintain relative path and remove stale comment remnants
    body=body.replace('\\<!--','').replace('<!--','')
    soup=BeautifulSoup(body,'html.parser')
    for styled in soup.find_all(style=True):
        del styled['style']
    for img in soup.find_all('img'):
        if not img.get('alt'): img['alt'] = ''
    # Legacy decorative map/photo on the beginner page is unnecessary in the text flow.
    if path == 'coaching/howtoplay.html':
        for img in soup.find_all('img'):
            if 'lawn.gif' in (img.get('src') or ''): img.decompose()
    toc=[]
    for h in soup.find_all(['h2','h3']):
        if not h.get('id'):
            slug=re.sub(r'[^a-z0-9]+','-',h.get_text(' ',strip=True).lower()).strip('-') or 'section'
            base=slug; n=2
            while any(x['id']==slug for x in toc): slug=f'{base}-{n}'; n+=1
            h['id']=slug
        if h.name=='h2': toc.append({'id':h['id'],'text':h.get_text(' ',strip=True)})
    # add standard image attributes and collect local refs
    for img in soup.find_all('img'):
        img['loading']=img.get('loading','lazy')
        img['decoding']='async'
        src=img.get('src','')
        if src and not re.match(r'^(https?:|data:|#)',src): used_images.add((out.parent/src).as_posix())
    body='<!doctype html>' + str(soup)
    root='../'*len(out.parent.parts)
    canonical=SITE['base_url']+path
    og=SITE['base_url']+'images/editorial/playing_in_the_parks.jpg'
    html=env.get_template('page.html').render(title=pg['title'],description=pg['description'] or pg['dek'],dek=pg['dek'],path=path,section=pg['section'],archive=pg['archive'],root=root,canonical=canonical,og_image=og,body=body,toc=toc,nav=NAV,section_home=section_home)
    (DIST/out).write_text(html)

# homepage
root=''
canonical=SITE['base_url']+'index.html'
html=env.get_template('home.html').render(title='OUACC',description='Oxford University Association Croquet Club, established in 1867.',path='index.html',section='Home',root=root,canonical=canonical,og_image=SITE['base_url']+'images/editorial/playing_in_the_parks.jpg',nav=NAV,section_home=section_home)
(DIST/'index.html').write_text(html)

# search page
html=env.get_template('search.html').render(title='Search OUACC',description='Search the public OUACC website.',path='search.html',section='More',root='',canonical=SITE['base_url']+'search.html',og_image=SITE['base_url']+'images/editorial/playing_in_the_parks.jpg',nav=NAV,section_home=section_home)
(DIST/'search.html').write_text(html)

# responsive image optimization: create webp copies for used editorial photos that exist in source
for src_rel in list(used_images):
    src=SRC/'assets'/unquote(src_rel)
    if not src.exists() or src.suffix.lower() in {'.gif','.ico','.svg'}: continue
    try:
        im=Image.open(src).convert('RGB')
        # keep originals only when used directly, but cap derivative width at 1400
        maxw=min(im.width,1400)
        if maxw < im.width:
            im=im.resize((maxw,round(im.height*maxw/im.width)),Image.LANCZOS)
        target=DIST/src_rel
        target.parent.mkdir(parents=True,exist_ok=True)
        im.save(target,quality=82,optimize=True)
        webp=target.with_suffix('.webp')
        im.save(webp,'WEBP',quality=82,method=6)
    except Exception:
        target=DIST/src_rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,target)

# explicit editorial home assets
for rel in ['images/editorial/playing_in_the_parks.jpg','images/editorial/winners_cuppers_2026.jpg','images/editorial/varsity_1983.jpg','images/editorial/coaching.jpg','images/editorial/playing_all_balls.jpg']:
    src=SRC/'assets'/unquote(rel)
    if src.exists():
        im=Image.open(src).convert('RGB'); maxw=min(im.width,1400)
        if maxw<im.width: im=im.resize((maxw,round(im.height*maxw/im.width)),Image.LANCZOS)
        target=DIST/rel; target.parent.mkdir(parents=True,exist_ok=True); im.save(target,quality=82,optimize=True); im.save(target.with_suffix('.webp'),'WEBP',quality=82,method=6)

# Convert local raster images to responsive picture elements where a WebP derivative exists.
for hp in DIST.rglob('*.html'):
    soup=BeautifulSoup(hp.read_text(errors='replace'),'html.parser')
    for img in soup.find_all('img'):
        src=img.get('src','')
        if not src or re.match(r'^(https?:|data:|#)',src): continue
        src_path=(hp.parent/src).resolve()
        try: rel_path=src_path.relative_to(DIST.resolve())
        except ValueError: continue
        wp=src_path.with_suffix('.webp')
        if wp.exists() and src_path.suffix.lower() in {'.jpg','.jpeg','.png'}:
            pic=soup.new_tag('picture')
            source=soup.new_tag('source',type='image/webp',srcset=os.path.relpath(wp, hp.parent).replace('\\','/'))
            pic.append(source); img.wrap(pic)
    hp.write_text('<!doctype html>\n'+str(soup))

# Copy linked local assets in content, including PDFs, photos and maps. Respect original paths.
for rel in list(used_images):
    src=SRC/'assets'/unquote(rel)
    if src.exists():
        target=DIST/rel; target.parent.mkdir(parents=True,exist_ok=True)
        if src.suffix.lower() not in {'.jpg','.jpeg','.png','.gif','.webp'} or not target.exists(): shutil.copy2(src,target)

# Copy local links to documents/PDFs referenced in generated HTML.
for hp in DIST.rglob('*.html'):
    s=BeautifulSoup(hp.read_text(errors='replace'),'html.parser')
    for a in s.find_all('a',href=True):
        href=a['href']
        if re.match(r'^(https?:|mailto:|#|javascript:)',href): continue
        dest=(hp.parent/unquote(href)).resolve()
        try: rel=dest.relative_to(DIST.resolve())
        except ValueError: continue
        if not dest.exists():
            src=SRC/'assets'/unquote(str(rel))
            if src.exists(): dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)

# Ensure every local image, document, stylesheet and script referenced by the generated HTML is present.\n# This also handles legacy filenames containing spaces or URL-encoded brackets.\nfrom urllib.parse import unquote\nfor hp in DIST.rglob('*.html'):\n    soup=BeautifulSoup(hp.read_text(errors='replace'),'html.parser')\n    for tag, attr in [('img','src'),('a','href')]:\n        for el in soup.find_all(tag):\n            u=el.get(attr)\n            if not u or re.match(r'^(https?:|mailto:|tel:|javascript:|data:|#)',u): continue\n            raw=unquote(u.split('#')[0].split('?')[0])\n            if not raw: continue\n            dest=(hp.parent/raw).resolve()\n            try:\n                rel_dest=dest.relative_to(DIST.resolve())\n            except ValueError:\n                continue\n            if not dest.exists():\n                src=SRC/'assets'/rel_dest\n                if src.exists():\n                    dest.parent.mkdir(parents=True,exist_ok=True)\n                    shutil.copy2(src,dest)\n            if tag=='img' and ('paypalobjects.com' in (u or '') or 'pixel.gif' in (u or '')):\n                el['alt']=''\n        # remove accidental duplicate picture serialization marker is not relevant\n    hp.write_text('<!doctype html>\\n'+str(soup))\n\n# Final asset sweep. Resolve URL-encoded paths before locating source files.
for hp in DIST.rglob('*.html'):
    soup=BeautifulSoup(hp.read_text(errors='replace'),'html.parser')
    for tag, attr in [('img','src'),('a','href'),('link','href'),('script','src')]:
        for el in soup.find_all(tag):
            u=el.get(attr)
            if not u or re.match(r'^(https?:|mailto:|tel:|javascript:|data:|#)',u): continue
            raw=unquote(u.split('#')[0].split('?')[0])
            dest=(hp.parent/raw).resolve()
            if dest.exists(): continue
            try: rel_dest=dest.relative_to(DIST.resolve())
            except ValueError: continue
            src=SRC/'assets'/rel_dest
            if src.exists():
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(src,dest)

# Search index from main content only.
search=[]
for pg in DATA:
    if pg['path']=='search.html': continue
    p=DIST/pg['path']
    if not p.exists(): continue
    s=BeautifulSoup(p.read_text(errors='replace'),'html.parser')
    main=s.find('article',id='article-content') or s.find('main')
    text=' '.join(main.stripped_strings) if main else ''
    text=re.sub(r'\s+',' ',text).strip()
    if len(text)>4000: text=text[:4000]
    search.append({'title':pg['title'],'path':pg['path'],'section':pg['section'],'text':text})
(DIST/'search-index.json').write_text(json.dumps(search,ensure_ascii=False,indent=2))

# Robots, sitemap, and site map metadata.
(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+SITE['base_url']+'sitemap.xml\n')
from datetime import date
urls=[]
for pg in DATA:
    if pg['path']=='404.html': continue
    urls.append(SITE['base_url']+pg['path'])
urls.append(SITE['base_url']+'search.html')
xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in dict.fromkeys(urls): xml.append(f'  <url><loc>{u}</loc></url>')
xml.append('</urlset>')
(DIST/'sitemap.xml').write_text('\n'.join(xml)+'\n')

# custom 404
(DIST/'404.html').write_text((SRC/'templates/404.html').read_text().replace('{{ root }}','')) if (SRC/'templates/404.html').exists() else None
print(f'Built {len(list(DIST.rglob("*.html")))} HTML pages')
