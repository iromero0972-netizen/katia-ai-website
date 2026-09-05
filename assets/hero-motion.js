/* Hero color cycle; pauses offscreen, in hidden tabs, or on request. */
(function () {
  'use strict';
  const visual = document.querySelector('.hero-visual');
  const button = document.querySelector('.hero-motion-toggle');
  if (!visual || !button) return;

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const english = document.documentElement.lang === 'en';
  let userPaused = false;
  let inView = true;

  function syncMotion() {
    const enabled = !reduced.matches;
    const playing = enabled && !userPaused;
    visual.classList.toggle('motion-ready', enabled);
    visual.classList.toggle('motion-running', playing && inView && !document.hidden);
    button.hidden = !enabled;
    const label = english
      ? (userPaused ? 'Resume animation' : 'Pause animation')
      : (userPaused ? 'Reanudar animación' : 'Pausar animación');
    button.setAttribute('aria-label', label);
    button.setAttribute('title', label);
    button.dataset.paused = String(userPaused);
  }

  button.addEventListener('click', () => {
    userPaused = !userPaused;
    syncMotion();
  });
  document.addEventListener('visibilitychange', syncMotion);
  reduced.addEventListener('change', syncMotion);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      inView = entries[0].isIntersecting;
      syncMotion();
    }).observe(visual);
  }
  syncMotion();
}());
