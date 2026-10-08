"""AI-Resume-Analyzer Streamlit entry point (Phase 3 navigation fix).

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
from app.pages import architecture, auth_pages, design_lab, home, roadmap, secure_pages, resume_pages
from app.ui.components import sidebar_identity
from app.ui.session import logout, session_user
from app.ui.theme import inject_theme


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
    current = session_user()

    with st.sidebar:
        sidebar_identity()
        st.caption("A private, explainable career intelligence system")
        st.divider()
        if current:
            st.success(f"Signed in: {current['display_name']} ({current['role']})")
            if st.button("Sign out", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.caption("Guest · Choose a dedicated login portal")

    workspace_pages = [
        st.Page(home.render, title="Command Center", icon="🏠", url_path="home", default=True),
        st.Page(design_lab.render, title="Interaction Studio", icon="✨", url_path="interaction-studio"),
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
            st.Page(resume_pages.admin_library, title="All Resumes", icon="📚", url_path="admin-resumes"),
        ]
    elif current["role"] == "user":
        account_pages = [
            st.Page(secure_pages.user_dashboard, title="User Dashboard", icon="👤", url_path="user-dashboard"),
            st.Page(resume_pages.upload_resume, title="Upload Resume", icon="📤", url_path="upload-resume"),
            st.Page(resume_pages.user_library, title="My Resumes", icon="📄", url_path="my-resumes"),
        ]
    else:
        # Unknown roles must never receive a privileged navigation entry.
        account_pages = []

    project_pages = [
        st.Page(roadmap.render, title="Build Roadmap", icon="🗺️", url_path="build-roadmap"),
        st.Page(architecture.render, title="Architecture", icon="🧩", url_path="architecture"),
    ]

    pages = {"WORKSPACE": workspace_pages, "PROJECT": project_pages}
    if account_pages:
        pages["ACCOUNT"] = account_pages

    st.navigation(pages).run()

    with st.sidebar:
        st.divider()
        st.markdown(
            '<div class="sidebar-status"><span class="status-dot"></span>'
            " SQLite & authentication · Phase 04</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"v{APP_VERSION} · Python 3.11 · Streamlit")


if __name__ == "__main__":
    main()
