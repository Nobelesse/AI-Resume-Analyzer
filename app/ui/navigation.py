"""Safe in-app navigation to pages registered in the active Streamlit session."""
import streamlit as st

ROUTE_LABELS = {
    "upload-resume": "Upload Resume",
    "my-resumes": "My Resumes",
    "resume-analysis": "AI Resume Analysis",
    "analysis-history": "Analysis History",
    "job-match": "Job Match Studio",
    "career-finder": "AI Career Finder",
    "job-history": "Job Match History",
    "user-dashboard": "User Dashboard",
    "admin-dashboard": "Admin Dashboard",
    "admin-resume-management": "Resume Management",
    "account-management": "Account Management",
    "audit-log": "Activity Log",
    "architecture": "Architecture",
    "build-roadmap": "Project Milestones",
    "interaction-studio": "Interaction Studio",
}

def navigate(route: str) -> None:
    pages = st.session_state.get("_ara_registered_pages", {})
    if route not in pages:
        st.error("That workspace is unavailable for your account.")
        return
    st.switch_page(pages[route])

def navigation_card(title: str, description: str, route: str, icon: str = "✦") -> None:
    """Real navigation button, not a decorative HTML card."""
    if st.button(f"{icon}  {title}  ↗\n\n{description}", key=f"nav_card_{route}", use_container_width=True, type="secondary"):
        navigate(route)
