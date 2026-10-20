"""Release history of completed university project milestones."""
import streamlit as st
from app.ui.components import section_heading

PHASES = [
    ("01", "Foundation", "Streamlit project, configuration and version control"),
    ("02", "Interactive experience", "Responsive interface, motion and accessibility"),
    ("03", "Authentication & database", "Admin/User permissions and local SQLite"),
    ("04", "Document processing", "Resume (2 MB) and CV (10 MB) PDF, DOCX, TXT, RTF and ODT uploads"),
    ("05", "Resume intelligence", "ATS-readiness review and skill extraction"),
    ("06", "Career matching", "Evidence-ranked career matching and Career Finder"),
    ("07", "Workspace dashboards", "Admin management, analytics and audit logs"),
    ("08", "Validation & release", "Regression tests, hardening and documentation"),
]

def render() -> None:
    section_heading("PLATFORM CAPABILITIES", "From resume to next opportunity.", "Explore the features available in the secure career intelligence workspace.")
    for number, title, description in PHASES:
        st.markdown(f'<div class="roadmap-row"><span class="phase-number">{number}</span><div><strong>{title}</strong><p>{description}</p></div><span class="phase-status phase-complete">✦ AVAILABLE</span></div>', unsafe_allow_html=True)
