"""Phase 2 command center; honest preview metrics rather than fictitious uploads."""
import streamlit as st
from app.config import GITHUB_URL, MAX_RESUME_BYTES, SUPPORTED_EXTENSIONS
from app.ui.components import metric_tile, feature_tile, section_heading, motion_demo

def render() -> None:
    st.markdown('<div class="eyebrow">✦ UNIVERSITY PROJECT / AUTHENTICATION SYSTEM 03</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Resumes deserve<br><span>a smarter future.</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-copy">An elegant, local-first workspace for explainable resume intelligence. Phase 3 adds SQLite accounts and role-protected sign-in while keeping our interactive design system.</p>', unsafe_allow_html=True)
    left, right = st.columns([1, 1.15], gap="large")
    with left:
        st.markdown('<div class="eyebrow small">INTERACTIVE SHOWCASE</div>', unsafe_allow_html=True)
        st.markdown('<h3 class="subheading">Designed to feel alive.</h3>', unsafe_allow_html=True)
        st.write("Move your cursor over the preview to see a 3D tilt and contextual glow. On touch devices and with reduced-motion preferences, the experience stays still and readable.")
        st.link_button("Explore the GitHub project ↗", GITHUB_URL)
        st.info("Phase 3 active: User and Admin authentication with local SQLite account storage. Resume uploads and scoring arrive later.")
    with right:
        motion_demo(360)
    section_heading("PROJECT CAPABILITIES", "Engineered for the next phases", "Configuration targets and planned features — not fabricated analysis statistics.")
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1: metric_tile("MAX RESUME SIZE", "2 MiB", f"{MAX_RESUME_BYTES:,} bytes per file", "violet")
    with c2: metric_tile("TARGET SKILL CATALOG", "10,000+", "Expandable, curated taxonomy", "cyan")
    with c3: metric_tile("DOCUMENT FORMATS", str(len(SUPPORTED_EXTENSIONS)), "PDF · DOCX · TXT · RTF · ODT", "green")
    section_heading("UPCOMING MODULES", "Built in clearly defined phases", "Security and document handling come before personal data enters the application.")
    a,b,c = st.columns(3, gap="medium")
    with a: feature_tile("◈", "Secure role-based portal", "Separate administrator and user access, protected sessions, and SQLite account records.", "ACTIVE · PHASE 03")
    with b: feature_tile("▣", "Resume understanding", "Strict document validation, parsing and explainable ATS-readiness feedback.", "PHASE 04–05")
    with c: feature_tile("◎", "Skills to jobs", "Normalize skills against a large catalog and reveal job-description gaps.", "PHASE 05–06")
    st.caption("Phase 3 stores registered accounts locally. Resume documents are not collected yet.")
