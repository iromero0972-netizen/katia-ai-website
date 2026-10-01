/* Aggregate intent events only. Consent, production host and an existing GA client are required. */
(() => {
  'use strict';
  const production = ['katia.solutions', 'www.katia.solutions'].includes(location.hostname);
  const services = new Set(['automatizacion_procesos', 'agentes_ia', 'app_personalizada', 'ecommerce_multicanal', 'integraciones_erp_api', 'dashboards_control']);
  const channels = new Set(['phone', 'whatsapp', 'email', 'calendar']);
  const placements = new Set(['hero', 'next_step', 'header', 'quick_contact', 'other']);
  function emit(event, parameters) {
    if (!production || window.KATIAPrivacy?.status() !== 'accepted' || typeof window.gtag !== 'function') return;
    const payload = {language: document.documentElement.lang === 'en' ? 'en' : 'es'};
    if (channels.has(parameters.channel)) payload.channel = parameters.channel;
    if (services.has(parameters.service)) payload.service = parameters.service;
    if (placements.has(parameters.placement)) payload.placement = parameters.placement;
    // Never collect link URLs, query strings, form values, contact details or message text.
    window.gtag('event', event, payload);
  }
  window.KatiaMetrics = Object.freeze({
    leadReceived(service) { emit('lead_form_submit', {service}); }
  });
  document.addEventListener('click', event => {
    const link = event.target.closest?.('a[href]');
    if (!link) return;
    let target;
    try { target = new URL(link.href, location.href); } catch { return; }
    const selected = link.dataset?.placement;
    const placement = placements.has(selected) ? selected
      : link.closest?.('.quick-contact') ? 'quick_contact'
      : link.closest?.('.site-header') ? 'header' : 'other';
    if (target.protocol === 'tel:') emit('contact_intent', {channel: 'phone', placement});
    else if (target.protocol === 'mailto:') emit('contact_intent', {channel: 'email', placement});
    else if (target.hostname === 'wa.me') emit('contact_intent', {channel: 'whatsapp', placement});
    else if (target.hostname === 'calendly.com') emit('booking_intent', {channel: 'calendar', placement});
  });
})();
