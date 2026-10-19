/* Premium Cinematic UI 1.5.9.9.7 — first-party, main-document code only.
   No data access, external requests or Streamlit state changes. */
(() => {
  'use strict';
  const w = window;
  const d = document;
  if (w.__araScrollEngine159997) {
    w.__araScrollEngine159997.refresh();
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
      if (!elState.has(el)) elState.set(el, {kind: el.matches('.feature-card,.metric-tile,.roadmap-row') ? 'card' : el.matches('.ara-native-orb-shell') ? 'orb' : 'text', direction: 0});
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
      // Premium restraint: preserve the text baseline and legibility.
      // The heading settles once into view; no lateral or rotary motion.
      const center = r.top + r.height / 2;
      const entering = clamp((center - viewport * 0.52) / (viewport * 0.44), 0, 1);
      const settled = 1 - entering;
      const state = elState.get(el);
      if (!state) continue;
      let transform;
      if (state.kind === 'orb') {
        // Very gentle hero depth, no rotational scrolling.
        transform = `translate3d(0,${(entering * 8).toFixed(1)}px,0)`;
      } else if (state.kind === 'card') {
        transform = `translate3d(0,${(entering * 6).toFixed(1)}px,0)`;
      } else {
        transform = `translate3d(0,${(entering * 7).toFixed(1)}px,0)`;
      }
      el.style.setProperty('--ara-spotlight-progress', settled.toFixed(3));
      if (settled >= 0.5) el.classList.add('ara-polished-visible');
      else el.classList.remove('ara-polished-visible');
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
  w.__araScrollEngine159997 = {refresh, version:'1.5.9.9.7'};
  refresh();
})();
