from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
import sys, re

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'public').resolve()
files = [p for p in ROOT.rglob('*') if p.suffix.lower() in {'.html', '.shtml'}]
errors = []
for p in files:
    text = p.read_text(encoding='utf-8', errors='replace')
    soup = BeautifulSoup(text, 'html.parser')
    if not text.lstrip().lower().startswith('<!doctype html>'):
        errors.append(f'No HTML5 doctype: {p.relative_to(ROOT)}')
    if p.name not in {'404.html', '404.shtml'} and not soup.find('main'):
        errors.append(f'Missing main landmark: {p.relative_to(ROOT)}')
    if soup.find(attrs={'style': True}):
        errors.append(f'Inline style found: {p.relative_to(ROOT)}')
    for img in soup.find_all('img'):
        if not img.get('alt'):
            errors.append(f'Missing alt text: {p.relative_to(ROOT)}')
    for tag, attr in [('a','href'),('img','src'),('link','href'),('script','src')]:
        for el in soup.find_all(tag):
            val = el.get(attr)
            if not val:
                continue
            val = unquote(val.split('#',1)[0].split('?',1)[0])
            if not val or val.startswith(('http://','https://','mailto:','tel:','javascript:','data:','#')):
                continue
            target = (p.parent / val).resolve() if not val.startswith('/') else (ROOT / val.lstrip('/')).resolve()
            if not target.exists():
                errors.append(f'Broken reference: {p.relative_to(ROOT)} -> {val}')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'OK: {len(files)} HTML/SHTML pages checked in {ROOT}')
