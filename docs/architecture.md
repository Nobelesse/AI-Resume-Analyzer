# Phase 2 architecture

- `app/main.py`: Streamlit entry point and page registry.
- `app/pages/`: four render functions for home, interaction studio, roadmap and architecture.
- `app/ui/components.py`: HTML-escaped presentational component helpers.
- `app/ui/theme.py`, `app/assets/styles.css`: first-party CSS theme.
- `app/ui/motion.py`: isolated Streamlit HTML component renderer.
- `app/ui/web/motion.html`: first-party local HTML/CSS/JavaScript pointer tilt effect with reduced-motion and touch safeguards.
- `app/config.py`: upload and taxonomy targets (not implemented backend operations).

All metrics displayed in Phase 2 are configured project specifications, not production resume records. Phase 3 establishes SQLite and role-based authorization before any private data is accepted.
