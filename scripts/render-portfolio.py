#!/usr/bin/env python3
"""Render the bilingual portfolio from content/portfolio.json. No runtime API."""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist' if (ROOT / 'dist').is_dir() else ROOT
PROJECTS = json.loads((ROOT / 'content/portfolio.json').read_text())
ARROW = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
CLOSE = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>'
CATEGORIES = {'all': ['Todos', 'All'], 'apps': ['Apps y reservas', 'Apps & booking'], 'comercio': ['Comercio', 'Commerce'], 'gestion': ['Gestión y finanzas', 'Management & finance'], 'ia': ['Agentes e IA', 'Agents & AI']}
STATUS = {'development': ['En desarrollo', 'In development'], 'demo': ['Demo de aplicación', 'Application demo'], 'prototype': ['Prototipo', 'Prototype'], 'inuse': ['En uso', 'In use'], 'service': ['Servicio en curso', 'Ongoing service']}
DIMENSIONS = {'projects/qtx': (1122, 1402), 'projects/quamtex': (1122, 1402), 'projects/barber': (1122, 1402)}

def img(project, lang, dialog=False):
    key = project['image']
    dimensions = DIMENSIONS.get(key, (1280, 854))
    # Dimensions for responsive photographs are read from existing WebP headers.
    if key not in DIMENSIONS:
        from PIL import Image
        dimensions = Image.open(DIST / f'assets/{key}.webp').size
    kind = 'project' if key.startswith('projects/') else 'context'
    caption = (['Imagen del proyecto', 'Project image'] if kind == 'project' else ['Fotografía de contexto', 'Context photograph'])[lang]
    if key == 'editorial/devices': caption = ['Visualización conceptual con IA', 'AI-generated concept visualization'][lang]
    name = project.get('nameEn', project['name']) if lang else project['name']
    srcset = ''
    if (DIST / f'assets/{key}-720.webp').exists():
        sizes = '(max-width: 680px) calc(100vw - 40px), (max-width: 1000px) 44vw, 384px'
        srcset = f' srcset="/assets/{key}-720.webp 720w, /assets/{key}.webp 1280w" sizes="{sizes}"'
    css = 'dialog-art' if dialog else ''
    return f'<img class="{css}" src="/assets/{key}.webp"{srcset} width="{dimensions[0]}" height="{dimensions[1]}" alt="{escape(caption + ": " + name, quote=True)}" loading="lazy" decoding="async">'

def catalog(lang):
    choose = lambda es, en: en if lang else es
    filters = ''.join(f'<button type="button" data-project-filter="{key}" aria-pressed="{str(key == "all").lower()}" aria-controls="project-grid">{labels[lang]}</button>' for key, labels in CATEGORIES.items())
    cards, dialogs = [], []
    for p in PROJECTS:
        name = p.get('nameEn', p['name']) if lang else p['name']
        pid = p['id']
        status = STATUS[p['status']][lang]
        category_words = ' '.join(CATEGORIES[key][lang] for key in p['categories'])
        search = escape(' '.join([name, p['sector'][lang], p['summary'][lang], category_words, *p['tags']]), quote=True)
        photo_class = ' is-project' if p['image'].startswith('projects/') else ''
        cards.append(f'''<article class="catalog-card" id="caso-{pid}" tabindex="-1" aria-labelledby="catalog-title-{pid}" data-project-card data-categories="{' '.join(p['categories'])}" data-search="{search}"><figure class="catalog-image{photo_class}">{img(p, lang)}<span class="catalog-status">{status}</span></figure><div class="catalog-copy"><p class="catalog-sector">{escape(p['sector'][lang])}</p><h2 id="catalog-title-{pid}">{escape(name)}</h2><p>{escape(p['summary'][lang])}</p><button type="button" data-project="{pid}" aria-haspopup="dialog" aria-controls="project-{pid}" aria-label="{choose('Ver ficha de ', 'View details for ')}{escape(name, quote=True)}">{choose('Ver proyecto', 'View project')}{ARROW}</button></div></article>''')
        steps = ''.join(f'<li><span>{i:02d}</span>{escape(step)}</li>' for i, step in enumerate(p['scope'][lang], 1))
        note = choose('Alcance del trabajo. Las fotografías de contexto no son capturas de la aplicación.', 'Project scope. Context photographs are not application screenshots.')
        if p['image'].startswith('projects/'):
            note = choose('Vista del diseño y alcance del proyecto.', 'A view of the project design and scope.')
        dialogs.append(f'''<dialog class="project-dialog catalog-dialog" id="project-{pid}" aria-labelledby="project-title-{pid}"><div class="dialog-layout">{img(p, lang, True)}<div class="dialog-info"><button class="dialog-close" type="button" data-close-project aria-label="{choose('Cerrar proyecto', 'Close project')}">{CLOSE}</button><p class="eyebrow">{status}</p><h2 id="project-title-{pid}">{escape(name)}</h2><p>{escape(p['summary'][lang])}</p><ol class="project-flow">{steps}</ol><p class="project-disclaimer">{note}</p><a class="text-link" href="/{choose('contacto', 'contact')}.html?servicio=app_personalizada" data-service="app_personalizada">{choose('Conversemos sobre una solución así', 'Let’s discuss a solution like this')}{ARROW}</a></div></div></dialog>''')
    count = len(PROJECTS)
    intro = f'''<section class="page-intro project-photo-intro"><div class="wrap"><div><p class="eyebrow">{choose('Proyectos', 'Projects')} / KATIA.AI</p><h1 id="page-title">{choose('Soluciones que<br>toman forma.', 'Solutions<br>taking shape.')}</h1><p class="page-description">{choose('Aplicaciones, procesos e inteligencia artificial. Explora nuestro trabajo, su alcance y su estado.', 'Applications, processes and artificial intelligence. Explore our work, its scope and its current stage.')}</p><span class="catalog-intro-note">{count} {choose('proyectos · Distintas industrias, una misma atención al detalle.', 'projects · Different industries, the same attention to detail.')}</span></div><div class="project-intro-gallery"><img src="/assets/projects/qtx.webp" width="1122" height="1402" alt="QTX Auto" loading="eager" decoding="async"><img src="/assets/projects/quamtex.webp" width="1122" height="1402" alt="Quamtex" loading="eager" decoding="async"><img src="/assets/projects/barber.webp" width="1122" height="1402" alt="ZOHO Mobile Barber" loading="eager" decoding="async"></div></div></section>'''
    content = f'''<section class="section catalog-section" id="proyectos" data-project-catalog aria-label="{choose('Catálogo de proyectos', 'Project catalog')}"><div class="wrap"><div class="catalog-toolbar" data-project-controls hidden><div class="catalog-search-row"><label class="catalog-search" for="project-search"><span>{choose('Encuentra un proyecto', 'Find a project')}</span><input id="project-search" type="search" placeholder="{choose('Nombre, industria o tecnología…', 'Name, industry or technology…')}" autocomplete="off" aria-controls="project-grid"></label><p id="project-count" class="catalog-count" role="status" aria-live="polite">{count} {choose('proyectos', 'projects')}</p></div><div class="catalog-filters" role="group" aria-label="{choose('Filtrar por solución', 'Filter by solution')}">{filters}</div></div><div class="catalog-grid" id="project-grid">{''.join(cards)}</div><div class="catalog-empty" data-project-empty hidden><h2>{choose('No encontramos coincidencias.', 'No matching projects.')}</h2><p>{choose('Prueba otro término o explora todas las soluciones.', 'Try another term or explore all solutions.')}</p><button type="button" class="btn btn-outline" data-project-reset>{choose('Mostrar todos', 'Show all')}</button></div><button type="button" class="btn btn-outline catalog-more" data-project-more aria-controls="project-grid" hidden>{choose('Ver más proyectos', 'Show more projects')}</button><p class="catalog-note">{choose('Cada ficha indica el estado del trabajo. Las demos y los prototipos muestran propuestas de aplicación. Las fotografías de contexto ilustran la industria; no representan capturas del producto.', 'Each entry identifies the stage of the work. Demos and prototypes show application concepts. Context photographs illustrate the industry; they are not product screenshots.')}</p></div></section>{''.join(dialogs)}'''
    return intro + content

TECH = [
    ('Oracle', 'NetSuite', 'https://www.netsuite.com/portal/products/erp.shtml', ['ERP, inventario y operación empresarial.', 'ERP, inventory and business operations.']),
    ('QuickBooks', '', 'https://quickbooks.intuit.com/', ['Contabilidad, facturación y organización financiera.', 'Accounting, invoicing and financial organization.']),
    ('Stripe', '', 'https://stripe.com/payments', ['Pagos, cobros y flujos de facturación.', 'Payments, collections and billing workflows.']),
    ('Apollo', '', 'https://www.apollo.io/', ['Prospección B2B e inteligencia comercial.', 'B2B prospecting and sales intelligence.']),
    ('Amazon', '', 'https://developer-docs.amazon/sp-api/', ['Comercio, pedidos y atención en el marketplace.', 'Commerce, orders and marketplace support.']),
    ('OpenAI', '', 'https://openai.com/business/', ['Modelos de IA para asistentes y automatización.', 'AI models for assistants and automation.']),
    ('Anthropic', 'Claude', 'https://www.anthropic.com/', ['Modelos Claude para agentes y análisis.', 'Claude models for agents and analysis.']),
]

def technologies(lang, compact):
    choose = lambda es, en: en if lang else es
    title = choose('Tecnologías con las que trabajamos.', 'Technologies we work with.')
    if compact:
        names = ''.join(f'<li><a href="/{choose("servicios", "services")}.html#tecnologias">{name}{f"<small>{sub}</small>" if sub else ""}</a></li>' for name, sub, _, _ in TECH)
        return f'<section class="technology-strip" aria-labelledby="technology-title"><div class="wrap"><div class="technology-strip-head"><h2 id="technology-title">{title}</h2><a class="text-link" href="/{choose("servicios", "services")}.html#tecnologias">{choose("Explorar nuestro ecosistema", "Explore our ecosystem")}{ARROW}</a></div><ul class="technology-names" aria-label="{title}">{names}</ul></div></section>'
    groups = []
    for label, indices in [(choose('Gestión y finanzas', 'Management & finance'), [0,1,2]), (choose('Comercio y crecimiento', 'Commerce & growth'), [3,4]), (choose('Inteligencia artificial', 'Artificial intelligence'), [5,6])]:
        items = ''
        for i in indices:
            name, sub, url, description = TECH[i]
            display = name + (' ' + sub if sub else '')
            items += f'<a class="technology-item" href="{url}" target="_blank" rel="noopener"><strong>{display}</strong><span>{description[lang]}</span><span class="sr-only">{choose("Sitio oficial; abre en otra pestaña", "Official website; opens in a new tab")}</span></a>'
        groups.append(f'<div class="technology-group"><h3>{label}</h3>{items}</div>')
    return f'<section class="section technology-section" id="tecnologias" aria-labelledby="technology-title"><div class="wrap"><div class="section-top"><div><p class="eyebrow">{choose("Nuestro ecosistema tecnológico", "Our technology ecosystem")}</p><h2 id="technology-title">{title}</h2></div><p>{choose("Conectamos herramientas de negocio e inteligencia artificial alrededor de tu operación.", "We connect business tools and artificial intelligence around your operations.")}</p></div><div class="technology-group-grid">{"".join(groups)}</div><p class="catalog-note">{choose("Seleccionamos las herramientas y definimos permisos, datos, integraciones y supervisión según las necesidades de cada proyecto.", "We select tools and define permissions, data, integrations and oversight around each project’s needs.")}</p></div></section>'

def replace_block(text, name, html, before=None):
    start, end = f'<!-- {name}:start -->', f'<!-- {name}:end -->'
    block = start + html + end
    if start in text:
        return re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: block, text, flags=re.S)
    assert before in text, f'Missing insertion point: {before}'
    return text.replace(before, block + before, 1)

for lang in (0,1):
    for page in (('index.html','en.html')[lang], ('servicios.html','services.html')[lang], ('proyectos.html','projects.html')[lang]):
        path = DIST / page
        text = path.read_text()
        if '/assets/portfolio.css' not in text:
            text = text.replace('</head>', '<link rel="stylesheet" href="/assets/portfolio.css"></head>')
        if page in ('proyectos.html','projects.html'):
            if '<!-- portfolio:start -->' not in text:
                text, n = re.subn(r'<section class="page-intro project-photo-intro">.*?(?=<section class="next-step">)', lambda _: '<!-- portfolio:start -->' + catalog(lang) + '<!-- portfolio:end -->', text, count=1, flags=re.S)
                assert n == 1
            else: text = replace_block(text, 'portfolio', catalog(lang))
            if '/assets/portfolio.js' not in text:
                text = text.replace('</body>', '<script src="/assets/portfolio.js" defer></script></body>')
        elif page in ('index.html','en.html'):
            # Normalize only catalog links, then assign anchors within each card.
            text = re.sub(r'href="/(proyectos|projects)\.html#caso-[^"]+"', r'href="/\1.html"', text)
            text = replace_block(text, 'technology-strip', technologies(lang, True), '<section class="next-step">')
            if 'class="portfolio-all"' not in text:
                href = '/projects.html' if lang else '/proyectos.html'
                label = 'Explore all projects' if lang else 'Explorar todos los proyectos'
                text = re.sub(r'(<section class="section portfolio home-portfolio".*?)(</div></section>)', lambda m: m[1] + f'<div class="portfolio-all"><a class="btn btn-outline" href="{href}">{label}{ARROW}</a></div>' + m[2], text, count=1, flags=re.S)
            for pid in ('qtx','quamtex','barber'):
                text = re.sub(r'<article class="project-tile project-' + pid + r'">.*?</article>', lambda m: re.sub(r'href="/(proyectos|projects)\.html"', r'href="/\1.html#caso-' + pid + '"', m[0], count=1), text, count=1, flags=re.S)
        else:
            text = replace_block(text, 'technology-details', technologies(lang, False), '<section class="section ecosystem-section"')
        path.write_text(text)
print(f'Rendered {len(PROJECTS)} projects and 7 technologies in Spanish and English.')
