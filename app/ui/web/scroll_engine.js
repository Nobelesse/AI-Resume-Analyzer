/* Celestial Spatial Engine 1.5.9.9.5 — first-party, main-document code only.
   No data access, external requests or Streamlit state changes. */
(() => {
  'use strict';
  const w = window;
  const d = document;
  if (w.__araScrollEngine159995) {
    w.__araScrollEngine159995.refresh();
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
      let transform;
      if (state.kind === 'orb') {
        transform = `perspective(1200px) translate3d(${(-offset * 22).toFixed(1)}px,${(offset * 24).toFixed(1)}px,0) rotateY(${(-offset * 10).toFixed(1)}deg) scale(${(1 - Math.abs(offset) * .055).toFixed(3)})`;
      } else if (state.kind === 'card') {
        transform = `perspective(1100px) translate3d(${(offset * 40 * state.direction).toFixed(1)}px,${(offset * 28).toFixed(1)}px,0) rotateY(${(offset * 9 * state.direction).toFixed(1)}deg) rotateX(${(-offset * 6).toFixed(1)}deg)`;
      } else {
        transform = `perspective(1050px) translate3d(${(offset * 17 * state.direction).toFixed(1)}px,${(offset * 30).toFixed(1)}px,0) rotateX(${(-offset * 15).toFixed(1)}deg) rotateY(${(offset * 7 * state.direction).toFixed(1)}deg)`;
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
  w.__araScrollEngine159995 = {refresh, version:'1.5.9.9.5'};
  refresh();
})();
