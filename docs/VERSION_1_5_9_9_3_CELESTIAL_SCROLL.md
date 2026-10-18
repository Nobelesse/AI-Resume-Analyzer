# Version 1.5.9.9.3 — Celestial Scroll Experience

UI-only release. Preserves all backend features, SQLite database, account controls and O*NET/ESCO data.

## Effects

- Global scroll-linked headline reveal (depth, modest tilt, blur to focus).
- Read-only overview cards rise into focus; scroll exit softens depth.
- Native Overview hero has a subtle scroll-linked scale and offset. The animated SVG globe stays present.
- Applies from the shared app stylesheet to guest, user and admin pages.
- Uses CSS `animation-timeline: view(block)`, without JavaScript scroll listeners or Streamlit reruns.
- On browsers without support, content stays statically visible. Reduced-motion disables these effects.
- Forms, buttons, reports, tables and sidebar are not intentionally animated.

## Browser validation

Check Chrome with browser zoom 100%: Overview, user/admin dashboard, Resume Library, ATS and Career Finder. Scroll slowly and quickly, verify inputs and sidebar work. CSS view timelines rely on browser support and must be inspected on the user's PC.
