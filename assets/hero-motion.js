/* Hero color cycle; pauses offscreen, in hidden tabs, or on request. */
(function () {
  'use strict';
  const visual = document.querySelector('.philosophy-media, .hero-visual');
  const button = document.querySelector('.hero-motion-toggle');
  if (!visual || !button) return;

  const video = visual.querySelector('.hero-video');
  if (video) {
    const english = document.documentElement.lang === 'en';
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    let userPaused = reduced.matches || Boolean(navigator.connection?.saveData);
    let inView = true;
    let failed = false;
    let starting = false;
    video.muted = true;
    video.controls = false;
    button.hidden = false;

    function updateButton() {
      const paused = video.paused;
      const label = english ? (paused ? 'Play video' : 'Pause video')
        : (paused ? 'Reproducir video' : 'Pausar video');
      button.dataset.paused = String(paused);
      button.setAttribute('aria-label', label);
      button.setAttribute('title', label);
      button.hidden = failed;
    }
    function syncVideo() {
      if (failed || userPaused || !inView || document.hidden) {
        video.pause();
      } else if (video.paused && !starting) {
        starting = true;
        video.play().then(() => {
          starting = false;
          if (userPaused || !inView || document.hidden) video.pause();
          updateButton();
        }).catch(error => {
          starting = false;
          // A pause can cancel a pending play request. A blocked autoplay
          // leaves a working, explicit play button and the poster visible.
          if (error.name !== 'AbortError') userPaused = true;
          updateButton();
        });
      }
      updateButton();
    }
    button.addEventListener('click', () => {
      userPaused = !video.paused;
      syncVideo();
    });
    video.addEventListener('play', updateButton);
    video.addEventListener('pause', updateButton);
    video.addEventListener('error', () => { failed = true; syncVideo(); });
    document.addEventListener('visibilitychange', syncVideo);
    reduced.addEventListener('change', () => {
      userPaused = reduced.matches;
      syncVideo();
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {
        inView = entries[0].isIntersecting;
        syncVideo();
      }).observe(visual);
    }
    syncVideo();
    return;
  }

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
      ? (userPaused ? 'Resume color changes' : 'Pause color changes')
      : (userPaused ? 'Reanudar cambio de colores' : 'Pausar cambio de colores');
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
