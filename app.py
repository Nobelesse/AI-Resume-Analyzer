import streamlit as st


st.set_page_config(
    page_title="ResumeAI | AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("📄 ResumeAI")
st.subheader("AI Resume & Job Match Analyzer")

st.write(
    "Analyze your resume, compare it with a job description, "
    "and discover opportunities to improve your profile."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.info(
        """
        ### 📄 Resume Analysis

        Upload your resume PDF to extract:

        - Skills
        - Education
        - Experience
        - Projects
        - Certifications
        """
    )

with col2:
    st.info(
        """
        ### 🎯 Job Matching

        Compare your resume against a job description to discover:

        - Match percentage
        - Matching skills
        - Missing skills
        - Improvement opportunities
        """
    )

st.divider()

st.success("Phase 1 environment is ready.")