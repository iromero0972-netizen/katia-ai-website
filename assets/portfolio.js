(() => {
  'use strict';
  const catalog = document.querySelector('[data-project-catalog]');
  if (!catalog) return;
  const search = catalog.querySelector('#project-search');
  const filters = [...catalog.querySelectorAll('[data-project-filter]')];
  const cards = [...catalog.querySelectorAll('[data-project-card]')];
  const count = catalog.querySelector('#project-count');
  const more = catalog.querySelector('[data-project-more]');
  const empty = catalog.querySelector('[data-project-empty]');
  const en = document.documentElement.lang === 'en';
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  const entries = cards.map(card => ({card, text: normalize(card.dataset.search), categories: card.dataset.categories.split(' ')}));
  let category = 'all';
  let limit = 6;
  function render() {
    const words = normalize(search.value).split(/\s+/).filter(Boolean);
    const matches = entries.filter(entry => (category === 'all' || entry.categories.includes(category)) && words.every(word => entry.text.includes(word)));
    const visible = new Set(matches.slice(0, limit).map(entry => entry.card));
    cards.forEach(card => { card.hidden = !visible.has(card); });
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.projectFilter === category)));
    count.textContent = en ? `${visible.size} of ${matches.length} projects` : `${visible.size} de ${matches.length} proyectos`;
    more.hidden = matches.length <= limit;
    more.textContent = en ? `Show more projects (${matches.length - visible.size})` : `Ver más proyectos (${matches.length - visible.size})`;
    empty.hidden = matches.length !== 0;
    return matches;
  }
  filters.forEach(button => button.addEventListener('click', () => { category = button.dataset.projectFilter; limit = 6; render(); }));
  search.addEventListener('input', () => { limit = 6; render(); });
  catalog.querySelector('[data-project-reset]').addEventListener('click', () => { search.value = ''; category = 'all'; limit = 6; render(); search.focus(); });
  more.addEventListener('click', () => {
    const previousLimit = limit;
    limit += 6;
    const matches = render();
    matches[previousLimit]?.card.focus();
  });
  function revealHash() {
    const target = cards.find(card => '#' + card.id === location.hash);
    if (!target) return;
    search.value = ''; category = 'all'; limit = Math.max(6, cards.indexOf(target) + 1); render();
    target.scrollIntoView({block: 'start', behavior: 'instant'});
  }
  catalog.querySelector('[data-project-controls]').hidden = false;
  render();
  revealHash();
  window.addEventListener('hashchange', revealHash);
})();
