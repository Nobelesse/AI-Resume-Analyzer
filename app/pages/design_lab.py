"""Accessible product experience: interactive scene and genuine workspace navigation."""
import streamlit as st
from app.ui.components import motion_demo, section_heading
from app.ui.navigation import navigation_card
from app.ui.session import session_user

def render() -> None:
    section_heading("PRODUCT EXPERIENCE", "Explore the interface", "An interactive illustration of our local AI workspace, plus shortcuts to real tools.")
    st.caption("Move your pointer in the scene to alter its perspective and spotlight. Animations are decorative and respect reduced-motion preferences.")
    motion_demo(380)
    st.markdown("### Explore real workflows")
    actor = session_user()
    if not actor:
        st.info("Sign in using the sidebar to open private resume tools. This visual scene needs no account.")
    elif actor.get("role") == "admin":
        cols=st.columns(2)
        with cols[0]: navigation_card("Admin Dashboard", "Live application statistics", "admin-dashboard", "◈")
        with cols[1]: navigation_card("Resume Management", "Review saved resumes", "admin-resume-management", "▤")
    else:
        cols=st.columns(2)
        with cols[0]: navigation_card("Resume Analysis", "Review your skills", "resume-analysis", "✦")
        with cols[1]: navigation_card("AI Career Finder", "Explore suitable occupations", "career-finder", "✧")
