# UI 1.0 — Milestone 1: Design foundation

This integrated release starts the three-milestone UI 1.0 redesign. It is **not** the completion of all three milestones.

## Delivered
- Redesigned welcome dashboard with a CSS-only futuristic orb, depth layers, and reduced-motion support.
- Dedicated UI 1.0 visual tokens, consistent navigation styling and focused workspace cards.
- Real Streamlit button navigation preserving Python role checks; no HTML link bypasses authorization.
- Compact sidebar sign-out and auth controls preserved.
- All previous resume, database, AI, and administrative functionality retained.

## Coming in next UI milestones
Milestone 2: detailed redesign of login, resume upload, analysis, job matching and career-finder screens.
Milestone 3: administrative screens, motion/performance tuning, keyboard/accessibility and live browser testing.

## Run
`python -m streamlit run app/main.py` from the project root.

## Verify
`python -m pytest -q` and `python scripts/final_audit.py`.

This project does not use a separate Node.js / React application. Motion and visual depth are CSS-based in this milestone; navigation remains native Streamlit to preserve accessibility and server-side protection.
