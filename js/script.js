document.documentElement.classList.add('js-ready');

document.addEventListener('DOMContentLoaded', () => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const header = document.querySelector('[data-header]');
  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.site-nav');

  const setHeaderState = () => header?.classList.toggle('is-scrolled', window.scrollY > 18);
  setHeaderState();
  window.addEventListener('scroll', setHeaderState, { passive: true });

  const closeMenu = () => {
    menu?.classList.remove('is-open');
    menuButton?.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('menu-open');
  };

  menuButton?.addEventListener('click', () => {
    const willOpen = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(willOpen));
    menu?.classList.toggle('is-open', willOpen);
    document.body.classList.toggle('menu-open', willOpen);
  });

  menu?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  window.addEventListener('resize', () => {
    if (window.innerWidth > 860) closeMenu();
  });

  const splitHeading = (heading) => {
    const walker = document.createTreeWalker(heading, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);

    let wordIndex = 0;
    textNodes.forEach((node) => {
      if (!node.textContent.trim()) return;
      const fragment = document.createDocumentFragment();
      node.textContent.split(/(\s+)/).forEach((part) => {
        if (!part.trim()) {
          fragment.appendChild(document.createTextNode(part));
          return;
        }
        const outer = document.createElement('span');
        const inner = document.createElement('span');
        outer.className = 'word';
        inner.className = 'word-inner';
        inner.textContent = part;
        outer.style.setProperty('--word-delay', `${100 + wordIndex * 65}ms`);
        outer.appendChild(inner);
        fragment.appendChild(outer);
        wordIndex += 1;
      });
      node.replaceWith(fragment);
    });
  };

  document.querySelectorAll('[data-split]').forEach(splitHeading);

  const countUp = (element) => {
    if (element.dataset.counted) return;
    element.dataset.counted = 'true';
    const target = Number(element.dataset.count || 0);
    const suffix = element.dataset.suffix || '';
    const start = performance.now();
    const duration = 1100;

    const frame = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      element.textContent = `${Math.round(target * eased)}${suffix}`;
      if (progress < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  };

  const revealElements = [...document.querySelectorAll('[data-reveal], [data-split]')];
  revealElements.forEach((element, index) => {
    element.style.setProperty('--delay', `${Math.min(index % 4, 3) * 70}ms`);
  });

  if (reducedMotion || !('IntersectionObserver' in window)) {
    revealElements.forEach((element) => element.classList.add('is-visible'));
    document.querySelectorAll('[data-count]').forEach(countUp);
  } else {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        entry.target.querySelectorAll?.('[data-count]').forEach(countUp);
        if (entry.target.matches('[data-count]')) countUp(entry.target);
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -6% 0px' });

    revealElements.forEach((element) => observer.observe(element));
  }

  const revealAnchorTarget = () => {
    if (!window.location.hash) return;
    const target = document.querySelector(window.location.hash);
    if (!target) return;

    target.querySelectorAll('[data-reveal], [data-split]').forEach((element) => {
      element.classList.add('is-visible');
      element.querySelectorAll?.('[data-count]').forEach(countUp);
    });
    if (target.matches('[data-reveal], [data-split]')) target.classList.add('is-visible');
    window.scrollTo({ top: Math.max(target.offsetTop - 92, 0), behavior: 'auto' });
  };

  revealAnchorTarget();
  window.addEventListener('load', () => window.setTimeout(revealAnchorTarget, 80), { once: true });
  window.addEventListener('hashchange', revealAnchorTarget);

});
