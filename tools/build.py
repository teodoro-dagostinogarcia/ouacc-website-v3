from pathlib import Path
import argparse, json, re, datetime, html
from bs4 import BeautifulSoup
import mistune
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'site_src'
CONTENT=SRC/'content'
TEMPLATES=SRC/'templates'
DATA=json.loads((SRC/'data'/'site.json').read_text(encoding='utf-8'))

SECTIONS=[
 {'key':'club','label':'The Club','index':'oucc/about.html','items':[('About the Club','oucc/about.html'),('Committee','oucc/committee.html'),('Membership','oucc/join.html'),('Find us','oucc/directions.html'),('Documents','oucc/documents.html'),('History','oucc/history.html')]},
 {'key':'play','label':'Play','index':'coaching/howtoplay.html','items':[('How to play','coaching/howtoplay.html'),('Intermediate coaching','coaching/intermediate.html'),('Handicapping','coaching/handicapping.html')]},
 {'key':'cuppers','label':'Cuppers','index':'college/cuppersintro.html','items':[('Cuppers overview','college/cuppersintro.html'),('Entry','college/cupperssignup.html'),('Rules','college/cuppersrules.html'),('Results','college/cuppersresults.html'),('FAQ','college/cuppersfaq.html'),('Archive','college/cuppersarchive.html')]},
 {'key':'varsity','label':'Varsity','index':'varsity/index.html','items':[('Varsity overview','varsity/index.html'),('Oxford team','varsity/oxfordteam.html'),('Results','varsity/varsity_results.html'),('Match reports','varsity/matchreports.html'),('Photographs','varsity/photos.html'),('Half Blues','varsity/halfblue.html'),('Archive','varsity/archive.html')]},
 {'key':'fixtures','label':'Fixtures','index':'fixtures/index.html','items':[('Fixtures','fixtures/index.html'),('Student Championships','fixtures/studentchamps.html')]},
 {'key':'more','label':'More','index':'members.html','items':[('Partnerships','partnerships.html'),('Partner with us','partnerships/benefits.html'),('Members area','members.html'),('Alumni','alumni.html')]},
]
section_map={u:(s['key'],s['label'],[(l,u2) for l,u2 in s['items']]) for s in SECTIONS for _,u in s['items']}

def section_for_url(url):
    if url in section_map:
        return section_map[url]
    if url.startswith('oucc/'):
        s=SECTIONS[0]; return (s['key'],s['label'],[(l,u) for l,u in s['items']])
    if url.startswith('coaching/'):
        s=SECTIONS[1]; return (s['key'],s['label'],[(l,u) for l,u in s['items']])
    if url.startswith('college/'):
        s=SECTIONS[2]; return (s['key'],s['label'],[(l,u) for l,u in s['items']])
    if url.startswith('varsity/'):
        s=SECTIONS[3]; return (s['key'],s['label'],[(l,u) for l,u in s['items']])
    if url.startswith('fixtures/'):
        s=SECTIONS[4]; return (s['key'],s['label'],[(l,u) for l,u in s['items']])
    if url.startswith('alumni') or url.startswith('partnerships') or url == 'members.html':
        s=SECTIONS[5]; return (s['key'],s['label'],[(l,u) for l,u in s['items']])
    return ('','',[])

# Parse frontmatter without adding another dependency.
def read_md(p):
    text=p.read_text(encoding='utf-8')
    meta={}
    if text.startswith('---'):
        _, head, body=text.split('---',2)
        for line in head.strip().splitlines():
            if ':' in line:
                k,v=line.split(':',1); meta[k.strip()]=v.strip()
        text=body.lstrip('\n')
    return meta,text

env=Environment(loader=FileSystemLoader(str(TEMPLATES)),autoescape=select_autoescape(['html']))
md=mistune.create_markdown(escape=False, plugins=['table','strikethrough','url'])

def load_content():
    records=[]
    for p in CONTENT.rglob('*.md'):
        rel=p.relative_to(CONTENT).with_suffix('.html').as_posix()
        meta,body=read_md(p)
        html_body=md(body)
        s=BeautifulSoup(html_body,'html.parser')
        # Assign stable ids to headings for TOC.
        used=set(); toc=[]
        for h in s.find_all(['h2','h3']):
            label=h.get_text(' ',strip=True)
            slug=re.sub(r'[^a-z0-9]+','-',label.lower()).strip('-') or 'section'
            base=slug; i=2
            while slug in used:
                slug=f'{base}-{i}'; i+=1
            used.add(slug); h['id']=slug
            if h.name=='h2': toc.append({'id':slug,'label':label})
        records.append({'url':rel,'meta':meta,'html':str(s),'toc':toc})
    return records

def root_for(rel):
    return '../'* (len(Path(rel).parts)-1)

def collect_search(records):
    items=[]
    for r in records:
        if r['url'] in {'search.html','404.html'}: continue
        soup=BeautifulSoup(r['html'],'html.parser')
        text=' '.join(soup.get_text(' ',strip=True).split())
        items.append({'title':r['meta'].get('title',r['url']),'url':r['url'],'text':text})
    return items

def rewrite_preview_links(html_text, root):
    # Keep links relative and leave assets untouched. Ensure any generated links are relative to page.
    return html_text

def rewrite_production_links(html_text):
    # Preserve the historic .shtml URL convention for Oxford hosting.
    def repl(m):
        attr, q, val = m.group(1), m.group(2), m.group(3)
        if val.startswith(('http:','https:','mailto:','tel:','#','javascript:','data:')): return m.group(0)
        if val.endswith('.html') and Path(val).name != 'search.html':
            return attr+q+val[:-5]+'.shtml'+q
        return m.group(0)
    return re.sub(r'((?:href|src)=)(["\'])([^"\']+)\2', repl, html_text)

def nav_for(current):
    groups=[]
    current_group=''
    for s in SECTIONS:
        items=[{'label':l,'url':u} for l,u in s['items']]
        skey,slabel,pairs=section_for_url(current)
        if current and skey==s['key']: current_group=s['key']
        groups.append({'key':s['key'],'label':s['label'],'index':s['index'],'items':items})
    skey,slabel,pairs=section_for_url(current)
    side=[{'label':l,'url':u} for l,u in pairs]
    return groups,current_group,slabel,side

def build(target):
    out=ROOT/('public' if target=='preview' else 'production')
    if out.exists():
        import shutil; shutil.rmtree(out)
    out.mkdir()
    # Copy static assets
    import shutil
    shutil.copytree(SRC/'static', out, dirs_exist_ok=True)
    records=load_content()
    # homepage bespoke
    homefrag=(CONTENT/'home.htmlfrag').read_text(encoding='utf-8')
    home_body='<main id="main-content">'+homefrag.replace('src="images/','src="images/')+'</main>'
    if target=='production': home_body=rewrite_production_links(home_body)
    t=env.get_template('base.html')
    common={'nav_groups':nav_for('')[0],'current':'home','current_group':'','year':datetime.date.today().year,'root':'','home_url':'index.shtml' if target=='production' else 'index.html','search_script':False}
    home_html=t.render(title=DATA['name'],description=DATA['name']+' , established in 1867.',body=home_body,**common)
    if target=='production':
        home_html=rewrite_production_links(home_html)
        (out/'index.shtml').write_text(home_html,encoding='utf-8')
    else:
        (out/'index.html').write_text(home_html,encoding='utf-8')
    # all markdown pages
    for r in records:
        url=r['url']; meta=r['meta']
        if meta.get('template') in {'search','404'}: continue
        groups,cgroup,slabel,side=nav_for(url)
        root=root_for(url)
        content=r['html']
        if target=='production': content=rewrite_production_links(content)
        body=env.get_template('page.html').render(
            root=root,title=meta.get('title',url),description=meta.get('description',''),eyebrow=meta.get('eyebrow',''),
            section=meta.get('section',''),section_label=slabel or meta.get('section') or 'OUACC',content=content,toc=r['toc'],
            side_items=side, current=url,current_group=cgroup,search_query='',nav_groups=groups)
        full=t.render(title=meta.get('title',url)+' | OUACC',description=meta.get('description',''),body=body,
                      nav_groups=groups,current=url,current_group=cgroup,year=datetime.date.today().year,root=root,home_url=(root+'index.shtml' if target=='production' else root+'index.html'),search_script=False)
        if target=='production':
            full=rewrite_production_links(full)
            dest=out/Path(url).with_suffix('.shtml')
        else:
            dest=out/url
        dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(full,encoding='utf-8')
    # search
    groups,_,_,_=nav_for('search.html')
    search_body=env.get_template('search.html').render()
    full=t.render(title='Search | OUACC',description='Search the OUACC website.',body=search_body,nav_groups=groups,current='search.html',current_group='',year=datetime.date.today().year,root='',home_url=('index.shtml' if target=='production' else 'index.html'),search_script=True)
    if target=='production': full=rewrite_production_links(full)
    (out/'search.html').write_text(full,encoding='utf-8')
    # 404
    four=t.render(title='Page not found | OUACC',description='The page you were looking for could not be found.',body=env.get_template('404.html').render(root='',home_url=('index.shtml' if target=='production' else 'index.html')),nav_groups=groups,current='404.html',current_group='',year=datetime.date.today().year,root='',home_url=('index.shtml' if target=='production' else 'index.html'),search_script=False)
    if target=='production':
        four=rewrite_production_links(four)
    (out/'404.html').write_text(four,encoding='utf-8')
    if target=='production':
        (out/'404.shtml').write_text(four,encoding='utf-8')
    # search index and sitemap
    idx=collect_search(records)
    (out/'search-index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf-8')
    canonical=DATA['base_url'] if target=='preview' else ''
    urls=[]
    for r in records:
        u=r['url']
        urls.append((canonical+u) if canonical else u[:-5]+'.shtml')
    urls.append(canonical if canonical else 'index.shtml')
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{html.escape(u)}</loc></url>\n' for u in urls) + '</urlset>\n',encoding='utf-8')
    (out/'robots.txt').write_text('User-agent: *\nAllow: /\n' + (f'Sitemap: {canonical}sitemap.xml\n' if canonical else ''),encoding='utf-8')

    if target=='production':
        (out/'DEPLOYMENT.txt').write_text("Upload the contents of this production folder to the University's web directory.\nThe .shtml files preserve the historic server URL convention.\nThe generated search.html is a new page and does not replace an historic .shtml page.\nDo not upload site_src or tools.\n",encoding='utf-8')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--target',choices=['preview','production'],default='preview'); args=ap.parse_args(); build(args.target)
