#!/usr/bin/env python3
"""Prepare IndexNow from the real sitemap; send only in the production repository on main."""
import argparse
import json
import os
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--submit',action='store_true');args=parser.parse_args()
sitemap=ROOT/'sitemap.xml'
if not sitemap.exists():sitemap=ROOT/'dist/sitemap.xml'
expected={n.text for n in ET.parse(sitemap).findall('.//{*}loc')}
assert expected and all(u.startswith('https://katia.solutions/') for u in expected),'Unexpected sitemap host'
if not args.submit:
    print(json.dumps({'mode':'dry-run','urls':len(expected),'submission_sent':False}));raise SystemExit(0)
assert os.environ.get('GITHUB_REF')=='refs/heads/main','Submission is restricted to main'
assert os.environ.get('GITHUB_REPOSITORY')=='iromero0972-netizen/katia-ai-website','Wrong production repository'
assert (ROOT/'CNAME').read_text().strip()=='katia.solutions','Wrong domain'
key_file=ROOT/'53057d35a5d8f948d8ded2825b6b9e75.txt'
key=key_file.read_text().strip()
assert key and key_file.stem==key,'IndexNow ownership key mismatch'
with urllib.request.urlopen('https://katia.solutions/sitemap.xml',timeout=30) as response:
    live={n.text for n in ET.fromstring(response.read()).findall('.//{*}loc')}
assert expected.issubset(live),'The domain has not published this sitemap yet. Retry after publication.'
with urllib.request.urlopen('https://katia.solutions/',timeout=30) as response:
    html=response.read().decode('utf-8');header=response.headers.get('X-Robots-Tag','')
assert 'noindex' not in header.lower() and 'content="noindex' not in html.lower(),'Public home is not indexable'
payload={'host':'katia.solutions','key':key,'keyLocation':'https://katia.solutions/'+key_file.name,'urlList':sorted(expected)}
req=urllib.request.Request('https://api.indexnow.org/indexnow',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json; charset=utf-8'},method='POST')
with urllib.request.urlopen(req,timeout=30) as response:
    assert response.status in [200,202],response.status
    print(json.dumps({'accepted':True,'urls':len(expected),'http_status':response.status}))
