# Version 1.5.9.9.4 — Celestial Spatial Journey

This UI-only release replaces the v1.5.9.9.3 fade/blur motion system with geometric scroll movement: perspective heading rotations, static-card stacking, alternating horizontal movement on informational roadmap rows and subtle depth on the Overview hero. The global starfield and sidebar scroll correction stay unchanged.

Animations use Chrome-compatible CSS view timelines, are disabled on reduced-motion preference or narrow screens, and do not target forms, native controls, data grids or download buttons. Browser support varies; where unsupported, content is displayed normally. A true pinned horizontal scene was intentionally not added because the site's workflow and accessibility depend on standard vertical scrolling.

No databases, uploaded resumes or private credentials are included. Existing O*NET/ESCO imports are preserved during installation by excluding the `data` and `datasets` directories.
