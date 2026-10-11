# Version 1.4.1.1 — Sign out button layout correction

The previous sign-out button was placed inside a one-third-width Streamlit sidebar column, causing its label to collapse to "Sign ...". This update removes the narrow column and places the native Streamlit sign-out button inside a centered, full-width keyed container. Scoped CSS gives it a compact minimum width and preserves the full label. No changes to logout logic or database.

## Verification

Run `python -m pytest -q` and `python scripts/final_audit.py`. Check that the full **Sign out** label is visible and centered in the sidebar at different browser zoom levels.
