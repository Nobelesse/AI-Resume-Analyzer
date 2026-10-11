# UI 1.1 — Immersive motion

Integrated with UI 1.0 Milestone 3. All Streamlit backend, permissions, resume storage, Ollama workflows and routes remain unchanged.

- Revolving orbital hero with three rings, planet shading, twinkling starfield and a glowing satellite.
- Experience Center replaces the redundant design-demo copy with a genuine product tour and authenticated tool shortcuts.
- Reusable page-wide depth styles for metric panels, input focus, analysis sections and forms.
- Pointer-responsive spotlight and perspective inside the isolated Experience Center component.
- No JavaScript injection into Streamlit's parent window: other pages use performant CSS interaction, not cross-iframe cursor tracking.
- Reduced-motion preference stops orb animation, surface movement and interactive spotlight effects.
- CSS effects require no new Python dependencies and are intended for modest machines.

## QA
Run `python -m pytest -q`, `python scripts/final_audit.py`, and `python -m streamlit run app/main.py` from the project root. Visually check Firefox/Chrome and reduced-motion settings.
