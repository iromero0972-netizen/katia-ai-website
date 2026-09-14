#!/usr/bin/env python3
"""Keep the bilingual quick-contact entry points consistent on every reviewed page."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
ICONS = {
    'chat': '<path d="M21 11a8 8 0 0 1-8 8H8l-5 3V11a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8Z"/><path d="M7 9h10M7 13h7"/>',
    'phone': '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.8 2.1Z"/>',
    'calendar': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18m-14 5 3 3 6-5"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
    'form': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    'arrow': '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    'close': '<path d="m6 6 12 12M18 6 6 18"/>',
}

def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'

def render_dialog(en, contact):
    def t(es, english): return english if en else es
    def choice(href, title, note, symbol, primary=False, extra=''):
        return (f'<a class="contact-choice{" contact-choice-primary" if primary else ""}" href="{escape(href, quote=True)}"{extra}>'
                f'<span class="contact-choice-icon">{icon(symbol)}</span><span class="contact-choice-copy">'
                f'<strong>{title}</strong><span>{note}</span></span>{icon("arrow")}</a>')
    leo = choice('tel:+13462204052', t('Llamar a Leo', 'Call Leo'),
                 t('Agente IA por teléfono', 'AI phone agent') + '<span class="contact-number">+1 346 220 4052</span>', 'phone', True)
    andres = choice('https://wa.me/13468920577', t('WhatsApp con Andrés', 'WhatsApp with Andrés'),
                    t('Agente IA por mensaje', 'AI messaging agent') + '<span class="contact-number">+1 346 892 0577</span>', 'chat', True,
                    ' target="_blank" rel="noopener"')
    chat = (f'<button class="contact-choice" type="button" data-contact-chat>'
            f'<span class="contact-choice-icon">{icon("chat")}</span><span class="contact-choice-copy">'
            f'<strong>{t("Chat en esta web", "Chat on this website")}</strong>'
            f'<span>{t("Pregunta a nuestro asistente IA", "Ask our AI assistant")}</span></span>{icon("arrow")}</button>')
    calendar = choice('https://calendly.com/iromero0972/30min', t('Agendar una reunión', 'Book a meeting'),
                      t('30 minutos · Sin costo', '30 minutes · Complimentary'), 'calendar', extra=' target="_blank" rel="noopener"')
    email = choice('mailto:ventas@katia.solutions', t('Escribir por correo', 'Send an email'), 'ventas@katia.solutions', 'mail')
    form = choice(contact, t('Cuéntanos tu proyecto', 'Tell us about your project'), t('Formulario de contacto', 'Contact form'), 'form')
    return (f'<!-- quick-contact:start --><dialog class="quick-contact" id="quick-contact" aria-labelledby="quick-contact-title" aria-describedby="quick-contact-description">'
            f'<div class="quick-contact-heading"><div><p class="contact-brand">KATIA.AI · ES / EN</p>'
            f'<h2 id="quick-contact-title">{t("Hablemos.", "Let’s talk.")}</h2>'
            f'<p id="quick-contact-description">{t("Elige cómo prefieres contactarnos.", "Choose how you’d like to reach us.")}</p></div>'
            f'<button class="quick-contact-close" type="button" data-contact-close aria-label="{t("Cerrar opciones de contacto", "Close contact options")}" autofocus>{icon("close")}</button></div>'
            f'<div class="quick-contact-body"><div class="contact-primary-grid">{leo}{andres}</div>'
            f'<div class="contact-secondary-grid">{chat}{calendar}{email}{form}</div>'
            f'<div class="quick-contact-social"><span>{t("También en redes", "Find us on social")}</span>'
            f'<div><a href="https://www.instagram.com/katia.ai_/" target="_blank" rel="noopener">Instagram{icon("arrow")}</a>'
            f'<a href="https://www.facebook.com/profile.php?id=61575396974517" target="_blank" rel="noopener">Facebook{icon("arrow")}</a></div>'
            f'</div></div></dialog><!-- quick-contact:end -->')

pages = json.loads((ROOT / 'content/page-inventory.json').read_text())
for page in pages:
    path = DIST / page['path']
    html = path.read_text()
    en = bool(re.search(r'<html\b[^>]*lang="en"', html))
    contact = '/contact.html#contacto' if en else '/contacto.html#contacto'
    label = 'Contact us' if en else 'Contactar'
    attrs = f'href="{contact}" data-contact-open aria-haspopup="dialog" aria-controls="quick-contact" aria-expanded="false"'
    header = f'<a class="btn contact-header-trigger" {attrs} aria-label="{label}">{icon("chat")}<span>{label}</span></a>'
    html, count = re.subn(r'(<div class="nav-actions">.*?)<a class="btn[^\"]*"[^>]*>.*?</a>',
                          lambda m: m[1] + header, html, count=1, flags=re.S)
    assert count == 1, f'Header contact missing: {path}'
    if page['path'] in ['index.html', 'en.html']:
        hero_label = 'Contact KATIA' if en else 'Contactar con KATIA'
        html, count = re.subn(r'(<div class="hero-actions">)<a\b[^>]*>.*?</a>',
                              lambda m: m[1] + f'<a class="btn" {attrs}>{hero_label}{icon("arrow")}</a>', html, count=1, flags=re.S)
        assert count == 1, f'Hero contact missing: {path}'
    launcher = f'<a class="chat-launcher contact-launcher" id="chat-toggle" {attrs}>{icon("chat")}<span>{label}</span></a>'
    html, count = re.subn(r'<(?:button|a)\b[^>]*id="chat-toggle"[^>]*>.*?</(?:button|a)>', lambda _: launcher, html, count=1, flags=re.S)
    assert count == 1, f'Contact launcher missing: {path}'
    html = re.sub(r'<!-- quick-contact:start -->.*?<!-- quick-contact:end -->', '', html, flags=re.S)
    html = html.replace('</body>', render_dialog(en, contact) + '</body>', 1)
    if '/assets/quick-contact.css' not in html:
        html = html.replace('</head>', '<link rel="stylesheet" href="/assets/quick-contact.css"></head>', 1)
    # The shared script changed; request this revision even if a browser cached the old one.
    html = re.sub(r'src="/assets/evolution.js(?:\?[^\"]*)?"', 'src="/assets/evolution.js?v=quick-contact-1"', html)
    path.write_text(html)
print(f'Quick contact rendered on {len(pages)} bilingual pages.')
