# Version 1.5.9.9.9 — Premium hero motion and 3D globe

The Overview uses a same-document **transparent HTML canvas** with local JavaScript (`app/ui/web/premium_globe.js`). It draws a rotating perspective-projected sphere, light/dark near/far mesh geometry, nodes and two orbital rings. No external scripts, paid APIs, network requests or uploaded resume data are used by the visualization.

The existing scroll engine still tracks the real Streamlit scroll container. Hero kicker, heading, description, pills and globe now receive independent, upright depth movement. On smaller viewports or when reduced-motion is requested, scroll transformations are disabled. Continuous globe animation also stops for reduced-motion, hidden tabs and out-of-view canvases.

## Manual browser verification

1. In Windows VS Code, run `python -m streamlit run app/main.py` from the repository virtual environment.
2. Open Overview. Verify the globe appears without an opaque rectangle and rotates, with visible rear/near geometry.
3. Scroll gently toward Your Workspace, then reverse. Verify the heading and supporting text travel at different speeds while staying readable.
4. Check responsive width, user/admin login, sidebar scrolling, ATS and Job Studio controls.
5. In Chrome's accessibility setting, turn on reduced motion and verify all information remains visible.

Note: automated tests and a syntax check do **not** replace visual testing in the user's particular Chrome and Streamlit environment.

## Data safety

Deployment ZIP excludes `.git`, `.venv`, `.env`, local `data`, `datasets/ESCO`, `datasets/ONET`, `uploads`, backup databases, caches and uploaded resumes. Existing E: drive databases and user records must be preserved during installation.
