"""Project roadmap display."""
import streamlit as st

PHASES = [
    ("01", "Foundation", "Active: environment, Streamlit shell, theme and Git tooling"),
    ("02", "Interactive interface", "Polished UI components and cursor-reactive effects"),
    ("03", "Security and database", "Separate logins, role checks and local SQLite"),
    ("04", "Resume parser", "2 MiB validation and safe five-format extraction"),
    ("05", "Skills and analysis", "Expandable 10,000+ skills catalog and explainable ATS readiness"),
    ("06", "Job matching", "Skill gaps, job alignment and PDF reports"),
    ("07", "Dashboards", "Private histories and secured admin analytics"),
    ("08", "Testing and release", "Automated tests, security review and documentation"),
]


def render() -> None:
    st.title("Development roadmap")
    st.caption("The eight milestones planned for the university project")
    for number, title, description in PHASES:
        with st.container(border=True):
            st.markdown(f"**Phase {number} — {title}**")
            st.write(description)
