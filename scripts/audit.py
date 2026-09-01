from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup
import json, re, sys

ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
htmls=sorted(ROOT.rglob('*.html'))
issues=[]
for p in htmls:
    rel=p.relative_to(ROOT).as_posix(); text=p.read_text(errors='replace'); s=BeautifulSoup(text,'html.parser')
    if not text.lstrip().lower().startswith('<!doctype html>'): issues.append((rel,'missing HTML5 doctype'))
    if not s.find('main'): issues.append((rel,'missing main element'))
    if s.find(style=True): issues.append((rel,'inline style attribute'))
    if '<!--' in text: issues.append((rel,'HTML comment marker in generated output'))
    if '/~croquet/' in text: issues.append((rel,'legacy /~croquet/ URL'))
    title=s.title.get_text(' ',strip=True) if s.title else ''
    if not title: issues.append((rel,'missing title'))
    if not s.find('meta',attrs={'name':'description'}): issues.append((rel,'missing meta description'))
    for img in s.find_all('img'):
        if 'alt' not in img.attrs: issues.append((rel,'image missing alt attribute: '+str(img.get('src'))))
    for tag,attr in [('a','href'),('img','src'),('link','href'),('script','src')]:
        for el in s.find_all(tag):
            u=el.get(attr)
            if not u or re.match(r'^(https?:|mailto:|tel:|javascript:|data:|#)',u): continue
            raw=unquote(u.split('#')[0].split('?')[0])
            if not raw: continue
            dest=(p.parent/raw).resolve()
            if not dest.exists(): issues.append((rel,f'broken {tag}: {u}'))
# global expectations
alltext='\n'.join(p.read_text(errors='replace') for p in htmls)
for phrase in ['Oxford University Association Croquet Club, with competitive play, coaching, college competition and a long institutional history.','style="','/~croquet/']:
    if phrase in alltext: issues.append(('GLOBAL','forbidden/legacy text: '+phrase))
# search index
idx=ROOT/'search-index.json'
if not idx.exists(): issues.append(('GLOBAL','missing search-index.json'))
else:
    data=json.loads(idx.read_text())
    public=[p for p in htmls if p.name not in {'404.html','search.html'}]
    if len(data) != len(public): issues.append(('GLOBAL',f'search index count {len(data)} != public page count {len(public)}'))
# sitemap
if not (ROOT/'sitemap.xml').exists(): issues.append(('GLOBAL','missing sitemap.xml'))
if not (ROOT/'robots.txt').exists(): issues.append(('GLOBAL','missing robots.txt'))

print(f'HTML pages checked: {len(htmls)}')
print(f'Issues found: {len(issues)}')
for issue in issues: print(issue)
if issues: sys.exit(1)
