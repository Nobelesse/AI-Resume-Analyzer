# Version 1.5.9.3 — Global Dark Abyss + Twinkling Stars

## Scope

Applied via `app/ui/theme.py` and `app/assets/styles.css` to every route registered in `app/main.py`, regardless of role (guest, user, admin). The starfield layers are CSS-only backgrounds using fixed pseudo-elements, with pointer events disabled. Sidebar includes its own subdued decorative stars. Original hero animation, forms, charts and navigation are retained.

## Accessibility and performance

Layered radial gradients use opacity animations, not JavaScript loops or canvas rendering. The `prefers-reduced-motion` media query disables twinkling. The effect is decorative and behind page content. Results depend on the browser and Streamlit version.

## Windows verification

1. Start the app: `python -m streamlit run app/main.py`.
2. Verify Overview, User Login, Admin Login, Registration.
3. Sign in as a user; inspect Dashboard, Upload, ATS Intelligence, Job Match, Career Finder and History.
4. Sign in as an admin; inspect Dashboard, Resume Management, Account Management, Audit and Skills Catalog.
5. Check clicking, scrolling, sidebar links, upload/download, popup dialogs, and keyboard focus.
6. Set Windows/Chrome to reduced-motion mode and verify the starfield becomes static.

Existing databases and skill data are not changed.
