"""Roadmap with truthful milestone statuses."""
import streamlit as st
from app.ui.components import section_heading
PHASES = [
    ("01", "Foundation", "COMPLETE", "Streamlit shell, packaging and configuration"),
    ("02", "Interactive interface", "CURRENT", "Command center, responsive components and isolated pointer-reactive 3D preview"),
    ("03", "Security and database", "NEXT", "Admin/User logins, permissions and SQLite persistence"),
    ("04", "Resume parser", "PLANNED", "2 MiB validation, safe multi-format parsing and storage"),
    ("05", "Skills and analysis", "PLANNED", "10,000+ skills taxonomy, normalization, skill extraction and ATS review"),
    ("06", "Job matching", "PLANNED", "Match explanations, missing skills and downloadable reports"),
    ("07", "Dashboards", "PLANNED", "Private histories and admin insights"),
    ("08", "Testing and release", "PLANNED", "Security checks, final polish and university documentation"),
]
def render() -> None:
    section_heading("PROJECT EXECUTION", "Eight-phase delivery plan", "Two visual foundation milestones are packaged; backend capabilities are upcoming.")
    for number, title, status, description in PHASES:
        st.markdown(f'<div class="roadmap-row"><span class="phase-number">{number}</span><div><strong>{title}</strong><p>{description}</p></div><span class="phase-status">{status}</span></div>',unsafe_allow_html=True)
