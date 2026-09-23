import streamlit as st


def render_header() -> None:
    """Render the main ResumeAI header."""

    st.markdown(
        """
        <div class="resumeai-header">
            <div class="resumeai-title">
                Resume<span>AI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "### Intelligent Resume & Job Match Analyzer"
    )

    st.caption(
        "Upload your resume, add a job description, and analyze "
        "your profile against job requirements."
    )

def render_feature_cards() -> None:
    """Render the main product feature cards."""

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📄 Resume Analysis</h3>
                <p>
                    Upload your resume PDF and prepare it for
                    structured analysis of skills, education,
                    experience and other sections.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🎯 Job Matching</h3>
                <p>
                    Provide a job description to compare its
                    requirements with the information contained
                    in your resume.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📊 Smart Insights</h3>
                <p>
                    Later phases will provide matching scores,
                    missing skills, recommendations and
                    visualization of the results.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_resume_uploader():
    """Render and return the uploaded resume."""

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf"],
        help="Upload a PDF resume. Maximum supported size depends on Streamlit configuration.",
    )

    return uploaded_file


def render_job_description_input() -> str:
    """Render the job description input area."""

    job_description = st.text_area(
        "Job Description",
        height=250,
        placeholder=(
            "Paste the job description here...\n\n"
            "Example:\n"
            "We are looking for a Python Developer with experience "
            "in machine learning, SQL, Git and REST APIs."
        ),
        help="Paste the complete job description for future matching analysis.",
    )

    return job_description


def render_analysis_button() -> bool:
    """Render the analysis button."""

    return st.button(
        "🔍 Analyze Resume",
        type="primary",
        use_container_width=True,
    )


def render_upload_status(uploaded_file, job_description: str) -> None:
    """Display the current input status."""

    resume_ready = uploaded_file is not None
    job_ready = bool(job_description.strip())

    if resume_ready and job_ready:
        st.success(
            "Both resume and job description are ready for analysis."
        )

    elif resume_ready:
        st.info(
            "Resume uploaded successfully. Add a job description to continue."
        )

    elif job_ready:
        st.info(
            "Job description added. Upload a resume PDF to continue."
        )

    else:
        st.info(
            "Upload a resume PDF and provide a job description to begin."
        )


def render_footer() -> None:
    """Render the application footer."""

    st.markdown(
        """
        <div class="resumeai-footer">
            ResumeAI • AI Resume & Job Match Analyzer
            <br>
            Minor Project • MCA (AIML) • Oriental University
        </div>
        """,
        unsafe_allow_html=True,
    )