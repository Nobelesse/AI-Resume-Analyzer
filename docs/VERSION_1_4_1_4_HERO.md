# Version 1.4.1.4 — Full Sphere / Cinematic Depth

Focused visual-only upgrade from Version 1.4.1.3. The camera now sizes the sphere according to space available on **each side** of its center, including perspective projection and ring safety margins. Rotation is smoothed with cursor motion. Multi-layer core/rim lighting, moving beam and twinkling nodes enhance depth. Animation pauses when tab hidden and respects reduced-motion preferences. No database or taxonomy migration; keep existing `data/` folder.

## Windows
Stop Streamlit. Back up the project, copy `app/ui/web/intelligence_hero.html`, `app/config.py`, and new tests/documentation, then run `python -m pytest -q` and `python -m streamlit run app/main.py`.
