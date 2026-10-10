"""Release history of completed university project milestones."""
import streamlit as st
from app.ui.components import section_heading

PHASES = [
    ("01", "Foundation", "Streamlit project, configuration and version control"),
    ("02", "Interactive experience", "Responsive interface, motion and accessibility"),
    ("03", "Authentication & database", "Admin/User permissions and local SQLite"),
    ("04", "Document processing", "2 MB PDF, DOCX, TXT, RTF and ODT uploads"),
    ("05", "Resume intelligence", "ATS-readiness review and skill extraction"),
    ("06", "Career matching", "Job matching, Ollama and Career Finder"),
    ("07", "Workspace dashboards", "Admin management, analytics and audit logs"),
    ("08", "Validation & release", "Regression tests, hardening and documentation"),
]

def render() -> None:
    section_heading("PROJECT MILESTONES", "Built, tested, and delivered.", "All eight planned development milestones have been completed. The application continues to evolve through UI and maintenance releases.")
    for number, title, description in PHASES:
        st.markdown(f'<div class="roadmap-row"><span class="phase-number">{number}</span><div><strong>{title}</strong><p>{description}</p></div><span class="phase-status phase-complete">✓ COMPLETED</span></div>', unsafe_allow_html=True)
