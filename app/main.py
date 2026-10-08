
"""Streamlit entry point: run with python -m streamlit run app/main.py."""

from pathlib import Path
import sys
import streamlit as st

# Allow running Streamlit from the project root on Windows.
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import APP_NAME, APP_VERSION  # noqa: E402
from app.pages import architecture, home, roadmap  # noqa: E402
from app.ui.theme import inject_theme  # noqa: E402


# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply existing custom UI theme
inject_theme()


# Sidebar branding
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">✦ RESUME<span>INTEL</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("AI Resume Analyzer")
    st.divider()


# Define pages with unique URL paths
overview_page = st.Page(
    home.render,
    title="Overview",
    icon="🏠",
    url_path="overview",
    default=True,
)

roadmap_page = st.Page(
    roadmap.render,
    title="Roadmap",
    icon="🗺️",
    url_path="roadmap",
)

architecture_page = st.Page(
    architecture.render,
    title="Architecture",
    icon="🧩",
    url_path="architecture",
)


# Streamlit navigation
navigation = st.navigation(
    {
        "Explore": [
            overview_page,
            roadmap_page,
            architecture_page,
        ]
    }
)

# Execute selected page
navigation.run()


# Sidebar footer
with st.sidebar:
    st.divider()
    st.caption(f"Version {APP_VERSION} · Phase 1 / 8")
    st.caption("Python 3.11 · Streamlit · Local-first")
