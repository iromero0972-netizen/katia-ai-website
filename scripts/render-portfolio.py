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
    if not key:
        return ''
    dimensions = DIMENSIONS.get(key, (1280, 854))
    # Dimensions for responsive photographs are read from existing WebP headers.
    if key not in DIMENSIONS:
        from PIL import Image
        dimensions = Image.open(DIST / f'assets/{key}.webp').size
    caption = ['Portada real del proyecto', 'Actual project cover'][lang]
    if project.get('imageKind') == 'presentation':
        caption = ['Portada original de presentación', 'Original presentation cover'][lang]
    name = project.get('nameEn', project['name']) if lang else project['name']
    srcset = ''
    if (DIST / f'assets/{key}-720.webp').exists():
        sizes = '(max-width: 680px) calc(100vw - 40px), 580px' if not dialog else '(max-width: 1200px) 94vw, 1160px'
        srcset = f' srcset="/assets/{key}-720.webp 720w, /assets/{key}.webp {dimensions[0]}w" sizes="{sizes}"'
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
        preview = f'<button class="catalog-preview" type="button" data-project="{pid}" aria-haspopup="dialog" aria-controls="project-{pid}" aria-label="{choose("Ampliar portada de ", "Enlarge cover for ")}{escape(name, quote=True)}">{img(p, lang)}</button>' if p['image'] else ''
        scope_class = '' if p['image'] else ' catalog-card--scope'
        cards.append(f'''<article class="catalog-card{scope_class}" id="caso-{pid}" tabindex="-1" aria-labelledby="catalog-title-{pid}" data-project-card data-categories="{' '.join(p['categories'])}" data-search="{search}">{preview}<div class="catalog-copy"><div class="catalog-meta"><p class="catalog-sector">{escape(p['sector'][lang])}</p><span class="catalog-status">{status}</span></div><h2 id="catalog-title-{pid}">{escape(name)}</h2><p>{escape(p['summary'][lang])}</p><a class="catalog-details" href="/{choose('proyectos', 'projects')}/{pid}.html" aria-label="{choose('Ver ficha de ', 'View details for ')}{escape(name, quote=True)}">{choose('Ver proyecto', 'View project')}{ARROW}</a></div></article>''')
        steps = ''.join(f'<li><span>{i:02d}</span>{escape(step)}</li>' for i, step in enumerate(p['scope'][lang], 1))
        note = choose('Captura de la interfaz del proyecto. El estado de desarrollo se indica en esta ficha.', 'Captured project interface. The development stage is identified in this entry.') if p['image'] else ''
        if p['image'] and p['status'] in ('demo', 'prototype'):
            note = choose('Captura de la aplicación de demostración; contiene datos de ejemplo.', 'Screenshot of the demonstration application; includes example data.')
        if p.get('imageKind') == 'presentation':
            note = choose('Portada original de presentación del proyecto.', 'Original project presentation cover.')
        original = f'<a class="text-link cover-original" href="/assets/{p["image"]}.webp" target="_blank" rel="noopener">{choose("Abrir portada a tamaño completo", "Open full-size cover")}{ARROW}</a>' if p['image'] else ''
        dialogs.append(f'''<dialog class="project-dialog catalog-dialog" id="project-{pid}" aria-labelledby="project-title-{pid}"><div class="project-viewer-bar"><span>{escape(name)}</span><button class="dialog-close" type="button" data-close-project aria-label="{choose('Cerrar proyecto', 'Close project')}">{CLOSE}</button></div><div class="dialog-layout">{img(p, lang, True)}<div class="dialog-info"><p class="eyebrow">{status}</p><h2 id="project-title-{pid}">{escape(name)}</h2><p>{escape(p['summary'][lang])}</p><ol class="project-flow">{steps}</ol><p class="project-disclaimer">{note}</p><div class="project-viewer-actions">{original}<a class="text-link" href="/{choose('contacto', 'contact')}.html?servicio=app_personalizada" data-service="app_personalizada">{choose('Conversemos sobre una solución así', 'Let’s discuss a solution like this')}{ARROW}</a></div></div></div></dialog>''')
    count = len(PROJECTS)
    intro = f'<section class="page-intro project-photo-intro project-cover-intro"><div class="wrap"><div><p class="eyebrow">{choose("Proyectos", "Projects")} / KATIA.AI</p><h1 id="page-title">{choose("Nuestro trabajo,<br>a primera vista.", "Our work,<br>at a glance.")}</h1><p class="page-description">{choose("Conoce el diseño de nuestras aplicaciones y las soluciones que construimos.", "Discover the design of our applications and the solutions we build.")}</p></div></div></section>'
    content = f'''<section class="section catalog-section" id="proyectos" data-project-catalog aria-label="{choose('Catálogo de proyectos', 'Project catalog')}"><div class="wrap"><div class="catalog-toolbar" data-project-controls hidden><div class="catalog-search-row"><label class="catalog-search" for="project-search"><span>{choose('Encuentra un proyecto', 'Find a project')}</span><input id="project-search" type="search" placeholder="{choose('Nombre, industria o tecnología…', 'Name, industry or technology…')}" autocomplete="off" aria-controls="project-grid"></label><p id="project-count" class="catalog-count" role="status" aria-live="polite">{count} {choose('proyectos', 'projects')}</p></div><div class="catalog-filters" role="group" aria-label="{choose('Filtrar por solución', 'Filter by solution')}">{filters}</div></div><div class="catalog-grid" id="project-grid">{''.join(cards)}</div><div class="catalog-empty" data-project-empty hidden><h2>{choose('No encontramos coincidencias.', 'No matching projects.')}</h2><p>{choose('Prueba otro término o explora todas las soluciones.', 'Try another term or explore all solutions.')}</p><button type="button" class="btn btn-outline" data-project-reset>{choose('Mostrar todos', 'Show all')}</button></div><button type="button" class="btn btn-outline catalog-more" data-project-more aria-controls="project-grid" hidden>{choose('Ver más proyectos', 'Show more projects')}</button><p class="catalog-note">{choose('Portadas de nuestras aplicaciones y fichas de alcance. Cada proyecto indica su estado de desarrollo; las demos pueden mostrar datos de ejemplo.', 'Application covers and project scope. Each entry identifies its development stage; demos may show example data.')}</p></div></section>{''.join(dialogs)}'''
    return intro + content

TECH = json.loads((ROOT / 'content/technologies.json').read_text())
TECH_GROUPS = [
    ('ai', ['Inteligencia artificial', 'Artificial intelligence'], '<rect x="6" y="6" width="12" height="12" rx="3"/><path d="M9 2v4m6-4v4M9 18v4m6-4v4M2 9h4m-4 6h4m12-6h4m-4 6h4"/>'),
    ('automation', ['Automatización y datos', 'Automation & data'], '<rect x="2" y="8" width="6" height="8" rx="2"/><rect x="16" y="2" width="6" height="6" rx="2"/><rect x="16" y="16" width="6" height="6" rx="2"/><path d="M8 12h4m0 0V5h4m-4 7v7h4"/>'),
    ('finance', ['Gestión y finanzas', 'Management & finance'], '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M7 15h4m4 0h2"/>'),
    ('growth', ['Comercio y crecimiento', 'Commerce & growth'], '<path d="M4 4v16h16M8 14l4-4 4 2 4-7m-5 0h5v5"/>'),
    ('communication', ['Atención y productividad', 'Support & productivity'], '<path d="M21 11a8 8 0 0 1-8 8H8l-5 3v-7a8 8 0 0 1 7-12h3a8 8 0 0 1 8 8Z"/><path d="M8 9h8m-8 4h5"/>'),
    ('development', ['Apps e infraestructura', 'Apps & infrastructure'], '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 8h18m-12 4-3 3 3 3m6-6 3 3-3 3"/>'),
]

def technologies(lang, compact):
    choose = lambda es, en: en if lang else es
    title = choose('Tecnologías con las que trabajamos.', 'Technologies we work with.')
    if compact:
        names = ''
        for t in (tool for tool in TECH if tool['featured']):
            sub = f'<small>{escape(t["sub"])}</small>' if t['sub'] else ''
            names += f'<li><a href="/{choose("servicios", "services")}.html#tecnologias">{escape(t["name"])}{sub}</a></li>'
        more = choose(f'Ver las {len(TECH)} herramientas', f'View all {len(TECH)} tools')
        return f'<section class="technology-strip" aria-labelledby="technology-title"><div class="wrap"><div class="technology-strip-head"><h2 id="technology-title">{title}</h2><a class="text-link" href="/{choose("servicios", "services")}.html#tecnologias">{more}{ARROW}</a></div><ul class="technology-names" aria-label="{title}">{names}</ul></div></section>'
    groups = []
    for key, labels, icon in TECH_GROUPS:
        items = ''
        for t in (tool for tool in TECH if tool['group'] == key):
            display = escape(t['name'] + (' ' + t['sub'] if t['sub'] else ''))
            items += f'<li><a class="technology-item" href="{escape(t["url"], quote=True)}" target="_blank" rel="noopener"><div><strong>{display}</strong><span>{escape(t["description"][lang])}</span></div>{ARROW}<span class="sr-only">{choose("Sitio oficial; abre en otra pestaña", "Official website; opens in a new tab")}</span></a></li>'
        groups.append(f'<div class="technology-group"><h3><svg class="technology-group-icon" viewBox="0 0 24 24" aria-hidden="true">{icon}</svg>{escape(labels[lang])}</h3><ul>{items}</ul></div>')
    return f'<section class="section technology-section" id="tecnologias" aria-labelledby="technology-title"><div class="wrap"><div class="section-top"><div><p class="eyebrow">{choose("Nuestro ecosistema tecnológico", "Our technology ecosystem")}</p><h2 id="technology-title">{title}</h2></div><p>{choose("IA, gestión, comunicación y desarrollo: un ecosistema conectado para tu empresa.", "AI, management, communication and development: a connected ecosystem for your business.")}</p></div><div class="technology-group-grid">{"".join(groups)}</div><p class="catalog-note">{choose("Seleccionamos las herramientas y definimos permisos, datos, integraciones y supervisión según las necesidades de cada proyecto.", "We select tools and define permissions, data, integrations and oversight around each project’s needs.")}</p></div></section>'

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
                p = next(item for item in PROJECTS if item['id'] == pid)
                href = ('/projects/' if lang else '/proyectos/') + pid + '.html'
                name = p.get('nameEn', p['name']) if lang else p['name']
                label = ('Explore project ' if lang else 'Explorar proyecto ') + name
                cover = f'<a class="project-cover" aria-label="{escape(label, quote=True)}" href="{href}">{img(p, lang)}</a>'
                identity = f'<div class="home-project-identity"><span>{escape(name)}</span><small>{STATUS[p["status"]][lang]}</small></div>'
                def update_feature(m):
                    card = re.sub(r'<div class="home-project-identity">.*?</div>', '', m[0], flags=re.S)
                    return re.sub(r'<a class="project-cover".*?</a>', lambda _: cover + identity, card, count=1, flags=re.S)
                text = re.sub(r'<article class="project-tile project-' + pid + r'">.*?</article>', update_feature, text, count=1, flags=re.S)
        else:
            text = replace_block(text, 'technology-details', technologies(lang, False), '<section class="section ecosystem-section"')
        path.write_text(text)
print(f'Rendered {len(PROJECTS)} projects and {len(TECH)} technologies in Spanish and English.')
