"""Accurate Phase 2 architecture description."""
import streamlit as st
from app.config import APP_VERSION
from app.ui.components import section_heading

def render() -> None:
    section_heading("SYSTEM BLUEPRINT", "Architecture at a glance", f"Version {APP_VERSION} · Streamlit visual layer implemented")
    st.markdown("""**Implemented now:** Browser → Streamlit pages → Python presentation helpers → CSS theme and an isolated first-party HTML/JavaScript motion component.

**Next:** Admin/User authentication → server-side role permissions → SQLite models and repositories.

**Later:** Validated resume upload → multi-format parsing → skills taxonomy with aliases → explainable analysis → job matching → protected reporting.
""")
    st.warning("Do not upload real resumes or assume account protection yet. There is no live upload, user database, or authentication in Phase 2.")
