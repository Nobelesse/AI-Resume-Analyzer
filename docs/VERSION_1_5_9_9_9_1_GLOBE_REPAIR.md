# Version 1.5.9.9.9.1 — Globe Visibility Repair

Fixes a blank Overview hero globe caused by relying on JavaScript Canvas without a visible fallback. The previous animated inline SVG is now rendered immediately underneath the Canvas. The Canvas remains transparent and takes over only after its first successful draw. On blocked/unavailable JavaScript, the SVG remains visible. No iframe, external scripts, datasets or database changes.

Run `python -m pytest -q` and `python scripts/final_audit.py`. Verify Overview in Chrome, with and without reduced-motion preference.
