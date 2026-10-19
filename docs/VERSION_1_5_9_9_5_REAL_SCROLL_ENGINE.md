# Version 1.5.9.9.5 — Real 3D Scroll Engine

## Why the previous animation was invisible
Older versions used `animation-timeline: view(block)` and narrowly selected Streamlit elements. Even when CSS was present, users could see no change if the scroll timeline did not activate or the target selectors were absent.

## Architecture
- Streamlit 1.65's `st.html(..., unsafe_allow_javascript=True)` executes **trusted first-party JavaScript inside the main page**. The code lives at `app/ui/web/scroll_engine.js` and is loaded on every page from `app/main.py`. It is **not** rendered inside an iframe.
- The engine listens for document scroll events in capture mode, including nested Streamlit scroll containers. It uses `requestAnimationFrame`, `getBoundingClientRect()` and CSS custom properties to animate selected **read-only** headings, feature tiles and the decorative hero globe.
- A `MutationObserver` refreshes targets when Streamlit replaces page elements after navigation/reruns. A versioned singleton avoids adding repeated listeners.
- Interactive controls, sidebar, forms, data tables, charts and links are deliberately excluded. No network calls or user data accesses are used.
- The engine respects `prefers-reduced-motion` and disables geometry effects on narrow screens. Layout and text remain fully visible when JavaScript is disabled.

## Verification procedure on user's Windows PC
1. Stop Streamlit, install the release while preserving `data/`, `datasets/`, `.venv`, `.git` and `.env`.
2. Start `python -m streamlit run app/main.py` from the project root, hard-refresh Chrome with Ctrl+Shift+R.
3. Scroll the **Overview** page slowly past **Your Workspace**. Headings should visibly rotate/shift, while the globe moves on its own depth path.
4. Scroll **Platform Capabilities** to verify read-only information moves laterally; check the sidebar scroll remains independent.
5. Check **User/Admin Login, ATS Intelligence, Job Studio**: no forms, buttons or charts may move or lose interactivity.
6. In Windows accessibility settings, enable Reduced Motion and verify the 3D motion stops.

This release has automated source tests, JavaScript syntax checks, and a small Chromium scroll harness. It has **not** been observed in the user's actual Windows Chrome; visual verification remains necessary.
