#!/usr/bin/env python3
"""Validate published-document invariants for the bilingual SEO expansion."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit,unquote
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT/'dist' if (ROOT/'dist').is_dir() else ROOT);parser.add_argument('--mode',choices=['review','production'],default='review');args=parser.parse_args()
inventory=json.loads((ROOT/'content/page-inventory.json').read_text())
projects=json.loads((ROOT/'content/portfolio.json').read_text())
class Document(HTMLParser):
    def __init__(self,text):
        super().__init__();self.nodes=[];self.stack=[];self.errors=[];self.feed(text)
        if self.stack:self.errors.append('Unclosed elements: '+str([n['tag'] for n in self.stack]))
    def handle_starttag(self,tag,attrs):
        n={'tag':tag,'attrs':dict(attrs),'text':''};self.nodes.append(n)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(n)
    def handle_endtag(self,tag):
        if not self.stack or self.stack[-1]['tag']!=tag:self.errors.append('Mismatched closing '+tag)
        else:self.stack.pop()
    def handle_data(self,data):
        for n in self.stack:n['text']+=data+' '
    def tags(self,tag):return [n for n in self.nodes if n['tag']==tag]
    def meta(self,key):return [n['attrs'].get('content') for n in self.tags('meta') if n['attrs'].get('name')==key or n['attrs'].get('property')==key]
errors=[];docs={};titles=[];image_count=0
for item in inventory:
    file=args.root/item['path']
    if not file.exists():errors.append(item['path']+': file missing');continue
    d=Document(file.read_text());docs[item['path']]=d
    errors.extend(item['path']+': '+e for e in d.errors)
    ids=[n['attrs']['id'] for n in d.nodes if n['attrs'].get('id')]
    errors.extend(item['path']+': duplicate id '+i for i,c in Counter(ids).items() if c>1)
    if len(d.tags('h1'))!=1:errors.append(item['path']+': expected one H1')
    title=d.tags('title')
    if len(title)!=1 or not title[0]['text'].strip():errors.append(item['path']+': invalid title')
    else:titles.append(title[0]['text'].strip())
    for key in ['description','robots','og:title','og:description','og:image','twitter:card']:
        if len(d.meta(key))!=1 or not d.meta(key)[0]:errors.append(item['path']+': missing or duplicate '+key)
    expected='noindex,nofollow' if args.mode=='review' else 'index,follow,max-image-preview:large'
    if d.meta('robots')!=[expected]:errors.append(item['path']+': unsafe environment robots')
    links=[n['attrs'] for n in d.tags('link')]
    if [a.get('href') for a in links if a.get('rel')=='canonical']!=[item['canonical']]:errors.append(item['path']+': canonical mismatch')
    alternates={a.get('hreflang'):a.get('href') for a in links if a.get('rel')=='alternate'}
    for lang,path in zip(['es','en'],item['pair']):
        target='https://katia.solutions/'+('' if path=='index.html' else path)
        if alternates.get(lang)!=target:errors.append(item['path']+': hreflang mismatch')
    if alternates.get('x-default')!=alternates.get('es'):errors.append(item['path']+': x-default mismatch')
    if d.tags('html')[0]['attrs'].get('lang')!=item['lang']:errors.append(item['path']+': language mismatch')
    for img in d.tags('img'):
        image_count+=1
        if not all(k in img['attrs'] for k in ['alt','width','height']):errors.append(item['path']+': image metadata missing')
    graphs=[]
    for n in d.tags('script'):
        if n['attrs'].get('type')=='application/ld+json':
            try:graphs.extend(json.loads(n['text'])['@graph'])
            except (ValueError,KeyError):errors.append(item['path']+': invalid graph JSON')
    types={n['@type'] for n in graphs}
    if not {'Organization','WebSite'}.issubset(types):errors.append(item['path']+': missing company identity')
    if item['kind']=='service' and 'Service' not in types:errors.append(item['path']+': missing Service')
    if item['kind']=='project' and 'CreativeWork' not in types:errors.append(item['path']+': missing project entity')
    for n in d.nodes:
        for idref in ['aria-controls','aria-labelledby','aria-describedby']:
            for target in n['attrs'].get(idref,'').split():
                if target not in ids:errors.append(item['path']+': missing ARIA target '+target)
if len(titles)!=len(set(titles)):errors.append('Duplicate page titles')
for item in inventory:
    d=docs.get(item['path'])
    if not d:continue
    for n in d.nodes:
        a=n['attrs'];refs=[]
        if n['tag'] in ['a','script','img','link']:
            ref=a.get('src') if n['tag'] in ['script','img'] else a.get('href')
            if ref:refs.append(ref)
        if n['tag']=='img':refs.extend(x.strip().split()[0] for x in a.get('srcset','').split(',') if x.strip())
        if n['tag']=='meta' and (a.get('property')=='og:image' or a.get('name')=='twitter:image'):refs.append(a['content'].replace('https://katia.solutions','',1))
        for ref in refs:
            u=urlsplit(ref)
            if u.scheme or u.netloc:continue
            rel=unquote(u.path).lstrip('/') or (item['path'] if not u.path else 'index.html')
            if u.path=='/':rel='index.html'
            target=args.root/rel
            if not target.is_file():errors.append(item['path']+': missing local target '+ref);continue
            if u.fragment and target.suffix=='.html':
                other=docs.get(rel) or Document(target.read_text())
                ids={x['attrs'].get('id') for x in other.nodes}
                if unquote(u.fragment) not in ids:errors.append(item['path']+': missing anchor '+ref)
sitemap=ET.parse(args.root/'sitemap.xml')
urls=[n.text for n in sitemap.findall('.//{*}loc')]
if len(urls)!=len(set(urls)):errors.append('Duplicate sitemap URLs')
if not set(i['canonical'] for i in inventory).issubset(urls):errors.append('Sitemap omits new canonical URLs')
robots=(args.root/'robots.txt').read_text()
if args.mode=='review' and robots.strip()!='User-agent: *\nDisallow: /':errors.append('Review robots changed')
if args.mode=='production':
    groups={};agents=[];rules=[]
    for line in robots.splitlines()+['User-agent: END']:
        if line.startswith('User-agent:'):
            if rules:
                for agent in agents:groups.setdefault(agent,[]).extend(rules)
                agents=[];rules=[]
            agents.append(line.split(':',1)[1].strip())
        elif line.startswith(('Allow:','Disallow:')):rules.append(line.strip())
    for agent,rules in groups.items():
        if 'Allow: /' in rules and 'Disallow: /' in rules:errors.append('Conflicting production rules: '+agent)
    for agent in ['Googlebot','Bingbot','OAI-SearchBot','Claude-SearchBot','PerplexityBot']:
        if 'Allow: /' not in groups.get(agent,[]):errors.append('Search bot not allowed: '+agent)
if errors:
    raise SystemExit('\n'.join(sorted(set(errors))))
print(f'SEO checks passed: {len(inventory)} pages, {image_count} images, {len(urls)} sitemap URLs, mode={args.mode}.')
