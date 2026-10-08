"""Landing page for the first runnable milestone."""
import streamlit as st
from app.config import GITHUB_URL, MAX_RESUME_BYTES, SUPPORTED_EXTENSIONS


def render() -> None:
    st.markdown('<div class="eyebrow">✦ INTELLIGENT CAREER TECHNOLOGY · PHASE 01</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Make your resume <span>work smarter.</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-copy">A privacy-conscious, explainable resume intelligence platform. The interface foundation is ready; authentication, file processing and job matching will be activated in upcoming phases.</p>', unsafe_allow_html=True)

    a, b, c = st.columns(3, gap="medium")
    with a:
        st.markdown('<div class="feature-card"><div class="feature-icon">▣</div><h3>Multi-format documents</h3><p>PDF, DOCX, TXT, RTF and ODT are planned. Validation and extraction arrive in Phase 4.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="feature-card"><div class="feature-icon">✧</div><h3>Skills intelligence</h3><p>Expandable catalog targeting 10,000+ skills, synonyms and job-description matching.</p></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="feature-card"><div class="feature-icon">◈</div><h3>Private local storage</h3><p>Separate Admin and User permissions and SQLite persistence will be added in Phase 3.</p></div>', unsafe_allow_html=True)

    st.markdown('### Project specifications')
    st.write(f"**File limit:** {MAX_RESUME_BYTES:,} bytes (2 MiB)  ·  **Planned file types:** {', '.join(x.upper() for x in SUPPORTED_EXTENSIONS)}")
    st.info("Phase 1 is a functional Streamlit UI foundation. Resume upload and user login are deliberately not active yet.")
    st.link_button("View GitHub repository", GITHUB_URL, use_container_width=False)
