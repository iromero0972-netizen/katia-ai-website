#!/usr/bin/env python3
"""Build bilingual service/project documents and SEO metadata. Review remains private."""
from pathlib import Path
from html import escape as esc
import json
import re
import runpy
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/'dist' if (ROOT/'dist').is_dir() else ROOT
BASE='https://katia.solutions/'
PORTFOLIO=runpy.run_path(str(ROOT/'scripts/render-portfolio.py'))
PROJECTS=PORTFOLIO['PROJECTS']
STATUS=PORTFOLIO['STATUS']
ARROW=PORTFOLIO['ARROW']
SERVICES=json.loads((ROOT/'content/services.json').read_text())
STORIES=json.loads((ROOT/'content/project-stories.json').read_text())
CORE=json.loads((ROOT/'content/seo-pages.json').read_text())
TEMPLATES=[(DIST/p).read_text() for p in ['servicios.html','services.html']]
PAGES=[]
ORG_ID=BASE+'#organization'
FOUNDER_ID=BASE+'nosotros.html#ignacio-romero'

def choose(lang,es,en): return en if lang else es
def url(path): return BASE+('' if path=='index.html' else path)
def case_path(p,lang): return ('projects/' if lang else 'proyectos/')+p['id']+'.html'
def block(text,key,html,before):
    return PORTFOLIO['replace_block'](text,key,html,before)
def picture(key,alt,hero=False,cover=False):
    width,height=Image.open(DIST/f'assets/{key}.webp').size
    small=DIST/f'assets/{key}-720.webp'
    srcset=f' srcset="/assets/{key}-720.webp 720w, /assets/{key}.webp {width}w" sizes="(max-width: 680px) calc(100vw - 40px), {"1160px" if cover else "580px"}"' if small.exists() else ''
    return f'<img src="/assets/{key}.webp"{srcset} width="{width}" height="{height}" alt="{esc(alt,quote=True)}" decoding="async" '+('fetchpriority="high"' if hero else 'loading="lazy"')+'>'

def breadcrumbs(items,lang):
    lis=''.join('<li>'+ (f'<a href="/{path}">{esc(label)}</a>' if i<len(items)-1 else f'<span aria-current="page">{esc(label)}</span>')+'</li>' for i,(label,path) in enumerate(items))
    return f'<div class="wrap"><nav class="seo-breadcrumb" aria-label="{choose(lang,"Ruta de navegación","Breadcrumb")}"><ol>{lis}</ol></nav></div>'

def metadata(html,meta,lang,crumbs=None,entity=None):
    page_url=url(meta['path']); image=meta.get('image','assets/img/og-card.jpg')
    html=re.sub(r'<title>.*?</title>',lambda _: '<title>'+esc(meta['title'])+'</title>',html,count=1,flags=re.S)
    html=re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>','',html,flags=re.S)
    html=re.sub(r'<link\b[^>]*rel="(?:canonical|alternate)"[^>]*>','',html)
    # Inner pages must not preload the unrelated homepage hero image.
    html=re.sub(r'<link\b[^>]*rel="preload"[^>]*as="image"[^>]*>','',html)
    values={
      'description':meta['description'],'robots':'noindex,nofollow',
      'og:title':meta['title'],'og:description':meta['description'],'og:url':page_url,
      'og:image':BASE+image,'og:image:alt':meta.get('imageAlt',choose(lang,'KATIA.AI · Soluciones empresariales con IA','KATIA.AI · Business solutions with AI')),
      'og:type':'website','og:locale':['es_US','en_US'][lang],
      'twitter:card':'summary_large_image','twitter:title':meta['title'],'twitter:description':meta['description'],
      'twitter:image':BASE+image,'twitter:image:alt':meta.get('imageAlt','KATIA.AI')
    }
    for name,value in values.items():
        html=re.sub(r'<meta\b[^>]*(?:name|property)="'+re.escape(name)+r'"[^>]*>','',html)
        attr='property' if name.startswith('og:') else 'name'
        html=html.replace('</head>',f'<meta {attr}="{name}" content="{esc(value,quote=True)}"></head>',1)
    organization={
      '@type':'Organization','@id':ORG_ID,'name':'KATIA.AI','url':BASE,'logo':BASE+'assets/katia-logo.png',
      'description':choose(lang,'Agencia de automatización con IA para PYMEs en Houston y Katy. Soluciones administrativas, contables, financieras y fiscales, apps, agentes e integraciones.','AI automation agency for small businesses in Houston and Katy. Administrative, accounting, financial and tax workflows, apps, agents and integrations.'),
      'email':'ventas@katia.solutions','areaServed':[{'@type':'City','name':'Houston'},{'@type':'City','name':'Katy'}],
      'founder':{'@id':FOUNDER_ID},
      'sameAs':['https://www.instagram.com/katia.ai_/','https://www.facebook.com/profile.php?id=61575396974517'],
      'contactPoint':[
        {'@type':'ContactPoint','contactType':'sales','telephone':'+1-346-220-4052','email':'ventas@katia.solutions','availableLanguage':['es','en']},
        {'@type':'ContactPoint','contactType':'sales','telephone':'+1-346-892-0577','url':'https://wa.me/13468920577','availableLanguage':['es','en']}
      ],
      'hasOfferCatalog':{'@type':'OfferCatalog','name':choose(lang,'Servicios de KATIA.AI','KATIA.AI services'),'itemListElement':[
        {'@type':'Offer','itemOffered':{'@type':'Service','@id':url(s['paths'][lang])+'#service','name':s['name'][lang],'url':url(s['paths'][lang])}} for s in SERVICES
      ]}
    }
    page={'@type':meta.get('type','WebPage'),'@id':page_url+'#webpage','url':page_url,'name':meta['title'],'description':meta['description'],'inLanguage':['es','en'][lang],'isPartOf':{'@id':BASE+'#website'},'about':{'@id':ORG_ID}}
    graph=[organization,{'@type':'WebSite','@id':BASE+'#website','url':BASE,'name':'KATIA.AI','inLanguage':['es','en'],'publisher':{'@id':ORG_ID}},page]
    if meta['path'] in ['nosotros.html','about.html']:
        person={'@type':'Person','@id':FOUNDER_ID,'name':'Ignacio Romero','url':BASE+'nosotros.html#ignacio-romero','jobTitle':choose(lang,'Contador Público · Fundador de KATIA.AI','Public Accountant · Founder of KATIA.AI'),'worksFor':{'@id':ORG_ID},'description':choose(lang,'Más de 30 años de experiencia en administración, finanzas y contabilidad.','Over 30 years of experience in administration, finance and accounting.')}
        graph.append(person); page['mainEntity']={'@id':FOUNDER_ID}
    if entity:
        graph.append(entity); page['mainEntity']={'@id':entity['@id']}
    if crumbs:
        bid=page_url+'#breadcrumb'
        page['breadcrumb']={'@id':bid}
        graph.append({'@type':'BreadcrumbList','@id':bid,'itemListElement':[{'@type':'ListItem','position':i+1,'name':label,'item':url(path)} for i,(label,path) in enumerate(crumbs)]})
    if meta['path'] in ['proyectos.html','projects.html']:
        listing={'@type':'ItemList','@id':page_url+'#projects','itemListElement':[{'@type':'ListItem','position':i+1,'name':p.get('nameEn',p['name']) if lang else p['name'],'url':url(case_path(p,lang))} for i,p in enumerate(PROJECTS)]}
        graph.append(listing);page['mainEntity']={'@id':listing['@id']}
    tags=f'<link rel="canonical" href="{page_url}">'
    for language,path in [('es',meta['pair'][0]),('en',meta['pair'][1]),('x-default',meta['pair'][0])]: tags+=f'<link rel="alternate" hreflang="{language}" href="{url(path)}">'
    tags+='<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')+'</script>'
    if '/assets/detail.css' not in html: tags+='<link rel="stylesheet" href="/assets/detail.css">'
    if '/assets/metrics.js' not in html: html=html.replace('<script src="/assets/evolution.js"','<script src="/assets/metrics.js" defer></script><script src="/assets/evolution.js"',1)
    html=html.replace('</head>',tags+'</head>',1)
    html=re.sub(r'<div class="lang"[^>]*>.*?</div>',lambda _:f'<div class="lang" aria-label="{choose(lang,"Idioma","Language")}"><a href="/{meta["pair"][0]}" lang="es" hreflang="es"'+(' class="active" aria-current="page"' if not lang else '')+'>ES</a><span aria-hidden="true">/</span><a href="/'+meta['pair'][1]+'" lang="en" hreflang="en"'+(' class="active" aria-current="page"' if lang else '')+'>EN</a></div>',html,count=1,flags=re.S)
    html=re.sub(r'<body\b([^>]*)>',lambda m:'<body'+m[1]+' data-content-kind="'+meta.get('kind','core')+'">' if 'data-content-kind' not in m[1] else m[0],html,count=1)
    # Keep publication inventory machine-readable without putting it in the runtime.
    PAGES.append({'path':meta['path'],'pair':meta['pair'],'lang':['es','en'][lang],'canonical':page_url,'kind':meta.get('kind','core')})
    return html

def save(path,html):
    p=DIST/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html)

def shell(main,lang,section='services'):
    html=TEMPLATES[lang]
    html=re.sub(r'<main id="main">.*?</main>',lambda _: '<main id="main">'+main+'</main>',html,count=1,flags=re.S)
    html=re.sub(r'<body\b[^>]*>', '<body id="inicio" class="page-detail">',html,count=1)
    if section=='projects':
        html=re.sub(r'(<nav class="nav-links".*?</nav>)',lambda m:m[0].replace(' aria-current="page"','').replace('href="/'+choose(lang,'proyectos','projects')+'.html"','href="/'+choose(lang,'proyectos','projects')+'.html" aria-current="page"'),html,count=1,flags=re.S)
    return html

def cta(lang,form):
    return f'<section class="next-step"><div class="wrap"><div><p class="eyebrow">{choose(lang,"Diagnóstico inicial · 30 minutos · Sin costo","Initial consultation · 30 minutes · No cost")}</p><h2>{choose(lang,"Hablemos de tu operación.","Let’s talk about your operations.")}</h2></div><a class="btn" href="/{choose(lang,"contacto","contact")}.html?servicio={form}">{choose(lang,"Solicitar diagnóstico","Request a consultation")}{ARROW}</a></div></section>'

def project_cards(ids,lang):
    cards=[]
    for pid in ids:
        p=next(p for p in PROJECTS if p['id']==pid);name=p.get('nameEn',p['name']) if lang else p['name'];path=case_path(p,lang)
        art=f'<a href="/{path}" aria-label="{esc(name,quote=True)}">'+picture(p['image'],choose(lang,'Portada de ','Cover for ')+name,cover=True)+'</a>' if p['image'] else ''
        cards.append(f'<article class="detail-project{(" detail-project--scope" if not p["image"] else "")}">{art}<span class="detail-project-status">{STATUS[p["status"]][lang]}</span><h3><a href="/{path}">{esc(name)}</a></h3><p>{esc(p["summary"][lang])}</p><a class="text-link" href="/{path}">{choose(lang,"Conocer el proyecto","Explore project")}{ARROW}</a></article>')
    return '<div class="detail-projects">'+''.join(cards)+'</div>'

def faq_html(faq):
    return ''.join(f'<details class="detail-faq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in faq)

for lang in (0,1):
    home=('en.html' if lang else 'index.html');hub=choose(lang,'servicios.html','services.html');phub=choose(lang,'proyectos.html','projects.html')
    for s in SERVICES:
        path=s['paths'][lang];name=s['name'][lang];crumbs=[(choose(lang,'Inicio','Home'),home),(choose(lang,'Servicios','Services'),hub),(name,path)]
        main=breadcrumbs(crumbs,lang)+f'<section class="detail-hero"><div class="wrap detail-hero-grid"><div><p class="eyebrow">KATIA.AI · Houston & Katy · ES / EN</p><h1>{esc(name)}</h1><p class="detail-intro">{esc(s["intro"][lang])}</p><a class="btn" href="/{choose(lang,"contacto","contact")}.html?servicio={s["form"]}">{choose(lang,"Conversemos sobre tu proyecto","Let’s discuss your project")}{ARROW}</a></div><figure class="detail-photo">{picture(s["image"],s["alt"][lang],True)}</figure></div></section>'
        outcomes=s['outcomesEn' if lang else 'outcomes'];steps=s['stepsEn' if lang else 'steps']
        tiles=''.join(f'<article class="detail-card"><span class="detail-number">{i:02d}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>' for i,(title,copy) in enumerate(outcomes,1))
        main+=f'<section class="detail-section soft"><div class="wrap"><h2>{choose(lang,"Una solución con propósito.","A solution with a purpose.")}</h2><p class="detail-lead">{esc(s["problem"][lang])}</p><div class="detail-grid">{tiles}</div></div></section>'
        flow=''.join(f'<article class="detail-card"><span class="detail-number">{i:02d}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>' for i,(title,copy) in enumerate(steps,1))
        main+=f'<section class="detail-section"><div class="wrap"><h2>{choose(lang,"Así se organiza el proceso.","How the process is organized.")}</h2><div class="detail-grid">{flow}</div><p class="detail-note">{choose(lang,"Flujo de referencia. Las funciones y criterios de aceptación se acuerdan en la propuesta.","Reference workflow. Features and acceptance criteria are agreed in the proposal.")}</p></div></section>'
        tools=''.join(f'<li>{esc(t)}</li>' for t in s['tools']);needs=''.join(f'<li>{esc(t)}</li>' for t in s['needsEn' if lang else 'needs'])
        main+=f'<section class="detail-section soft"><div class="wrap detail-two"><div><h2>{choose(lang,"Herramientas que conectamos.","Tools we connect.")}</h2><ul class="detail-tools">{tools}</ul><p class="detail-note">{choose(lang,"La selección y compatibilidad se validan por proyecto. Las licencias, permisos y consumo de terceros se confirman en el alcance.","Selection and compatibility are validated per project. Third-party licenses, permissions and usage are confirmed within scope.")}</p><a class="text-link" href="/{hub}#tecnologias">{choose(lang,"Ver el ecosistema completo","Explore the full ecosystem")}{ARROW}</a></div><div><h2>{choose(lang,"Qué necesitamos para empezar.","What we need to get started.")}</h2><ul class="detail-list">{needs}</ul></div></div></section>'
        main+=f'<section class="detail-section"><div class="wrap"><h2>{choose(lang,"Proyectos relacionados.","Related projects.")}</h2>{project_cards(s["projects"],lang)}</div></section>'
        if s['id']=='agentes':
            main+=f'<section class="detail-section soft"><div class="wrap"><h2>{choose(lang,"Conoce nuestros agentes.","Meet our agents.")}</h2><div class="detail-agents"><a href="tel:+13462204052"><strong>Leo</strong><span>{choose(lang,"Hablar por teléfono","Talk by phone")} · +1 346 220 4052</span></a><a href="https://wa.me/13468920577"><strong>Andrés</strong><span>{choose(lang,"Conversar por WhatsApp","Chat on WhatsApp")} · +1 346 892 0577</span></a></div></div></section>'
        main+=f'<section class="detail-section"><div class="wrap"><h2>{choose(lang,"Antes de decidir.","Before you decide.")}</h2>{faq_html(s["faqEn" if lang else "faq"])}<p class="detail-note">{choose(lang,"La inversión se cotiza según funciones, integraciones y acompañamiento.","Pricing depends on features, integrations and ongoing support.")} <a href="/{choose(lang,"guia","guide")}.html#preguntas">{choose(lang,"Consultar inversión y preguntas generales","View pricing and general questions")}</a>.</p></div></section>'+cta(lang,s['form'])
        meta={'path':path,'pair':s['paths'],'title':s['title'][lang],'description':s['intro'][lang],'kind':'service','image':'assets/'+s['image']+'.webp','imageAlt':s['alt'][lang]}
        entity={'@type':'Service','@id':url(path)+'#service','name':name,'description':s['intro'][lang],'serviceType':name,'url':url(path),'provider':{'@id':ORG_ID},'areaServed':[{'@type':'City','name':'Houston'},{'@type':'City','name':'Katy'}]}
        save(path,metadata(shell(main,lang),meta,lang,crumbs,entity))

    for p in PROJECTS:
        path=case_path(p,lang);name=p.get('nameEn',p['name']) if lang else p['name'];story=STORIES[p['id']];status=STATUS[p['status']][lang]
        crumbs=[(choose(lang,'Inicio','Home'),home),(choose(lang,'Proyectos','Projects'),phub),(name,path)]
        main=breadcrumbs(crumbs,lang)+f'<section class="project-page-hero"><div class="wrap"><p class="eyebrow">{esc(p["sector"][lang])} · KATIA.AI</p><h1>{esc(name)}</h1><span class="project-page-status">{status}</span><p class="detail-intro">{esc(p["summary"][lang])}</p></div></section>'
        if p['image']:
            caption=choose(lang,'Captura de la interfaz del proyecto.','Captured project interface.')
            if p['status'] in ['demo','prototype']:caption=choose(lang,'Captura de demostración con datos de ejemplo.','Demonstration screenshot with example data.')
            if p.get('imageKind')=='presentation':caption=choose(lang,'Portada original de presentación.','Original presentation cover.')
            main+=f'<section><div class="wrap"><figure class="project-full-cover"><a href="/assets/{p["image"]}.webp" target="_blank" rel="noopener" aria-label="{choose(lang,"Abrir portada de ","Open cover for ")+esc(name,quote=True)}">{picture(p["image"],caption+" "+name,True,True)}</a><figcaption>{caption} {choose(lang,"Selecciona la imagen para verla a tamaño completo.","Select the image to view it at full size.")}</figcaption></figure></div></section>'
        main+=f'<section class="detail-section"><div class="wrap detail-two"><div><h2>{choose(lang,"La necesidad.","The need.")}</h2><p class="detail-lead">{esc(story["context"][lang])}</p></div><div><h2>{choose(lang,"El enfoque de KATIA.","KATIA’s approach.")}</h2><p class="detail-lead">{esc(story["approach"][lang])}</p></div></div></section>'
        flow=''.join(f'<li><span>{i:02d}</span>{esc(step)}</li>' for i,step in enumerate(p['scope'][lang],1))
        main+=f'<section class="detail-section soft"><div class="wrap"><h2>{choose(lang,"Alcance del proyecto.","Project scope.")}</h2><ol class="project-scope-flow">{flow}</ol><p class="detail-note">{choose(lang,"Estado de esta ficha:","Status of this entry:")} {status}. {choose(lang,"Las imágenes y el alcance describen el trabajo presentado; no constituyen una medición de resultados comerciales.","Images and scope describe the work presented; they do not measure business results.")}</p></div></section>'
        related=[s for s in SERVICES if p['id'] in s['projects']]
        if not related:related=[next(s for s in SERVICES if s['id']=='apps')]
        links=''.join(f'<li><a href="/{s["paths"][lang]}">{esc(s["name"][lang])}</a></li>' for s in related)
        main+=f'<section class="detail-section"><div class="wrap"><h2>{choose(lang,"Explora las soluciones relacionadas.","Explore related solutions.")}</h2><nav class="service-navigation" aria-label="{choose(lang,"Servicios relacionados","Related services")}"><ul>{links}</ul></nav><a class="text-link" href="/{phub}">{choose(lang,"Volver a todos los proyectos","Back to all projects")}{ARROW}</a></div></section>'+cta(lang,related[0]['form'])
        meta={'path':path,'pair':[case_path(p,0),case_path(p,1)],'title':name+' · '+choose(lang,'Proyecto','Project')+' | KATIA.AI','description':p['summary'][lang]+' '+choose(lang,'Estado: ','Status: ')+status+'.','kind':'project'}
        entity={'@type':'CreativeWork','@id':url(path)+'#project','name':name,'description':p['summary'][lang],'creativeWorkStatus':status,'url':url(path),'creator':{'@id':ORG_ID},'inLanguage':['es','en'][lang],'mainEntityOfPage':{'@id':url(path)+'#webpage'}}
        if p['image']:
            meta.update(image='assets/'+p['image']+'.webp',imageAlt=choose(lang,'Portada de ','Cover for ')+name);entity['image']=BASE+meta['image']
        save(path,metadata(shell(main,lang,'projects'),meta,lang,crumbs,entity))

for meta in CORE:
    lang=int(meta['lang']=='en');path=meta['path'];html=(DIST/path).read_text();crumbs=None
    if path in ['index.html','en.html']:
        intro=choose(lang,'Apps, agentes e integraciones con IA para tu gestión administrativa, contable, financiera y fiscal. Con controles claros y acompañamiento humano.','AI apps, agents and integrations for administration, accounting, finance and tax workflows. With clear controls and human guidance.')
        html=re.sub(r'<p class="hero-description">.*?</p>',lambda _:'<p class="hero-description">'+intro+'</p>',html,count=1,flags=re.S)
    if path in ['nosotros.html','about.html']:
        html=html.replace('<div class="founder-signature">','<div class="founder-signature" id="ignacio-romero">')
        bio=choose(lang,'Ignacio Romero aporta más de 30 años de experiencia en administración, finanzas y contabilidad. En KATIA, ese criterio guía el análisis del proceso, los controles y la revisión de cada solución.','Ignacio Romero brings over 30 years of experience in administration, finance and accounting. At KATIA, that experience informs process analysis, controls and the review of each solution.')
        # Locate the complete signature, including its nested div.
        html=re.sub(r'(<div class="founder-signature"[^>]*>.*?</div></div>)(?:<p class="founder-bio">.*?</p>)?',lambda m:m[1]+'<p class="founder-bio">'+bio+'</p>',html,count=1,flags=re.S)
        if 'id="metodo"' not in html:html=html.replace('<section class="section delivery-visual"','<section id="metodo" class="section delivery-visual"')
    if path in ['servicios.html','services.html']:
        nav='<nav class="service-navigation" aria-label="'+choose(lang,'Explorar servicios','Explore services')+'"><div class="wrap"><ul>'+''.join(f'<li><a href="/{s["paths"][lang]}">{esc(s["name"][lang])}</a></li>' for s in SERVICES)+'</ul></div></nav>'
        html=block(html,'service-links',nav,'<section class="section service-overview"' if '<section class="section service-overview"' in html else '<section class="section services-section"') if '<!-- service-links:start -->' in html else html
        if '<!-- service-links:start -->' not in html:
            html=re.sub(r'(<main id="main">.*?</section>)',lambda m:m[1]+'<!-- service-links:start -->'+nav+'<!-- service-links:end -->',html,count=1,flags=re.S)
        for suffix,sid in [('apps','apps'),('leads','leads'),('market','mercado'),('support','agentes')]:
            s=next(s for s in SERVICES if s['id']==sid)
            html=re.sub(r'<article class="solution-tile solution-'+suffix+r'">.*?</article>',lambda m:re.sub(r'<a href="[^"]*" class="circle-link"[^>]*>',f'<a href="/{s["paths"][lang]}" class="circle-link" aria-label="{esc(s["name"][lang],quote=True)}">',m[0],count=1),html,count=1,flags=re.S)
    # Add useful FAQ content without replacing established pricing or policy answers.
    if path in ['guia.html','guide.html']:
        faq=[(choose(lang,'¿Cómo se conectan NetSuite y QuickBooks?','How are NetSuite and QuickBooks connected?'),choose(lang,'Validamos producto, módulos, permisos y APIs antes de acordar qué datos se intercambian. Las licencias y costos de terceros se confirman por proyecto.','We validate the product, modules, permissions and APIs before agreeing on data exchanges. Third-party licenses and costs are confirmed per project.')),(choose(lang,'¿Qué distingue una demo de una solución en uso?','What distinguishes a demo from a solution in use?'),choose(lang,'Cada ficha de proyecto indica su estado. Una demo permite revisar la experiencia; una solución en uso describe un flujo operativo. Las portadas no demuestran por sí solas resultados comerciales.','Every project entry identifies its status. A demo supports experience review; work in use describes an operational workflow. Covers alone do not establish business results.')),(choose(lang,'¿Quién administra los datos y accesos?','Who manages data and access?'),choose(lang,'La propuesta define cuentas, permisos, responsables, retención y condiciones de entrega. Las decisiones sensibles y aprobaciones permanecen con las personas designadas.','The proposal defines accounts, permissions, owners, retention and handover terms. Sensitive decisions and approvals stay with designated people.'))]
        section='<section class="detail-section"><div class="wrap"><h2>'+choose(lang,'Integración, datos y proyectos.','Integrations, data and projects.')+'</h2>'+faq_html(faq)+'</div></section>'
        html=block(html,'extended-faq',section,'<section class="next-step">')
    if path not in ['index.html','en.html']:
        label=meta['title'].split('|')[0].strip()
        # Short labels mirror navigation, not keyword-heavy title tags.
        labels={'servicios.html':'Servicios','services.html':'Services','proyectos.html':'Proyectos','projects.html':'Projects','nosotros.html':'Nuestra firma','about.html':'Our firm','guia.html':'Recursos','guide.html':'Resources','contacto.html':'Contacto','contact.html':'Contact'}
        crumbs=[(choose(lang,'Inicio','Home'),'en.html' if lang else 'index.html'),(labels[path],path)]
        if '<!-- breadcrumb:start -->' in html:html=block(html,'breadcrumb',breadcrumbs(crumbs,lang),None)
        else:html=html.replace('<main id="main">','<main id="main"><!-- breadcrumb:start -->'+breadcrumbs(crumbs,lang)+'<!-- breadcrumb:end -->',1)
    save(path,metadata(html,meta,lang,crumbs))

(ROOT/'content/page-inventory.json').write_text(json.dumps(PAGES,ensure_ascii=False,indent=2)+'\n')
# Review sitemap references only canonical publication URLs; robots still disallows review.
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
tree=ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
for meta in sorted(PAGES,key=lambda m:m['canonical']):
    node=ET.SubElement(tree,'{http://www.sitemaps.org/schemas/sitemap/0.9}url')
    ET.SubElement(node,'{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text=meta['canonical']
ET.ElementTree(tree).write(DIST/'sitemap.xml',encoding='utf-8',xml_declaration=True)
# Refresh the pre-existing production index without presenting it as a Google ranking mechanism.
lines=['# KATIA.AI','', '> Agencia de automatización con IA para PYMEs en Houston y Katy. Atención en español e inglés.', '', '## Servicios / Services', '']
for s in SERVICES:
    for lang in [0,1]:lines.append(f'- [{s["name"][lang]}]({url(s["paths"][lang])})')
lines+=['','## Empresa y proyectos','',f'- [Nuestra firma]({BASE}nosotros.html)',f'- [Our firm]({BASE}about.html)',f'- [Proyectos y estados]({BASE}proyectos.html)',f'- [Projects and stages]({BASE}projects.html)',f'- [Costos de referencia y preguntas]({BASE}guia.html)',f'- [Reference costs and questions]({BASE}guide.html)',f'- [Contacto]({BASE}contacto.html)',f'- [Contact]({BASE}contact.html)','', 'Cada proyecto indica su estado. Las demos y portadas no constituyen una medición de resultados. Alcance, inversión y condiciones se confirman en la propuesta. KATIA no sustituye a los profesionales responsables de contabilidad, asesoría o presentación fiscal.','']
(ROOT/'deployment/llms.production.txt').write_text('\n'.join(lines))
runpy.run_path(str(ROOT/'scripts/render-contact.py'))
print(f'Rendered SEO for {len(PAGES)} pages: 12 core, {len(SERVICES)*2} service, {len(PROJECTS)*2} project pages.')
