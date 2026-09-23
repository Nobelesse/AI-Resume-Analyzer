import streamlit as st

from ui.dashboard import render_dashboard
from ui.styles import load_custom_css


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="ResumeAI | AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------------

load_custom_css()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown("## 📄 ResumeAI")

    st.caption(
        "AI Resume & Job Match Analyzer"
    )

    st.divider()

    st.markdown("### Navigation")

    st.radio(
        "Go to",
        [
            "🏠 Dashboard",
            "📊 Analysis",
            "💡 Recommendations",
        ],
        index=0,
    )

    st.divider()

    st.markdown("### Project")

    st.caption(
        "MCA (AIML) Minor Project"
    )

    st.caption(
        "Oriental University, Indore"
    )

    st.caption(
        "Academic Session: 2026–2027"
    )

    st.divider()

    st.caption(
        "Phase 2 • Professional UI"
    )


# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------

render_dashboard()