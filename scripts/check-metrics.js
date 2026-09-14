/* Privacy and attribution boundaries: no browser, network, cookies or external events. */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const assetRoot = fs.existsSync(path.join(root, 'dist')) ? path.join(root, 'dist') : root;
const source = fs.readFileSync(path.join(assetRoot, 'assets/metrics.js'), 'utf8');
function setup(hostname, initialConsent) {
  let consent = initialConsent;
  const events = [];
  const handlers = {};
  const window = {KATIAPrivacy: {status: () => consent}, gtag: (...args) => events.push(args)};
  const document = {documentElement: {lang: 'es'}, addEventListener: (name, fn) => { handlers[name] = fn; }};
  vm.runInNewContext(source, {window, document, URL, location: {hostname, href: `https://${hostname}/contacto.html`}});
  return {events, metrics: window.KatiaMetrics, consent: value => { consent = value; }, click: href => handlers.click({target: {closest: () => ({href})}})};
}
for (const [host, consent] of [['katia-evolution.iromero0972.chatgpt.site', 'accepted'], ['katia.solutions', 'rejected'], ['katia.solutions', '']]) {
  const s = setup(host, consent);
  s.click('https://calendly.com/iromero0972/30min');
  s.metrics.leadReceived('agentes_ia');
  assert.equal(s.events.length, 0, 'No measurement outside consented production');
}
const active = setup('katia.solutions', 'accepted');
active.click('https://wa.me/13468920577?text=Synthetic%20Name%20test%40example.com');
active.click('https://calendly.com/iromero0972/30min');
active.click('tel:+13462204052');
active.metrics.leadReceived('app_personalizada');
assert.deepEqual(active.events.map(e => e[1]), ['contact_intent', 'booking_intent', 'contact_intent', 'lead_form_submit']);
const serialized = JSON.stringify(active.events);
assert(!/Synthetic|example.com|wa.me|1346|calendly|booking_confirmed/.test(serialized), 'Personal details, URLs and unconfirmed bookings must not be recorded');
assert.equal(active.events[3][2].service, 'app_personalizada');
active.metrics.leadReceived('test@example.com');
assert.equal(active.events[4][2].service, undefined, 'Unknown form values cannot enter event parameters');
active.consent('rejected');
active.click('mailto:ventas@katia.solutions');
assert.equal(active.events.length, 5, 'Consent is checked again on every event');
console.log('Measurement checks passed: consent, host, revocation, event meaning and data minimization.');
