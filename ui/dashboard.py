import streamlit as st

from ui.components import (
    render_analysis_button,
    render_feature_cards,
    render_footer,
    render_header,
    render_job_description_input,
    render_resume_uploader,
    render_upload_status,
)


def render_dashboard() -> None:
    """Render the complete ResumeAI dashboard."""

    render_header()

    st.markdown(
        """
        <div class="section-title">
            Analyze your resume against a job description
        </div>

        <div class="section-description">
            Upload your resume and provide the target job description.
            The analysis engine will be connected in later project phases.
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_feature_cards()

    st.divider()

    # ---------------------------------------------------------
    # INPUT SECTION
    # ---------------------------------------------------------

    st.markdown(
        '<div class="section-title">📥 Project Inputs</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-description">
            Provide the two inputs required by the ResumeAI matching system.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("### 📄 Resume PDF")

        uploaded_file = render_resume_uploader()

        if uploaded_file is not None:
            file_size_kb = uploaded_file.size / 1024

            st.success(
                f"Resume uploaded: **{uploaded_file.name}**"
            )

            st.caption(
                f"File size: {file_size_kb:.1f} KB"
            )

    with right_col:
        st.markdown("### 💼 Target Job")

        job_description = render_job_description_input()

        if job_description.strip():
            st.caption(
                f"Job description length: {len(job_description):,} characters"
            )

    st.divider()

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    render_upload_status(
        uploaded_file=uploaded_file,
        job_description=job_description,
    )

    st.divider()

    # ---------------------------------------------------------
    # ANALYSIS
    # ---------------------------------------------------------

    st.markdown(
        '<div class="section-title">🚀 Start Analysis</div>',
        unsafe_allow_html=True,
    )

    analyze_clicked = render_analysis_button()

    if analyze_clicked:

        if uploaded_file is None:
            st.error(
                "Please upload a resume PDF before starting the analysis."
            )
            return

        if not job_description.strip():
            st.error(
                "Please enter a job description before starting the analysis."
            )
            return

        st.info(
            "The interface is ready. Resume extraction and AI matching "
            "will be connected in the upcoming phases."
        )

        st.session_state["resume_uploaded"] = True
        st.session_state["job_description_provided"] = True
        st.session_state["resume_name"] = uploaded_file.name

    st.divider()

    # ---------------------------------------------------------
    # PROJECT STATUS
    # ---------------------------------------------------------

    st.markdown(
        '<div class="section-title">📌 Development Status</div>',
        unsafe_allow_html=True,
    )

    status_col1, status_col2, status_col3, status_col4 = st.columns(4)

    with status_col1:
        st.metric("UI", "Ready")

    with status_col2:
        st.metric("PDF Upload", "Ready")

    with status_col3:
        st.metric("NLP Engine", "Next")

    with status_col4:
        st.metric("Matching", "Planned")

    render_footer()