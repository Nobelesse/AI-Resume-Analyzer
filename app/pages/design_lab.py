"""Experience Center: interactive scene and genuine workspace navigation."""
import streamlit as st
from app.ui.components import intelligence_sphere, section_heading
from app.ui.navigation import navigation_card
from app.ui.session import session_user


def render() -> None:
    section_heading(
        "EXPERIENCE CENTER",
        "Interactive intelligence scene",
        "A live 3D-style illustration of the platform's AI core, plus shortcuts to real workspace tools.",
    )
    st.caption(
        "Move your pointer across the scene to shift the perspective and light. Animations are decorative and respect reduced-motion preferences."
    )
    intelligence_sphere(430)

    st.markdown("### Explore real workflows")
    actor = session_user()
    if not actor:
        st.info("Sign in using the sidebar to open private resume tools. The interactive scene itself is public.")
    elif actor.get("role") == "admin":
        cols = st.columns(2)
        with cols[0]:
            navigation_card("Admin Dashboard", "Live application statistics", "admin-dashboard", "◈")
        with cols[1]:
            navigation_card("Resume Management", "Review saved resumes", "admin-resume-management", "▤")
    else:
        cols = st.columns(2)
        with cols[0]:
            navigation_card("Resume Analysis", "Review your skills", "resume-analysis", "✦")
        with cols[1]:
            navigation_card("AI Career Finder", "Explore suitable occupations", "career-finder", "✧")
