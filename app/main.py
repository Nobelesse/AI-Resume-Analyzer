"""AI-Resume-Analyzer Streamlit entry point (Phase 8 final).

Run from the project root:
    python -m streamlit run app/main.py
"""

from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import APP_NAME, APP_VERSION
from app.database.connection import initialize_database
from app.pages import architecture, auth_pages, design_lab, home, roadmap, secure_pages, resume_pages, analysis_pages, job_pages, management_pages
from app.ui.components import sidebar_identity
from app.ui.session import logout, session_user
from app.ui.theme import inject_theme
from app.ui.scroll_engine import inject_scroll_engine
from app.ui.navigation import ROUTE_LABELS


def render_user_login() -> None:
    """Dedicated Streamlit page function for standard account sign-in."""
    auth_pages.login("user")


def render_admin_login() -> None:
    """Dedicated Streamlit page function for administrator sign-in."""
    auth_pages.login("admin")


def main() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    initialize_database()
    inject_theme()
    inject_scroll_engine()
    current = session_user()

    with st.sidebar:
        sidebar_identity()
        st.caption("A private, explainable career intelligence system")
        st.divider()
        if current:
            st.caption(f"Signed in as {current['display_name']} · {current['role']}")
            # Keep the button at its natural width in the full sidebar.
            # A one-third-width Streamlit column clips "Sign out" as "Sign ...".
            with st.container(key="sidebar_signout_area"):
                if st.button("Sign out", key="sidebar_signout", use_container_width=False):
                    logout()
                    st.rerun()
        else:
            st.caption("Guest · Choose a dedicated login portal")

    workspace_pages = [
        st.Page(home.render, title="Overview", icon="🏠", url_path="home", default=True),
        st.Page(design_lab.render, title="Getting Started", icon="✨", url_path="interaction-studio"),
    ]

    if current is None:
        account_pages = [
            st.Page(render_user_login, title="User Login", icon="🔑", url_path="user-login"),
            st.Page(auth_pages.register, title="User Registration", icon="📝", url_path="user-register"),
            st.Page(render_admin_login, title="Admin Login", icon="🛡️", url_path="admin-login"),
        ]
    elif current["role"] == "admin":
        account_pages = [
            st.Page(secure_pages.admin_dashboard, title="Admin Dashboard", icon="🛡️", url_path="admin-dashboard"),
            st.Page(management_pages.admin_resume_management, title="Resume & CV Management", icon="📚", url_path="admin-resume-management"),
            st.Page(management_pages.account_management, title="Account Management", icon="👥", url_path="account-management"),
            st.Page(management_pages.audit_page, title="Activity Log", icon="📋", url_path="audit-log"),
            st.Page(management_pages.taxonomy_management, title="Skills Catalog", icon="📚", url_path="skills-catalog"),
        ]
    elif current["role"] == "user":
        account_pages = [
            st.Page(secure_pages.user_dashboard, title="User Dashboard", icon="👤", url_path="user-dashboard"),
            st.Page(management_pages.my_record_management, title="Manage My Records", icon="🗂️", url_path="manage-my-records"),
            st.Page(resume_pages.upload_resume, title="Upload Resume / CV", icon="📤", url_path="upload-resume"),
            st.Page(resume_pages.user_library, title="My Resumes", icon="📄", url_path="my-resumes"),
            st.Page(analysis_pages.advanced_ats_intelligence, title="Advanced ATS Intelligence", icon="🧠", url_path="resume-analysis"),
            st.Page(analysis_pages.analysis_history, title="Analysis History", icon="📊", url_path="analysis-history"),
            st.Page(job_pages.job_match, title="Job Match Studio", icon="🎯", url_path="job-match"),
            st.Page(job_pages.career_finder, title="AI Career Finder", icon="🧭", url_path="career-finder"),
            st.Page(job_pages.job_history, title="Job Match History", icon="📑", url_path="job-history"),
        ]
    else:
        # Unknown roles must never receive a privileged navigation entry.
        account_pages = []

    project_pages = [
        st.Page(roadmap.render, title="Platform Capabilities", icon="✨", url_path="build-roadmap"),
        st.Page(architecture.render, title="Privacy & Technology", icon="🔐", url_path="architecture"),
    ]

    pages = {"WORKSPACE": workspace_pages, "PLATFORM": project_pages}
    if account_pages:
        pages["ACCOUNT"] = account_pages

    all_pages = workspace_pages + account_pages + project_pages
    # The same page objects used by Streamlit navigation are used by click-to-open tiles.
    st.session_state["_ara_registered_pages"] = {
        page.url_path: page for page in all_pages
    }
    st.navigation(pages).run()

    with st.sidebar:
        st.divider()
        st.markdown(
            '<div class="sidebar-status"><span class="status-dot"></span>'
            " Local storage protected · System ready</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"v{APP_VERSION} · Python 3.11 · Streamlit")


if __name__ == "__main__":
    main()
