"""UI 1.2 dashboard with interactive intelligence sphere."""
import streamlit as st
from app.config import MAX_RESUME_BYTES, SUPPORTED_EXTENSIONS
from app.ui.components import section_heading, metric_tile, intelligence_sphere
from app.ui.navigation import navigation_card
from app.ui.session import session_user

USER_CARDS = [
    ("Upload Resume", "Securely submit your resume", "upload-resume", "📤"),
    ("AI Resume Analysis", "Understand your resume strengths", "resume-analysis", "🧠"),
    ("Job Match Studio", "Compare your profile with real roles", "job-match", "🎯"),
    ("AI Career Finder", "Discover careers suited to your skills", "career-finder", "🧭"),
    ("My Resumes", "Browse your uploaded documents", "my-resumes", "📄"),
    ("Analysis History", "Return to saved ATS analyses", "analysis-history", "📊"),
    ("Job Match History", "See previous job comparisons", "job-history", "📑"),
    ("User Dashboard", "Explore your personal statistics", "user-dashboard", "◈"),
]
ADMIN_CARDS = [
    ("Admin Dashboard", "Application-wide overview", "admin-dashboard", "◈"),
    ("Resume Management", "Review authorized submissions", "admin-resume-management", "📚"),
    ("Account Management", "Manage account permissions", "account-management", "👥"),
    ("Activity Log", "Review recorded administrative events", "audit-log", "📋"),
]


def render() -> None:
    current = session_user()
    role = current.get("role") if current else None

    st.markdown('<div class="hero-shell">', unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        st.markdown(
            '<div class="u12-hero-copy">'
            '<div class="v10-kicker"><span class="v10-dot"></span> LOCAL AI · PRIVATE BY DESIGN</div>'
            '<h1 class="u12-headline">A sharper view of <em>your potential.</em></h1>'
            '<p class="u12-lead">Intelligent resume analysis, role matching and career discovery in one focused workspace.</p>'
            '<div class="u12-tags"><span>✧ Resume intelligence</span><span>◈ Skill matching</span><span>↗ Career discovery</span></div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="u12-sphere-frame">', unsafe_allow_html=True)
        intelligence_sphere(380)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if role in ("user", "admin"):
        section_heading("YOUR WORKSPACE", "Choose your next move", "Every card opens its actual workspace page.")
        cards = USER_CARDS if role == "user" else ADMIN_CARDS
        with st.container(key="workspace_cards"):
            for idx in range(0, len(cards), 2):
                cols = st.columns(2, gap="medium")
                for col, card in zip(cols, cards[idx:idx+2]):
                    with col:
                        navigation_card(*card)
    else:
        section_heading("YOUR WORKSPACE", "Everything your next opportunity needs", "Sign in to access your private documents and career tools.")
        a, b, c = st.columns(3, gap="medium")
        with a:
            metric_tile("UPLOAD LIMIT", "2 MB", f"{MAX_RESUME_BYTES:,} bytes per resume", "violet")
        with b:
            metric_tile("SUPPORTED FORMATS", str(len(SUPPORTED_EXTENSIONS)), "PDF · DOCX · TXT · RTF · ODT", "cyan")
        with c:
            metric_tile("PRIVATE AI ENGINE", "Ollama", "Job intelligence on your PC", "green")
        st.info("Open User Login or Admin Login in the sidebar to get started.")

    st.markdown(
        '<p class="v10-footer">AI-guided insights are estimates, not hiring decisions. Your workspace remains local to your computer.</p>',
        unsafe_allow_html=True,
    )
