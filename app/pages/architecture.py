"""A truthful summary of implemented and upcoming components."""
import streamlit as st
from app.config import APP_VERSION


def render() -> None:
    st.title("System architecture")
    st.caption(f"Application version {APP_VERSION} · Foundation milestone")
    st.markdown("**Current execution path:** Browser → Streamlit → Python page functions → custom CSS.")
    st.markdown("**Planned data path:** Resume → file validation → parser → skill extraction → local SQLite → user-specific analysis.")
    st.markdown("**Planned administrator path:** Admin login → server-side permission checks → secured database queries.")
    st.warning("No production authentication, resume upload, or admin data access is available in Phase 1. These require the security milestones before real resumes should be used.")
