"""First-party main-document scroll motion for Streamlit 1.65+.

No uploaded resume, user input or external URL is passed to this JavaScript.
It only reads element geometry and updates presentation-only CSS variables.
"""
from pathlib import Path
import streamlit as st

GLOBE_SCRIPT_PATH = Path(__file__).resolve().parent / "web" / "premium_globe.js"
SCRIPT_PATH = Path(__file__).resolve().parent / "web" / "scroll_engine.js"


def inject_scroll_engine() -> None:
    """Run the trusted scroll observer in the main document, not an iframe."""
    script = SCRIPT_PATH.read_text(encoding="utf-8") + "\n" + GLOBE_SCRIPT_PATH.read_text(encoding="utf-8")
    st.html("<script>\n" + script + "\n</script>", unsafe_allow_javascript=True)
