/* Sketchbot Studios — site behaviour (progressive enhancement, no framework) */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // ---- theme -------------------------------------------------------------
  const root = document.documentElement;
  const saved = (() => { try { return localStorage.getItem('theme'); } catch { return null; } })();
  if (saved) root.dataset.theme = saved;
  $$('.theme-toggle').forEach(b => b.addEventListener('click', () => {
    const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('theme', root.dataset.theme); } catch {}
  }));

  // ---- mobile nav --------------------------------------------------------
  const toggle = $('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => toggle.setAttribute('aria-expanded', toggle.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('click', e => { if (!e.target.closest('.site-header')) toggle.setAttribute('aria-expanded', 'false'); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') toggle.setAttribute('aria-expanded', 'false'); });
  }

  // ---- reveal fallback (browsers without scroll-driven animations) --------
  if (!CSS.supports('animation-timeline: view()')) {
    const io = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }), { rootMargin: '0px 0px -8% 0px' });
    $$('.reveal').forEach(el => io.observe(el));
  }

  // ---- lazy-load nudge: Chrome occasionally never kicks off lazy images inside scroll-driven reveals
  const lz = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) { en.target.loading = 'eager'; lz.unobserve(en.target); } }), { rootMargin: '400px 0px' });
  $$('img[loading="lazy"]').forEach(i => lz.observe(i));

  // ---- work filters ------------------------------------------------------
  const filters = $('.filters');
  if (filters) {
    const cards = $$('[data-cat]');
    filters.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      $$('button', filters).forEach(x => x.setAttribute('aria-pressed', x === b));
      const f = b.dataset.filter;
      cards.forEach(c => { c.hidden = !(f === 'all' || c.dataset.cat.split('|').includes(f)); });
      $('.work-grid')?.classList.toggle('is-filtered', f !== 'all');
    });
  }

  // ---- lightbox (native <dialog>) -----------------------------------------
  const gal = $$('.gallery figure');
  if (gal.length) {
    const dlg = document.createElement('dialog'); dlg.className = 'lightbox';
    dlg.innerHTML = `<div class="frame"><img alt=""></div><div class="cap" hidden></div>
      <button class="prev" aria-label="Previous">‹</button><button class="next" aria-label="Next">›</button><button class="x" aria-label="Close">×</button>`;
    document.body.append(dlg);
    const img = $('img', dlg), cap = $('.cap', dlg); let i = 0;
    const show = n => { i = (n + gal.length) % gal.length; const f = gal[i]; img.src = f.dataset.full; img.alt = $('img', f).alt;
      const c = f.querySelector('figcaption')?.textContent?.trim(); cap.hidden = !c; cap.textContent = c || ''; };
    gal.forEach((f, n) => f.addEventListener('click', () => { show(n); dlg.showModal(); }));
    $('.x', dlg).onclick = () => dlg.close(); $('.prev', dlg).onclick = () => show(i - 1); $('.next', dlg).onclick = () => show(i + 1);
    dlg.addEventListener('click', e => { if (e.target === dlg || e.target.classList.contains('frame')) dlg.close(); });
    dlg.addEventListener('keydown', e => { if (e.key === 'ArrowRight') show(i + 1); if (e.key === 'ArrowLeft') show(i - 1); });
    let sx = 0; dlg.addEventListener('touchstart', e => sx = e.touches[0].clientX, { passive: true });
    dlg.addEventListener('touchend', e => { const dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1)); });
  }

  // ---- layered app icon parallax -----------------------------------------
  $$('.app-icon').forEach(stage => {
    const coin = $('.coin', stage), glare = $('.glare', stage);
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    let tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
    const render = () => { raf = null; cx += (tx - cx) * .18; cy += (ty - cy) * .18;
      coin.style.transform = `rotateY(${cx * 26}deg) rotateX(${-cy * 26}deg)`;
      glare.style.setProperty('--gx', `${50 + cx * 40}%`); glare.style.setProperty('--gy', `${50 + cy * 40}%`);
      if (Math.abs(tx - cx) > .002 || Math.abs(ty - cy) > .002) raf = requestAnimationFrame(render); };
    const move = e => { const r = stage.getBoundingClientRect(); const p = e.touches ? e.touches[0] : e;
      tx = Math.max(-1, Math.min(1, (p.clientX - (r.left + r.width / 2)) / (r.width / 2)));
      ty = Math.max(-1, Math.min(1, (p.clientY - (r.top + r.height / 2)) / (r.height / 2)));
      if (!raf) raf = requestAnimationFrame(render); };
    const reset = () => { tx = ty = 0; if (!raf) raf = requestAnimationFrame(render); };
    window.addEventListener('pointermove', move, { passive: true }); stage.addEventListener('pointerleave', reset);
  });

  // ---- spatial capability hint --------------------------------------------
  const supportsModel = 'HTMLModelElement' in window;
  const supportsAR = (() => { try { return document.createElement('a').relList.supports('ar'); } catch { return false; } })();
  $$('.spatial-hint').forEach(h => {
    const mode = h.dataset.for || 'model';
    if ((mode === 'model' && supportsModel) || (mode === 'ar' && supportsAR) || (mode === 'any' && (supportsModel || supportsAR))) h.classList.add('show');
  });
  document.documentElement.dataset.spatial = supportsModel ? 'native' : supportsAR ? 'ar' : 'flat';

  // ---- current-year stamps -------------------------------------------------
  $$('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();
