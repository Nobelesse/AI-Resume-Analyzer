"""Hands-on design controls for accessibility and interaction review."""
import streamlit as st
from app.ui.components import motion_demo, section_heading, feature_tile

def render() -> None:
    section_heading("PHASE 02 / INTERACTION STUDIO", "Visual interaction laboratory", "A safe design-only playground for reviewing effects before real workflows are added.")
    show_motion = st.toggle("Show interactive 3D preview", value=True, help="Disable the preview without changing browser settings.")
    if show_motion:
        motion_demo(360)
    else:
        st.info("Animated preview hidden. All navigation and content remain accessible.")
    st.subheader("Component gallery")
    c1, c2, c3 = st.columns(3)
    with c1: feature_tile("✦", "Soft-glow borders", "Cards use an accessible color contrast and gradual hover effects.", "LIVE UI")
    with c2: feature_tile("↗", "Responsive layout", "Columns stack automatically for narrow layouts.", "LIVE UI")
    with c3: feature_tile("☾", "Reduced motion", "Animation is disabled when the operating system requests it.", "LIVE UI")
    st.caption("The motion scene uses an isolated local HTML/JavaScript Streamlit component. It does not fetch remote data or read resumes.")
