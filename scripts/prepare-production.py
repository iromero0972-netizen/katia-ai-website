#!/usr/bin/env python3
"""Create a local production candidate by overlaying the reviewed site on an existing checkout.
No upload, push, DNS change, search submission or deployment is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/'dist' if (ROOT/'dist').is_dir() else ROOT
parser=argparse.ArgumentParser()
parser.add_argument('--baseline',type=Path,required=True,help='Current checkout of the production repository')
parser.add_argument('--output',type=Path,required=True,help='New empty candidate directory')
args=parser.parse_args()
base=args.baseline.resolve();out=args.output.resolve()
assert base.is_dir() and (base/'CNAME').read_text().strip()=='katia.solutions','Wrong baseline domain'
assert base!=ROOT and out not in [ROOT,DIST,base] and ROOT not in out.parents and base not in out.parents,'Use a separate output directory'
assert not out.exists(),'Output must not exist; never overwrite a candidate'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=base,text=True).strip(),'Baseline must be clean'
baseline_sha=subprocess.check_output(['git','rev-parse','--verify','HEAD'],cwd=base,text=True).strip()
migration=json.loads((ROOT/'deployment/migration.json').read_text())
assert baseline_sha==migration['baseline_commit'],'Baseline changed: re-audit and update migration.json before preparing a release'
assert (base/'sitemap.xml').is_file(),'Baseline sitemap is required to preserve existing URLs'
shutil.copytree(base,out,ignore=shutil.ignore_patterns('.git','node_modules','.env','.env.*'))
for item in DIST.iterdir():
    if item.name.startswith('.') or item.name in ['robots.txt','sitemap.xml','node_modules','scripts','content','deployment','legacy']:continue
    # Do not introduce the unused earlier hero film; an existing public copy is retained by the baseline.
    if item.is_dir():shutil.copytree(item,out/item.name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('hero-glass.mp4') if item.name=='assets' else None)
    else:shutil.copy2(item,out/item.name)
for folder in ['content','scripts','deployment']:
    shutil.copytree(ROOT/folder,out/folder,dirs_exist_ok=True)
(out/'.github/workflows').mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'deployment/indexnow.yml',out/'.github/workflows/indexnow.yml')
inventory=json.loads((ROOT/'content/page-inventory.json').read_text())
for page in inventory:
    p=out/page['path'];text=p.read_text()
    text,n=re.subn(r'<meta name="robots" content="[^"]*">','<meta name="robots" content="index,follow,max-image-preview:large">',text)
    assert n==1,f'Robots metadata missing or duplicated: {p}'
    if page['path'] in ['apps.html','business-apps.html']:
        # Keep bookmarks to the original app capabilities, process and integration sections.
        for section,anchor in [('detail-section soft','capacidades'),('detail-section','proceso'),('detail-section soft','integraciones')]:
            text,n=re.subn('<section class="'+section+'">','<section class="'+section+'" id="'+anchor+'">',text,count=1)
            assert n==1,f'Missing app section for preserved anchor: {anchor}'
    # Retain public ownership checks when a redesigned document replaces an existing one.
    old=base/page['path']
    if old.exists():
        tags=re.findall(r'<meta\b[^>]*(?:name="google-site-verification"|name="msvalidate\.01")[^>]*>',old.read_text())
        for tag in tags:
            if tag not in text:text=text.replace('</head>',tag+'</head>',1)
    p.write_text(text)
shutil.copy2(ROOT/'deployment/robots.production.txt',out/'robots.txt')
shutil.copy2(ROOT/'deployment/llms.production.txt',out/'llms.txt')
# Retain original URL entries and lastmod values. New/changed pages are added without fictitious dates.
ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns)
xhtml='http://www.w3.org/1999/xhtml';ET.register_namespace('xhtml',xhtml)
tree=ET.parse(base/'sitemap.xml');root=tree.getroot()
existing={n.find('{*}loc').text:n for n in root.findall('{*}url')}
for page in inventory:
    canonical=page['canonical']
    if canonical in existing:
        old=existing[canonical]
        for tag in ['lastmod','priority','changefreq']:
            for n in list(old.findall('{*}'+tag)):old.remove(n)
    else:
        n=ET.SubElement(root,'{'+ns+'}url');ET.SubElement(n,'{'+ns+'}loc').text=canonical
        existing[canonical]=n
    # Replace legacy query-string language alternatives with the reviewed ES/EN routes.
    entry=existing[canonical]
    for link in list(entry.findall('{'+xhtml+'}link')):entry.remove(link)
    alternatives=[('es',page['pair'][0]),('en',page['pair'][1]),('x-default',page['pair'][0])]
    for language,relative in alternatives:
        address='https://katia.solutions/'+('' if relative=='index.html' else relative)
        ET.SubElement(entry,'{'+xhtml+'}link',{'rel':'alternate','hreflang':language,'href':address})
for address in existing:
    assert address.startswith('https://katia.solutions/'),'Unexpected sitemap host'
    relative=address.removeprefix('https://katia.solutions/') or 'index.html'
    assert (out/relative).is_file(),f'Preserved sitemap URL missing: {address}'
tree.write(out/'sitemap.xml',encoding='utf-8',xml_declaration=True)
for relative in migration['preserved_routes']:
    assert (out/relative).read_bytes()==(base/relative).read_bytes(),f'Legacy route changed: {relative}'
assert (out/'CNAME').read_bytes()==(base/'CNAME').read_bytes()
record={'baseline_commit':baseline_sha,'review_source_commit':subprocess.check_output(['git','rev-parse','--verify','HEAD'],cwd=ROOT,text=True).strip(),'source_has_uncommitted_changes':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),'new_or_updated_pages':len(inventory),'sitemap_urls':len(existing),'preserved_routes':migration['preserved_routes'],'published':False}
(out/'deployment/candidate-record.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'candidate':str(out),'pages':len(inventory),'sitemap_urls':len(existing),'published':False}))
