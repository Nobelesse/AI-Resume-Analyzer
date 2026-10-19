/* Cinematic Depth Scroll 1.5.9.9.9 — first-party, main-document code only.
   No data access, external requests or Streamlit state changes. */
(() => {
  'use strict';
  const w = window;
  const d = document;
  if (w.__araScrollEngine159999) {
    w.__araScrollEngine159999.refresh();
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
    '[data-testid="stMain"] .ara-native-kicker',
    '[data-testid="stMain"] .ara-native-copy h1',
    '[data-testid="stMain"] .ara-native-copy p',
    '[data-testid="stMain"] .ara-native-copy .ara-native-pills',
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
      if (!elState.has(el)) elState.set(el, {kind: el.matches('.feature-card,.metric-tile,.roadmap-row') ? 'card' : el.matches('.ara-native-orb-shell') ? 'orb' : el.matches('.ara-native-copy h1') ? 'hero-title' : el.matches('.ara-native-copy p') ? 'hero-description' : el.matches('.ara-native-kicker') ? 'hero-kicker' : el.matches('.ara-native-pills') ? 'hero-pills' : 'text', direction: 0});
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
      // Scroll-linked depth that is clearly visible while remaining typographically straight.
      // Compute progress from the untransformed layout rectangle so changes remain reversible.
      const center = r.top + r.height / 2;
      const entering = clamp((center - viewport * 0.45) / (viewport * 0.48), 0, 1);
      const settled = 1 - entering;
      const state = elState.get(el);
      if (!state) continue;
      let transform;
      if (state.kind === 'orb') {
        transform = `translate3d(0,${(entering * 46).toFixed(1)}px,${(-entering * 100).toFixed(1)}px) scale(${(1 - entering * 0.075).toFixed(3)})`;
      } else if (state.kind === 'hero-title') {
        transform = `translate3d(0,${(entering * 56).toFixed(1)}px,${(-entering * 105).toFixed(1)}px) scale(${(1 - entering * 0.095).toFixed(3)})`;
      } else if (state.kind === 'hero-description') {
        transform = `translate3d(0,${(entering * 35).toFixed(1)}px,${(-entering * 62).toFixed(1)}px) scale(${(1 - entering * 0.045).toFixed(3)})`;
      } else if (state.kind === 'hero-kicker') {
        transform = `translate3d(0,${(entering * 23).toFixed(1)}px,${(-entering * 32).toFixed(1)}px) scale(${(1 - entering * 0.025).toFixed(3)})`;
      } else if (state.kind === 'hero-pills') {
        transform = `translate3d(0,${(entering * 22).toFixed(1)}px,${(-entering * 40).toFixed(1)}px) scale(${(1 - entering * 0.02).toFixed(3)})`;
      } else if (state.kind === 'card') {
        transform = `translate3d(0,${(entering * 25).toFixed(1)}px,${(-entering * 55).toFixed(1)}px) scale(${(1 - entering * 0.035).toFixed(3)})`;
      } else {
        transform = `translate3d(0,${(entering * 34).toFixed(1)}px,${(-entering * 75).toFixed(1)}px) scale(${(1 - entering * 0.04).toFixed(3)})`;
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
  w.__araScrollEngine159999 = {refresh, version:'1.5.9.9.9'};
  refresh();
})();
