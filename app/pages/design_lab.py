"""Optional interaction gallery: finished product design system."""
import streamlit as st
from app.ui.components import motion_demo, section_heading, metric_tile
from app.ui.navigation import navigation_card

def render() -> None:
    section_heading("DESIGN SYSTEM", "Motion and depth", "Experience the depth effects used throughout ResumeIntel. Interactive navigation tiles below open real pages.")
    show = st.toggle("Show perspective scene", value=True)
    if show: motion_demo(360)
    a,b,c = st.columns(3)
    with a: metric_tile("DEPTH", "3D", "Perspective and layered lighting", "violet")
    with b: metric_tile("ACCESSIBILITY", "On", "Respects reduced-motion settings", "cyan")
    with c: metric_tile("NAVIGATION", "Live", "Real Streamlit page controls", "green")
    navigation_card("Project Milestones", "Browse all completed project milestones", "build-roadmap", "◈")
