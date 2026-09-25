import streamlit as st

from src.pdf.extractor import extract_text_from_pdf

from src.recommendations.skill_recommender import (
    JOB_ROLE_PROFILES,
    match_resume_to_target_job,
    recommend_job_roles_from_resume,
)

from ui.components import (
    render_analysis_button,
    render_feature_cards,
    render_footer,
    render_header,
    render_job_description_input,
    render_resume_uploader,
    render_upload_status,
)


def render_extraction_result(extraction_result) -> None:
    """
    Display the result of resume PDF extraction.
    """
    st.markdown(
        '<div class="section-title">📄 Resume Extraction</div>',
        unsafe_allow_html=True,
    )

    if not extraction_result.success:
        st.error(extraction_result.message)
        return

    st.success(extraction_result.message)

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric(
            "Pages",
            extraction_result.page_count,
        )

    with metric_col2:
        st.metric(
            "Characters",
            f"{extraction_result.character_count:,}",
        )

    with metric_col3:
        st.metric(
            "Words",
            f"{extraction_result.word_count:,}",
        )

    st.markdown("### 🔎 Extracted Resume Text")

    st.text_area(
        "Resume text preview",
        value=extraction_result.text,
        height=450,
        disabled=True,
        label_visibility="collapsed",
    )

    st.caption(
        "This is the raw text extracted from the uploaded PDF. "
        "The extracted text is passed to the NLP skill "
        "extraction, target-job matching, and job-role "
        "recommendation engines."
    )


def render_resume_skills(resume_skills) -> None:
    """
    Display the skills detected in the uploaded resume.
    """
    st.markdown(
        '<div class="section-title">🧠 Detected Resume Skills</div>',
        unsafe_allow_html=True,
    )

    if not resume_skills:
        st.warning(
            "No recognized technical or professional skills "
            "were found in the resume."
        )
        return

    st.success(
        f"Detected {len(resume_skills)} recognized skill"
        f"{'s' if len(resume_skills) != 1 else ''}."
    )

    skill_columns = st.columns(4)

    for index, skill in enumerate(resume_skills):
        with skill_columns[index % 4]:
            st.markdown(
                f"""
                <div class="feature-card">
                    <h4>✓ {skill}</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_target_job_match(match_result) -> None:
    """
    Display direct resume-to-target-job skill matching.
    """
    st.markdown(
        '<div class="section-title">'
        "🎯 Target Job Match"
        "</div>",
        unsafe_allow_html=True,
    )

    if not match_result.success:
        st.warning(match_result.message)
        return

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric(
            "Skill Match",
            f"{match_result.skill_match_percentage:.2f}%",
        )

    with metric_col2:
        st.metric(
            "Job Skills",
            len(match_result.job_skills),
        )

    with metric_col3:
        st.metric(
            "Matched Skills",
            len(match_result.matched_skills),
        )

    st.caption(
        "Skill Match shows the percentage of recognized target-job "
        "skills that were also detected in the resume. It is a "
        "skill-coverage measure, not a hiring probability."
    )

    matched_col, missing_col = st.columns(2)

    with matched_col:
        st.markdown("### ✅ Matched Skills")

        if match_result.matched_skills:
            for skill in match_result.matched_skills:
                st.markdown(f"- ✅ {skill}")
        else:
            st.info(
                "No detected target-job skills matched "
                "the resume."
            )

    with missing_col:
        st.markdown("### ❌ Missing Skills")

        if match_result.missing_skills:
            for skill in match_result.missing_skills:
                st.markdown(f"- ❌ {skill}")
        else:
            st.success(
                "All detected target-job skills are present "
                "in the resume."
            )

    with st.expander("📋 Target Job Skills", expanded=True):
        if match_result.job_skills:
            skill_columns = st.columns(4)

            for index, skill in enumerate(
                match_result.job_skills
            ):
                with skill_columns[index % 4]:
                    st.markdown(f"- {skill}")

    if match_result.extra_resume_skills:
        with st.expander(
            "➕ Additional Resume Skills",
            expanded=False,
        ):
            st.caption(
                "These skills were detected in the resume but "
                "were not detected in the target job description."
            )

            for skill in match_result.extra_resume_skills:
                st.markdown(f"- {skill}")

    if match_result.experience_requirements:
        with st.expander(
            "🕒 Detected Experience Requirements",
            expanded=False,
        ):
            for requirement in (
                match_result.experience_requirements
            ):
                st.markdown(f"- {requirement}")

    if match_result.education_requirements:
        with st.expander(
            "🎓 Detected Education Requirements",
            expanded=False,
        ):
            for requirement in (
                match_result.education_requirements
            ):
                st.markdown(f"- {requirement}")


def render_role_recommendation(recommendation) -> None:
    """
    Display one recommended job role in detail.
    """
    st.markdown(
        f"### 💼 {recommendation.role}"
    )

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric(
            "Skill Alignment Score",
            f"{recommendation.score:.2f}%",
        )

    with metric_col2:
        st.metric(
            "Alignment",
            recommendation.alignment,
        )

    st.write(recommendation.rationale)

    required_col, preferred_col = st.columns(2)

    with required_col:
        st.markdown("#### 🎯 Required Skills")

        if recommendation.matched_skills:
            st.markdown("**Matched:**")

            for skill in recommendation.matched_skills:
                st.markdown(f"- ✅ {skill}")

        if recommendation.missing_skills:
            st.markdown("**Missing:**")

            for skill in recommendation.missing_skills:
                st.markdown(f"- ❌ {skill}")

        if not recommendation.matched_skills:
            st.info("No required skills matched.")

        if not recommendation.missing_skills:
            st.success("All required skills matched.")

    with preferred_col:
        st.markdown("#### ⭐ Preferred Skills")

        if recommendation.preferred_matched_skills:
            for skill in recommendation.preferred_matched_skills:
                st.markdown(f"- ✅ {skill}")
        else:
            st.info(
                "No preferred skills from this role "
                "were detected."
            )

        profile = next(
            (
                item
                for item in JOB_ROLE_PROFILES
                if item.name == recommendation.role
            ),
            None,
        )

        if (
            profile is not None
            and profile.preferred_skills
        ):
            st.markdown("**Role preference profile:**")

            for skill in profile.preferred_skills:
                st.markdown(f"- {skill}")

    if recommendation.category_coverage:
        st.markdown(
            "#### 📊 Required Skill Coverage by Category"
        )

        coverage_columns = st.columns(
            len(recommendation.category_coverage)
        )

        for index, (
            category,
            coverage,
        ) in enumerate(
            recommendation.category_coverage.items()
        ):
            with coverage_columns[index]:
                display_name = (
                    category
                    .replace("_", " ")
                    .title()
                )

                st.metric(
                    display_name,
                    f"{coverage:.1f}%",
                )


def render_job_recommendations(
    recommendation_result,
) -> None:
    """
    Display resume-to-job-role recommendations.
    """
    st.markdown(
        '<div class="section-title">💼 Suitable Job Roles</div>',
        unsafe_allow_html=True,
    )

    if not recommendation_result.success:
        st.warning(
            recommendation_result.message
        )
        return

    recommendations = (
        recommendation_result.recommendations
    )

    if not recommendations:
        st.info(
            "No suitable job roles could be identified "
            "from the detected resume skills."
        )
        return

    st.success(
        recommendation_result.message
    )

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        with st.container(border=True):
            st.markdown(
                f"## {index}. {recommendation.role}"
            )

            render_role_recommendation(
                recommendation
            )


def render_dashboard() -> None:
    """
    Render the complete ResumeAI dashboard.
    """
    render_header()

    st.markdown(
        """
        <div class="section-title">
            Analyze your resume and discover suitable job roles
        </div>
        <div class="section-description">
            Upload your resume to extract skills, compare them
            against a target job description, and identify
            suitable technology roles based on your current
            skill profile.
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
            Upload your resume PDF. You can also provide a target
            job description to identify matched and missing skills.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("### 📄 Resume PDF")

        uploaded_file = render_resume_uploader()

        if uploaded_file is not None:
            file_size_kb = (
                uploaded_file.size / 1024
            )

            st.success(
                f"Resume uploaded: "
                f"**{uploaded_file.name}**"
            )

            st.caption(
                f"File size: {file_size_kb:.1f} KB"
            )

    with right_col:
        st.markdown("### 💼 Target Job")

        job_description = (
            render_job_description_input()
        )

        if job_description.strip():
            st.caption(
                f"Job description length: "
                f"{len(job_description):,} characters"
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

    st.caption(
        "Phase 6.4 extracts resume skills, matches them against "
        "the optional target job, and recommends suitable "
        "predefined job roles."
    )

    analyze_clicked = render_analysis_button()

    if analyze_clicked:

        # -----------------------------------------------------
        # Resume validation
        # -----------------------------------------------------
        if uploaded_file is None:
            st.error(
                "Please upload a resume PDF before starting "
                "the analysis."
            )
            return

        # -----------------------------------------------------
        # Read uploaded PDF
        # -----------------------------------------------------
        with st.spinner(
            "Reading and extracting your resume..."
        ):
            file_bytes = uploaded_file.getvalue()

            extraction_result = (
                extract_text_from_pdf(
                    file_bytes
                )
            )

        # -----------------------------------------------------
        # Display extraction result
        # -----------------------------------------------------
        render_extraction_result(
            extraction_result
        )

        # -----------------------------------------------------
        # Stop if extraction failed
        # -----------------------------------------------------
        if not extraction_result.success:
            return

        # -----------------------------------------------------
        # Store successful extraction in session state
        # -----------------------------------------------------
        st.session_state["resume_uploaded"] = True

        st.session_state["resume_name"] = (
            uploaded_file.name
        )

        st.session_state["resume_text"] = (
            extraction_result.text
        )

        st.session_state["resume_page_count"] = (
            extraction_result.page_count
        )

        st.session_state["resume_word_count"] = (
            extraction_result.word_count
        )

        st.session_state["target_job_description"] = (
            job_description
        )

        # -----------------------------------------------------
        # Resume skill extraction + job-role recommendation
        # -----------------------------------------------------
        with st.spinner(
            "Analyzing resume skills and identifying "
            "suitable job roles..."
        ):
            recommendation_result = (
                recommend_job_roles_from_resume(
                    extraction_result.text,
                    top_n=5,
                )
            )

        # -----------------------------------------------------
        # Store recommendation result
        # -----------------------------------------------------
        st.session_state[
            "job_role_recommendation_result"
        ] = recommendation_result

        # -----------------------------------------------------
        # Target-job matching
        # -----------------------------------------------------
        target_job_match_result = None

        if job_description.strip():
            with st.spinner(
                "Analyzing the target job and comparing "
                "required skills..."
            ):
                target_job_match_result = (
                    match_resume_to_target_job(
                        extraction_result.text,
                        job_description,
                    )
                )

            st.session_state[
                "target_job_match_result"
            ] = target_job_match_result

        else:
            st.session_state.pop(
                "target_job_match_result",
                None,
            )

        # -----------------------------------------------------
        # Display detected resume skills
        # -----------------------------------------------------
        render_resume_skills(
            recommendation_result.resume_skills
        )

        st.divider()

        # -----------------------------------------------------
        # Display target-job matching
        # -----------------------------------------------------
        if target_job_match_result is not None:
            render_target_job_match(
                target_job_match_result
            )

            st.divider()

        # -----------------------------------------------------
        # Display suitable job roles
        # -----------------------------------------------------
        render_job_recommendations(
            recommendation_result
        )

    # ---------------------------------------------------------
    # DISPLAY PREVIOUS RESULTS
    # ---------------------------------------------------------
    elif (
        "job_role_recommendation_result"
        in st.session_state
    ):
        recommendation_result = (
            st.session_state[
                "job_role_recommendation_result"
            ]
        )

        st.divider()

        st.markdown(
            '<div class="section-title">'
            "📌 Previous Resume Analysis"
            "</div>",
            unsafe_allow_html=True,
        )

        render_resume_skills(
            recommendation_result.resume_skills
        )

        previous_target_match = (
            st.session_state.get(
                "target_job_match_result"
            )
        )

        if previous_target_match is not None:
            st.divider()

            render_target_job_match(
                previous_target_match
            )

        st.divider()

        render_job_recommendations(
            recommendation_result
        )

    # ---------------------------------------------------------
    # PROJECT STATUS
    # ---------------------------------------------------------
    st.divider()

    st.markdown(
        '<div class="section-title">📌 Development Status</div>',
        unsafe_allow_html=True,
    )

    (
        status_col1,
        status_col2,
        status_col3,
        status_col4,
    ) = st.columns(4)

    with status_col1:
        st.metric(
            "UI",
            "Ready",
        )

    with status_col2:
        st.metric(
            "PDF Extraction",
            "Ready",
        )

    with status_col3:
        st.metric(
            "Skill Extraction",
            "Ready",
        )

    with status_col4:
        st.metric(
            "Job Matching",
            "Ready",
        )

    render_footer()