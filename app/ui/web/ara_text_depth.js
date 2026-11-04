/* AI Resume Analyzer — Cinematic Typography v2 (no dependencies, no data access). */
(() => {
  const KEY = '__araCinematicTypographyV2';
  if (window[KEY]?.refresh) { window[KEY].refresh(); return; }
  // Retire the previous observer on Streamlit hot-reloads so animations don't stack.
  const old = window.__araTextDepthV1;
  try { old?.observer?.disconnect(); old?.mutation?.disconnect(); } catch (_) {}
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const state = { observer: null, mutation: null, refresh: null, destroy: null };
  window[KEY] = state;
  const mainSel = '[data-testid="stMainBlockContainer"]';
  const ignoreSel = '[data-testid="stSidebar"], [data-testid="stExpander"], details, summary, [data-testid="stForm"], [data-testid="stDataFrame"], [data-testid="stTable"], [data-testid="stMetric"], [data-testid="stAlert"], [data-testid="stChatMessage"], [data-testid="stDialog"], [data-testid="stPopover"], [role="alert"], [role="dialog"], [contenteditable="true"], button, a, label, pre, code, input, textarea, select, table, canvas, svg';
  const tracked = new WeakSet();
  const visible = new Set();
  const timers = new WeakMap();
  let scheduled = false, motionFrame = false;

  // A page-local preference control via browser console (no storage or network).
  // window.araTypographyIntensity('balanced' | 'cinematic' | 'off')
  const preference = window.__araTypeIntensity || 'cinematic';
  function setIntensity(mode) {
    if (!['balanced', 'cinematic', 'off'].includes(mode)) return;
    window.__araTypeIntensity = mode;
    document.documentElement.dataset.araTypeIntensity = mode;
    if (mode === 'off') {
      state.observer?.disconnect(); visible.clear();
      document.querySelectorAll('.ara-cine-heading, .ara-cine-subtext, .ara-cine-kicker').forEach(el => {
        el.classList.remove('ara-cine-enter', 'ara-cine-settled', 'ara-cine-lit');
        el.style.removeProperty('--ara-cine-scroll-y'); el.style.removeProperty('--ara-cine-scroll-z');
        el.style.removeProperty('--ara-cine-scroll-rx'); el.style.removeProperty('--ara-cine-scroll-ry');
      });
    } else {
      scan(true);
    }
  }
  window.araTypographyIntensity = setIntensity;
  document.documentElement.dataset.araTypeIntensity = preference;
  if (!('IntersectionObserver' in window) || !('MutationObserver' in window)) return;

  function eligible(el, kind) {
    if (!el.isConnected || el.closest(ignoreSel)) return false;
    // Expander headers must never be animated: transforms can make labels flicker.
    if (el.closest('[data-testid="stExpander"], details, summary, [aria-expanded="true"], [aria-expanded="false"]')) return false;
    const body = (el.textContent || '').trim();
    if (!body || body.length > (kind === 'heading' ? 130 : kind === 'kicker' ? 92 : 165)) return false;
    if (kind === 'subtext' && body.length < 20) return false;
    if (el.querySelector('button, a, input, textarea, select, pre, code, table')) return false;
    if (el.closest('[data-testid="stSidebar"]')) return false;
    // Skip long enumerations, one-line results, charts and score text.
    if (kind !== 'heading' && /(?:\s[·•]\s.*){3,}/.test(body)) return false;
    if (kind !== 'heading' && /^\d+\s*\/\s*\d+/.test(body)) return false;
    if (kind === 'subtext' && /(?:skills matched|skills to improve)/i.test(body)) return false;
    return true;
  }

  function replay(el) {
    if (reduce.matches || window.__araTypeIntensity === 'off') return;
    clearTimeout(timers.get(el));
    el.classList.remove('ara-cine-enter', 'ara-cine-settled', 'ara-cine-lit');
    // Reflow is deliberate, limited to a few visible headings, not an entire page.
    void el.offsetWidth;
    const kind = el.classList.contains('ara-cine-heading') ? 'heading' :
                 el.classList.contains('ara-cine-kicker') ? 'kicker' : 'subtext';
    const ms = kind === 'heading' ? 1080 : kind === 'kicker' ? 780 : 860;
    el.classList.add('ara-cine-enter');
    if (kind === 'heading') el.classList.add('ara-cine-lit');
    timers.set(el, setTimeout(() => {
      if (!el.isConnected) return;
      el.classList.remove('ara-cine-enter', 'ara-cine-lit');
      el.classList.add('ara-cine-settled');
    }, window.__araTypeIntensity === 'balanced' ? Math.round(ms * .75) : ms + 35));
  }

  state.observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      const el = entry.target;
      if (!el.isConnected) { visible.delete(el); state.observer.unobserve(el); continue; }
      if (entry.isIntersecting) {
        if (!visible.has(el)) { visible.add(el); replay(el); }
      } else {
        visible.delete(el);
        clearTimeout(timers.get(el));
        el.classList.remove('ara-cine-enter', 'ara-cine-lit', 'ara-cine-settled');
        el.style.removeProperty('--ara-cine-scroll-y');
        el.style.removeProperty('--ara-cine-scroll-z');
        el.style.removeProperty('--ara-cine-scroll-rx');
        el.style.removeProperty('--ara-cine-scroll-ry');
      }
    }
    updateMotion();
  }, { threshold: .13, rootMargin: '0px 0px -5% 0px' });

  function scan(reobserve = false) {
    scheduled = false;
    if (reduce.matches || window.__araTypeIntensity === 'off') return;
    const root = document.querySelector(mainSel);
    if (!root) return;
    const groups = [
      ['h1, h2, h3', 'heading', 'ara-cine-heading'],
      ['p', 'subtext', 'ara-cine-subtext'],
      ['[data-testid="stCaptionContainer"]', 'kicker', 'ara-cine-kicker']
    ];
    for (const [selector, kind, klass] of groups) {
      for (const el of root.querySelectorAll(selector)) {
        if (!eligible(el, kind)) continue;
        if (!tracked.has(el)) {
          tracked.add(el); el.classList.add(klass);
          state.observer.observe(el);
        } else if (reobserve) state.observer.observe(el);
      }
    }
  }

  function updateMotion() {
    if (motionFrame) return;
    motionFrame = true;
    requestAnimationFrame(() => {
      motionFrame = false;
      if (reduce.matches || window.__araTypeIntensity === 'off') return;
      const height = Math.max(1, window.innerHeight);
      for (const el of visible) {
        if (!el.isConnected) { visible.delete(el); continue; }
        const rect = el.getBoundingClientRect();
        const normalized = Math.max(-1, Math.min(1, (rect.top + rect.height * .5 - height / 2) / (height / 2)));
        const mode = window.__araTypeIntensity === 'balanced' ? .48 : 1;
        const heading = el.classList.contains('ara-cine-heading');
        const shift = (-normalized * (heading ? 10 : 5) * mode).toFixed(2);
        el.style.setProperty('--ara-cine-scroll-y', shift + 'px');
        if (heading) {
          el.style.setProperty('--ara-cine-scroll-z', ((1 - Math.abs(normalized)) * 20 * mode).toFixed(2) + 'px');
          el.style.setProperty('--ara-cine-scroll-rx', (normalized * -2.7 * mode).toFixed(2) + 'deg');
          el.style.setProperty('--ara-cine-scroll-ry', (normalized * 1.3 * mode).toFixed(2) + 'deg');
        }
      }
    });
  }
  function schedule() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(scan);
  }
  state.refresh = schedule;
  state.mutation = new MutationObserver(schedule);
  state.mutation.observe(document.body, { childList: true, subtree: true });
  document.addEventListener('scroll', updateMotion, { passive: true, capture: true });
  window.addEventListener('resize', updateMotion, { passive: true });
  reduce.addEventListener?.('change', () => {
    if (reduce.matches) {
      state.observer.disconnect(); visible.clear();
      document.querySelectorAll('.ara-cine-heading, .ara-cine-subtext, .ara-cine-kicker').forEach(el => {
        el.classList.remove('ara-cine-enter', 'ara-cine-settled', 'ara-cine-lit');
        el.style.removeProperty('--ara-cine-scroll-y');
      });
    } else scan(true);
  });
  state.destroy = () => {
    state.observer.disconnect(); state.mutation.disconnect();
    document.removeEventListener('scroll', updateMotion, true);
    window.removeEventListener('resize', updateMotion);
  };
  schedule();
})();
