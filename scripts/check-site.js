#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=process.cwd(),errors=[];
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.name==='.git'?[]:e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);}
const files=walk(root).filter(f=>f.endsWith('.html'));
for(const file of files){
  const html=fs.readFileSync(file,'utf8'),label=path.relative(root,file);
  if(!/<meta\s+charset=/i.test(html))errors.push(label+': missing charset');
  if(!/<meta\s+name=["']viewport["']/i.test(html))errors.push(label+': missing viewport');
  if(!/<title>[^<]+<\/title>/i.test(html))errors.push(label+': missing title');
  if(!/<meta\s+name=["']description["']/i.test(html))errors.push(label+': missing description');
  for(const m of html.matchAll(/<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)){try{JSON.parse(m[1]);}catch(e){errors.push(label+': invalid JSON-LD: '+e.message);}}
  for(const m of html.matchAll(/<a\b[^>]*target=["']_blank["'][^>]*>/gi)){if(!/\brel=["'][^"']*noopener/i.test(m[0]))errors.push(label+': target=_blank without noopener');}
}
for(const file of walk(root)){
  if(!file.match(/\.(html|js|json|ya?ml|md|txt)$/))continue;
  const body=fs.readFileSync(file,'utf8'),label=path.relative(root,file);
  if(/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/.test(body)||/\b(?:sk|rk|ghp)_[A-Za-z0-9_-]{20,}\b/.test(body))errors.push(label+': possible secret');
}
if(errors.length){console.error(errors.join('\n'));process.exit(1);}
console.log('Site checks passed for '+files.length+' HTML files.');