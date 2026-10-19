/* Cinematic 3D Typography 1.5.9.9.6 — first-party, main-document code only.
   No data access, external requests or Streamlit state changes. */
(() => {
  'use strict';
  const w = window;
  const d = document;
  if (w.__araScrollEngine159996) {
    w.__araScrollEngine159996.refresh();
    return;
  }

  const selector = [
    '[data-testid="stMain"] .section-heading',
    '[data-testid="stMain"] .eyebrow',
    '[data-testid="stMain"] .section-copy',
    '[data-testid="stMain"] [data-testid="stHeading"] h1',
    '[data-testid="stMain"] [data-testid="stHeading"] h2',
    '[data-testid="stMain"] [data-testid="stHeading"] h3',
    '[data-testid="stMain"] .feature-card',
    '[data-testid="stMain"] .metric-tile',
    '[data-testid="stMain"] .roadmap-row',
    '[data-testid="stMain"] .ara-native-copy',
    '[data-testid="stMain"] .ara-native-orb-shell'
  ].join(',');
  const media = w.matchMedia('(prefers-reduced-motion: reduce)');
  const elState = new WeakMap();
  let items = [];
  let raf = 0;
  let observer = null;
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

  function isSafe(el) {
    // Never animate interactive widgets or sidebar navigation.
    return !el.closest('[data-testid="stSidebar"], button, [role="button"], form, [data-testid="stForm"], [data-testid="stDataFrame"], [data-testid="stTable"], [data-testid="stMetric"], [data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"], input, textarea, select, a, [contenteditable="true"]');
  }
  function refresh() {
    const main = d.querySelector('[data-testid="stMain"]');
    if (!main) return;
    const discovered = [...main.querySelectorAll(selector)].filter(isSafe);
    const active = new Set(discovered);
    for (const old of items) {
      if (!active.has(old)) {
        old.classList.remove('ara-scroll-live');
        old.style.removeProperty('--ara-scroll-transform');
      }
    }
    items = discovered;
    items.forEach((el, index) => {
      el.classList.add('ara-scroll-live');
      if (!elState.has(el)) elState.set(el, {kind: el.matches('.feature-card,.metric-tile,.roadmap-row') ? 'card' : el.matches('.ara-native-orb-shell') ? 'orb' : 'text', direction: index % 2 ? 1 : -1});
    });
    schedule();
  }
  function render() {
    raf = 0;
    const disabled = media.matches || w.innerWidth <= 800;
    const viewport = w.innerHeight || d.documentElement.clientHeight;
    for (const el of items) {
      if (!el.isConnected) continue;
      if (disabled) {
        el.style.removeProperty('--ara-scroll-transform');
        continue;
      }
      const r = el.getBoundingClientRect();
      // Travel is visible both entering and leaving the viewport, without hiding text.
      const fromCenter = (r.top + r.height / 2 - viewport * 0.51) / Math.max(1, viewport * 0.55);
      const offset = clamp(fromCenter, -1, 1);
      const state = elState.get(el);
      if (!state) continue;
      // Scroll-relative motion: no hard spins, opacity changes, or blur.
      // Clamp to keep titles readable even at the beginning and end of a page.
      const proximity = Math.min(1, Math.abs(offset));
      const eased = Math.sign(offset) * proximity * proximity * (3 - 2 * proximity);
      let transform;
      if (state.kind === 'orb') {
        // A slow floating visual anchor, independent of the typography.
        transform = `perspective(1400px) translate3d(${(-eased * 18).toFixed(1)}px,${(eased * 29).toFixed(1)}px,0) scale(${(1 - proximity * .035).toFixed(3)})`;
      } else if (state.kind === 'card') {
        // Magnetic card rise: slight diagonal drift and depth; no tilt stacking.
        transform = `perspective(1350px) translate3d(${(eased * 21 * state.direction).toFixed(1)}px,${(eased * 29).toFixed(1)}px,0) scale(${(1 - proximity * .045).toFixed(3)})`;
      } else {
        // Alternating heading directions create a split-line editorial rhythm.
        // The heading zooms gently from depth without rotation, so it remains readable.
        const x = eased * 48 * state.direction;
        const y = eased * 28;
        const scale = 1 - proximity * .075;
        transform = `perspective(1400px) translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0) scale(${scale.toFixed(3)})`;
      }
      el.style.setProperty('--ara-scroll-transform', transform);
    }
  }
  function schedule() {
    if (!raf) raf = w.requestAnimationFrame(render);
  }
  let refreshPending = false;
  function onMutations() {
    if (refreshPending) return;
    refreshPending = true;
    w.requestAnimationFrame(() => { refreshPending = false; refresh(); });
  }
  // Capture scrolling from Streamlit's nested page containers as well as window.
  d.addEventListener('scroll', schedule, {capture:true, passive:true});
  w.addEventListener('scroll', schedule, {passive:true});
  w.addEventListener('resize', schedule, {passive:true});
  if (media.addEventListener) media.addEventListener('change', schedule);
  observer = new MutationObserver(onMutations);
  const main = d.querySelector('[data-testid="stMain"]');
  if (main) observer.observe(main, {childList:true,subtree:true});
  w.__araScrollEngine159996 = {refresh, version:'1.5.9.9.6'};
  refresh();
})();
