"""Finished-product dashboard with actual page navigation."""
import streamlit as st
from app.config import MAX_RESUME_BYTES, SUPPORTED_EXTENSIONS
from app.ui.components import section_heading, metric_tile
from app.ui.navigation import navigation_card
from app.ui.session import session_user

USER_CARDS = [
    ("Upload Resume", "Securely submit a PDF, DOCX, TXT, RTF or ODT file", "upload-resume", "📤"),
    ("AI Resume Analysis", "Explore strengths, ATS-readiness and improvements", "resume-analysis", "🧠"),
    ("Job Match Studio", "Compare your resume with an occupation or posting", "job-match", "🎯"),
    ("AI Career Finder", "Discover careers using your resume evidence", "career-finder", "🧭"),
    ("My Resumes", "Open the private document library", "my-resumes", "📄"),
    ("Analysis History", "Explore saved resume intelligence", "analysis-history", "📊"),
    ("Job Match History", "Revisit your career comparisons and reports", "job-history", "📑"),
    ("User Dashboard", "View your personal workspace analytics", "user-dashboard", "◈"),
]
ADMIN_CARDS = [
    ("Admin Dashboard", "See application-wide activity and insights", "admin-dashboard", "◈"),
    ("Resume Management", "Search and manage authorized submissions", "admin-resume-management", "📚"),
    ("Account Management", "Manage user account access", "account-management", "👥"),
    ("Activity Log", "Audit recorded administrative events", "audit-log", "📋"),
]

def render() -> None:
    current = session_user()
    st.markdown('<div class="eyebrow">✦ RESUME INTEL / CAREER INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Your career, <span>reimagined.</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-copy">Explore your experience, discover career possibilities and make smarter next moves with secure resume analysis and local AI.</p>', unsafe_allow_html=True)
    if current and current["role"] in ("user", "admin"):
        st.markdown('<div class="welcome-pill">● &nbsp; Your private workspace is ready</div>', unsafe_allow_html=True)
        section_heading("EXPLORE", "Your AI workspace", "Choose any tool below. Each tile opens its actual workspace page.")
        cards = USER_CARDS if current["role"] == "user" else ADMIN_CARDS
        for i in range(0, len(cards), 2):
            cols = st.columns(2, gap="large")
            for col, card in zip(cols, cards[i:i+2]):
                with col:
                    navigation_card(*card)
    else:
        section_heading("EXPLORE", "Built for clarity. Designed for progress.", "A private, local-first application with dedicated user and administrator sign-in.")
        c1,c2,c3 = st.columns(3)
        with c1: metric_tile("DOCUMENT LIMIT", "2 MB", f"{MAX_RESUME_BYTES:,} bytes per file", "violet")
        with c2: metric_tile("SUPPORTED FILE TYPES", str(len(SUPPORTED_EXTENSIONS)), "PDF · DOCX · TXT · RTF · ODT", "cyan")
        with c3: metric_tile("LOCAL AI", "Ollama", "Occupation discovery and career matching", "green")
        st.info("Sign in through User Login or Admin Login in the sidebar to access your tools.")
    st.divider()
    st.caption("Local-first • Role-protected data • Explainable estimates, not hiring decisions")
