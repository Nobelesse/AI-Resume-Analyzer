# Version 1.5.9.6 — Seamless Hero & Cinematic Scroll

The overview hero iframe no longer draws a separate sky, dimming overlay, mask, or full-canvas glow. The original global Streamlit Dark Abyss starfield should show through behind the globe and copy. The animated 3D globe and orbit system remain intact.

Read-only headings and explanatory text have subtle scroll-linked perspective and fade effects in browsers supporting CSS view timelines, with an explicit reduced-motion fallback. No scroll listeners or Streamlit reruns are added. Forms, buttons and tables stay stationary.

Verify on Chrome using the Overview page: no square seam or change of sky shade at the hero edge, starfield visible through the entire hero, globe orbit renders, headings reveal on scroll, and both auth roles work. CSS/browser support can vary.
