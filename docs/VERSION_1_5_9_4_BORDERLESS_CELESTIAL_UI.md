# 1.5.9.4 — Borderless Celestial Workspace

This is a global **presentation-only** refinement to Version 1.5.9.3. All 21 routes share the existing stylesheet loader.

- Informational cards, large headers, hero frames, login containers, and metric tiles are borderless and transparent so the existing global twinkling stars remain visible.
- Floating headline typography uses multi-layer CSS shadows; it does not cause Streamlit reruns.
- Editable inputs, dense tables, upload drop zones and alerts retain subtle dark tint for contrast and usability.
- Focus outlines and reduced-motion support remain enabled.
- Embedded HTML hero has a semi-transparent scene; no dependency on external graphics.
- Python services, scoring, authentication, SQLite schema, O*NET data and reports are unchanged.

Browser verification recommended in Chrome: guest, user, admin, ATS, Job Studio, Career Finder; keyboard tab focus; mobile viewport.

## Scroll-reactive depth
- Native CSS scroll-driven view timelines subtly translate and tilt decorative headings and information tiles as they enter and leave the viewport.
- No JavaScript scroll listeners, external dependencies, Streamlit reruns, or changes to form controls.
- Unsupported browsers show the normal static design; narrow layouts and reduced-motion settings disable the scroll treatment.
- Verify in Chrome with a long dashboard and scrolling in both directions. Confirm that inputs and PDF/CSV download controls remain usable.
