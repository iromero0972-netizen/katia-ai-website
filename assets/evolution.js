/* KATIA.AI — progressively enhanced corporate website. No analytics or cookies in review. */
(function () {
  'use strict';
  const en = document.documentElement.lang === 'en';
  const say = (es, english) => en ? english : es;
  if (new URLSearchParams(location.search).get('lang') === 'en' && !en) {
    const target = document.querySelector('.lang a[lang="en"]');
    location.replace(target ? target.href : '/en.html');
    return;
  }
  const menu = document.querySelector('.menu-toggle');
  const navigation = document.getElementById('main-navigation');
  function closeMenu() {
    navigation.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', say('Abrir menú', 'Open menu'));
  }
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    navigation.classList.toggle('open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', say('Cerrar menú', 'Close menu'));
  });
  navigation.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('click', event => {
    if (!event.target.closest('.site-header')) closeMenu();
  });
  document.querySelectorAll('[data-service]').forEach(a => a.addEventListener('click', () => {
    const serviceField = document.getElementById('serviceInterest');
    if (serviceField) serviceField.value = a.dataset.service;
    const drawer = document.getElementById('contact-drawer');
    if (drawer) drawer.open = true;
  }));

  // Direct links keep the detailed catalog and resources easy to reach.
  function revealDetails(hash) {
    if (!hash || hash === '#') return;
    let target;
    try { target = document.getElementById(decodeURIComponent(hash.slice(1))); }
    catch { return; }
    if (!target) return;
    let opened = false;
    for (let node = target; node; node = node.parentElement) {
      if (node.tagName === 'DETAILS' && !node.open) {
        node.open = true;
        opened = true;
      }
    }
    if (opened) requestAnimationFrame(() => target.scrollIntoView({block: 'start'}));
  }
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#"]');
    if (anchor) revealDetails(anchor.hash);
  });
  window.addEventListener('hashchange', () => revealDetails(location.hash));
  revealDetails(location.hash);

  const cases = {
    retail: [
      ['De la venta al control de inventario.', 'Pedido recibido en tu tienda', 'Inventario y documentos conectados', 'Seguimiento y visibilidad del margen'],
      ['From a sale to inventory visibility.', 'Order received in your store', 'Connected inventory and documents', 'Follow-up and margin visibility']
    ],
    professional: [
      ['Del primer contacto al cobro.', 'Solicitud del cliente organizada', 'Propuesta y seguimiento de tareas', 'Facturación y cobranza supervisadas'],
      ['From first contact to collection.', 'Organized customer inquiry', 'Proposal and task follow-up', 'Supervised invoicing and collections']
    ],
    construction: [
      ['Cada proyecto, con más control.', 'Estimado y alcance documentados', 'Gastos y avances por proyecto', 'Alertas de cobro y reporte de costos'],
      ['More control over each project.', 'Documented estimate and scope', 'Project expenses and progress', 'Collection alerts and cost reports']
    ],
    food: [
      ['Una operación mejor conectada.', 'Pedidos y comprobantes organizados', 'Compras y costos por categoría', 'Reporte de márgenes para revisión'],
      ['A better-connected operation.', 'Organized orders and receipts', 'Purchases and costs by category', 'Margin report for review']
    ],
    beauty: [
      ['Más atención a cada cliente.', 'Cita registrada y confirmada', 'Recordatorios y seguimiento', 'Comisiones y reportes organizados'],
      ['More attention for every customer.', 'Recorded and confirmed appointment', 'Reminders and follow-up', 'Organized commissions and reports']
    ]
  };
  document.querySelectorAll('[data-industry]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-industry]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    const values = cases[button.dataset.industry][en ? 1 : 0];
    ['case-title', 'case-one', 'case-two', 'case-three'].forEach((id, i) => document.getElementById(id).textContent = values[i]);
  }));
  function estimate(hours, rate, percent) {
    if (![hours, rate, percent].every(Number.isFinite) || hours < 0 || hours > 168 || rate < 0 || rate > 1000 || percent < 0 || percent > 100) return null;
    const time = hours * 52 / 12 * percent / 100;
    return {time, value: time * rate};
  }
  const calcInputs = ['calc-hours', 'calc-rate', 'calc-percent'].map(id => document.getElementById(id));
  function calculate() {
    const result = estimate(...calcInputs.map(input => input.value === '' ? NaN : Number(input.value)));
    document.getElementById('calc-time').textContent = result ? result.time.toLocaleString(en ? 'en-US' : 'es-US', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' h' : '—';
    document.getElementById('calc-value').textContent = result ? result.value.toLocaleString('en-US', {style: 'currency', currency: 'USD', maximumFractionDigits: 0}) : '—';
  }
  if (calcInputs.every(Boolean)) {
    calcInputs.forEach(input => input.addEventListener('input', calculate));
    calculate();
  }

  function containsSensitive(value) {
    return /\b\d{3}-?\d{2}-?\d{4}\b/.test(value) || /\b(?:\d[ -]?){13,19}\b/.test(value);
  }
  const privacyWarning = say('No incluyas números de tarjeta, SSN/ITIN ni datos bancarios. Comparte solo una descripción general.', 'Do not include card numbers, SSN/ITIN or banking information. Share only a general description.');
  async function request(url, payload, timeout = 25000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload), signal: controller.signal, credentials: 'omit'});
      if (!response.ok) throw new Error('Request failed');
      const content = await response.text();
      let data = {};
      if (content) {
        try {data = JSON.parse(content);} catch {data = {raw: content};}
      }
      if (data && (data.success === false || data.ok === false || data.error)) throw new Error('Service did not accept request');
      return data || {};
    } finally {clearTimeout(timer);}
  }
  const form = document.getElementById('contactForm');
  const selectedService = new URLSearchParams(location.search).get('servicio');
  const serviceField = document.getElementById('serviceInterest');
  if (selectedService && serviceField && [...serviceField.options].some(option => option.value === selectedService)) {
    serviceField.value = selectedService;
  }
  const leadStatus = document.getElementById('form-status');
  let leadBusy = false;
  function status(message, state) {
    leadStatus.textContent = message;
    leadStatus.dataset.state = state;
  }
  function formValue(name) {return String(form.elements.namedItem(name)?.value || '').trim();}
  function problemForService(service) {
    return service === 'dashboards_control' ? 'cierre_reportes' : 'multiples_areas';
  }
  function makeLead() {
    const service = formValue('servicio_interes');
    const sector = formValue('sector');
    const problem = problemForService(service);
    const consent = form.elements.namedItem('consent').checked;
    return {
      nombre: formValue('nombre'), empresa: formValue('empresa'), email: formValue('email'), telefono: '',
      servicio_interes: service,
      industria: sector, industria_codigo: sector, industry_code: sector,
      industria_legacy: form.elements.namedItem('sector').selectedOptions[0]?.textContent || '',
      dolor: problem, dolor_codigo: problem, problem_code: problem, dolor_legacy: say('Ver contexto de la solicitud', 'See inquiry context'),
      notas: formValue('mensaje'), consent, consentimiento: consent,
      consent_timestamp: new Date().toISOString(), privacy_version: '2026-07-13',
      source: 'website_form_v3', fuente: 'website_form_v3'
    };
  }
  form?.addEventListener('submit', async event => {
    event.preventDefault();
    if (leadBusy || !form.reportValidity()) return;
    if (formValue('website')) {status(say('No pudimos validar la solicitud. Puedes contactarnos por correo.', 'We could not validate your inquiry. You can contact us by email.'), 'error'); return;}
    const payload = makeLead();
    if (!payload.nombre || !payload.empresa || !payload.consent || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(payload.email)) {
      status(say('Revisa tu nombre, empresa, correo y consentimiento.', 'Please check your name, company, email and consent.'), 'error'); return;
    }
    if (containsSensitive(payload.notas + ' ' + payload.nombre + ' ' + payload.empresa)) {status(privacyWarning, 'error'); return;}
    if (!window.KatiaRequestGuard) {status(say('Espera un momento y vuelve a intentarlo.', 'Please wait a moment and try again.'), 'error');return;}
    const guard = window.KatiaRequestGuard.validateLead(payload);
    if (!guard.ok) {status(en ? 'Please check that your message contains no sensitive data, or continue by WhatsApp if you have reached the request limit.' : guard.message, 'error');return;}
    leadBusy = true;
    const submit = document.getElementById('lead-submit');
    const originalLabel = submit.innerHTML;
    submit.disabled = true;
    submit.textContent = say('Enviando…', 'Sending…');
    status(say('Procesando tu solicitud.', 'Processing your request.'), 'pending');
    try {
      await request('https://srv1448901.hstgr.cloud/webhook/katia2-lead-capture', payload);
      status(say('Tu solicitud fue recibida. También puedes elegir una fecha en la agenda. La cita se confirma al completar la reserva.', 'Your inquiry was received. You can also choose a time in the calendar. Your appointment is confirmed when you complete the booking.'), 'success');
      if (typeof window.gtag === 'function') window.gtag('event', 'lead_form_submit', {industria: payload.industria});
      form.reset();
    } catch {
      status(say('No pudimos confirmar la recepción. Conservamos tus datos en el formulario; puedes continuar por WhatsApp o correo, o agendar directamente.', 'We could not confirm receipt. Your details are still in the form; continue by WhatsApp or email, or book directly.'), 'error');
    } finally {
      submit.disabled = false;
      submit.innerHTML = originalLabel;
      leadBusy = false;
    }
  });
  function fallbackMessage() {
    const name = formValue('nombre');
    const company = formValue('empresa');
    const note = formValue('mensaje');
    if (containsSensitive(name + company + note)) return null;
    return say('Hola KATIA, me interesa un diagnóstico para mi negocio.', 'Hello KATIA, I am interested in a consultation for my business.') +
      (name ? '\n' + say('Nombre: ', 'Name: ') + name : '') +
      (company ? '\n' + say('Empresa: ', 'Company: ') + company : '') +
      (note ? '\n' + note : '');
  }
  [['lead-whatsapp', 'whatsapp'], ['lead-email', 'email']].forEach(([id, channel]) => {
    document.getElementById(id)?.addEventListener('click', function (event) {
      const message = fallbackMessage();
      if (message === null) {event.preventDefault();status(privacyWarning, 'error');return;}
      this.href = channel === 'whatsapp' ? 'https://wa.me/13468920577?text=' + encodeURIComponent(message) : 'mailto:ventas@katia.solutions?subject=' + encodeURIComponent(say('Diagnóstico KATIA.AI', 'KATIA.AI consultation')) + '&body=' + encodeURIComponent(message);
    });
  });

  const toggle = document.getElementById('chat-toggle');
  const panel = document.getElementById('chat-panel');
  const chatInput = document.getElementById('chat-message');
  const chatBody = document.getElementById('chat-body');
  let chatBusy = false;
  let sessionId = null;
  function openChat(open) {
    panel.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    (open ? chatInput : toggle).focus({preventScroll: true});
  }
  toggle.addEventListener('click', () => openChat(panel.hidden));
  document.getElementById('chat-close').addEventListener('click', () => openChat(false));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      if (!panel.hidden) openChat(false);
      else if (navigation.classList.contains('open')) {closeMenu();menu.focus();}
    }
  });
  function message(text, type = '') {
    const element = document.createElement('div');
    element.className = 'message' + (type ? ' ' + type : '');
    element.textContent = text;
    chatBody.appendChild(element);
    chatBody.scrollTop = chatBody.scrollHeight;
    return element;
  }
  document.getElementById('chat-form').addEventListener('submit', async event => {
    event.preventDefault();
    const text = chatInput.value.trim();
    if (!text || chatBusy) return;
    if (text.length > 1000 || containsSensitive(text)) {message(privacyWarning, 'error');return;}
    if (!window.KatiaRequestGuard) {message(say('Espera un momento y vuelve a intentarlo.', 'Please wait a moment and try again.'), 'error');return;}
    const guard = window.KatiaRequestGuard.validateChat(text);
    if (!guard.ok) {message(en ? 'Please check that your message contains no sensitive data, or continue by WhatsApp if you have reached the message limit.' : guard.message, 'error');return;}
    chatBusy = true;
    const submit = event.currentTarget.querySelector('button');
    submit.disabled = true;
    message(text, 'user');
    chatInput.value = '';
    const pending = message(say('KATIA está respondiendo…', 'KATIA is responding…'));
    try {
      sessionId ||= 'katia-web-' + (globalThis.crypto?.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2));
      const data = await request('https://srv1448901.hstgr.cloud/webhook/b3-chat', {message: text, session_id: sessionId, source: 'website_chat_hybrid_v3', lang: en ? 'en' : 'es'});
      if (typeof data.response !== 'string' || !data.response.trim()) throw new Error('Missing response');
      pending.textContent = data.response;
    } catch {
      pending.classList.add('error');
      pending.textContent = say('No pude obtener una respuesta. Puedes hablar con nosotros por WhatsApp o elegir una hora en la agenda desde los enlaces de abajo.', 'I could not get a response. You can reach us by WhatsApp or choose a calendar time using the links below.');
    } finally {
      chatBusy = false;
      submit.disabled = false;
      chatBody.scrollTop = chatBody.scrollHeight;
    }
  });
  // Project dossiers use native dialogs: keyboard focus, Escape and return focus.
  document.querySelectorAll('[data-project]').forEach(button => {
    button.addEventListener('click', () => {
      const dialog = document.getElementById('project-' + button.dataset.project);
      if (dialog && !dialog.open) dialog.showModal();
    });
  });
  document.querySelectorAll('.project-dialog').forEach(dialog => {
    dialog.querySelectorAll('[data-close-project]').forEach(button => button.addEventListener('click', () => dialog.close()));
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    });
  });
  /* Existing July hashes keep their destinations after the redesign. */
  const legacyHashes = {servicios: 'soluciones',services: 'soluciones',methodology: 'metodo',metodologia: 'metodo',planes: 'preguntas',pricing: 'preguntas',faq: 'preguntas',contact: 'contacto',about: 'nosotros',company: 'nosotros',testimonios: 'nosotros',problema: 'soluciones',app: 'soluciones'};
  const mapped = legacyHashes[location.hash.slice(1)];
  if (mapped && document.getElementById(mapped)) location.hash = mapped;
  const destination = mapped || location.hash.slice(1);
  if (destination && !document.getElementById(destination)) {
    const routes = en
      ? {soluciones:'/services.html',catalogo:'/services.html',ecosistema:'/services.html#ecosistema',industrias:'/services.html#industrias',proyectos:'/projects.html',nosotros:'/about.html',metodo:'/about.html#metodo',confianza:'/about.html#confianza',preguntas:'/guide.html#preguntas',agentes:'/contact.html#agentes',contacto:'/contact.html'}
      : {soluciones:'/servicios.html',catalogo:'/servicios.html',ecosistema:'/servicios.html#ecosistema',industrias:'/servicios.html#industrias',proyectos:'/proyectos.html',nosotros:'/nosotros.html',metodo:'/nosotros.html#metodo',confianza:'/nosotros.html#confianza',preguntas:'/guia.html#preguntas',agentes:'/contacto.html#agentes',contacto:'/contacto.html'};
    if (routes[destination]) location.replace(routes[destination]);
  }
}());
