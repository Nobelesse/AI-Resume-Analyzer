"""Getting Started: product workflows, not a visual demonstration page."""
import streamlit as st

from app.ui.components import section_heading
from app.ui.navigation import navigation_card
from app.ui.session import session_user


def render() -> None:
    section_heading(
        "QUICK START",
        "Getting Started",
        "A practical guide to the actual resume intelligence workflows.",
    )
    user = session_user()
    st.markdown("### How the platform works")
    if user is None:
        st.markdown(
            "**1. Create an account or sign in.** Your resumes and analysis history "
            "are protected by account-based access.\n\n"
            "**2. Upload your resume.** Supported formats: PDF, DOCX, TXT, RTF and ODT "
            "(maximum 2 MB).\n\n"
            "**3. Analyze your profile.** Run resume-readiness checks, compare against "
            "a job posting, or explore suitable career paths.\n\n"
            "**4. Review and export.** Inspect the results, download available reports "
            "and revisit saved comparisons."
        )
        st.info("Choose User Login or User Registration in the sidebar to begin.")
    elif user.get("role") == "admin":
        st.markdown(
            "**1. Review platform activity.** Start from the Admin Dashboard.\n\n"
            "**2. Manage authorized resumes and accounts.** Use role-based administrative pages.\n\n"
            "**3. Review audit events and skills catalog.** Inspect operational data "
            "without changing candidate assessment results."
        )
        cols = st.columns(2)
        with cols[0]:
            navigation_card("Admin Dashboard", "Review platform activity", "admin-dashboard", "◈")
        with cols[1]:
            navigation_card("Skills Catalog", "Review imported taxonomy", "skills-catalog", "▤")
    else:
        st.markdown(
            "**1. Upload a resume.** Select a supported file up to 2 MB.\n\n"
            "**2. Review ATS Intelligence.** Inspect resume readiness and, optionally, "
            "job compatibility. Scores are estimates, not employer ATS decisions.\n\n"
            "**3. Match a job description.** Compare skills against an actual posting "
            "for more meaningful results than a job title alone.\n\n"
            "**4. Explore Career Finder.** Review suggested occupations and learning topics.\n\n"
            "**5. Save and download.** Revisit your permitted records and reports."
        )
        first = st.columns(2)
        with first[0]:
            navigation_card("Upload Resume", "Add a resume to your library", "upload-resume", "↥")
        with first[1]:
            navigation_card("ATS Intelligence", "Check resume readability", "resume-analysis", "✦")
        second = st.columns(2)
        with second[0]:
            navigation_card("Job Match Studio", "Compare with job requirements", "job-match", "◎")
        with second[1]:
            navigation_card("AI Career Finder", "Explore related careers", "career-finder", "◇")
    st.caption(
        "Local datasets and matching support decision-making; they do not verify "
        "employment, certifications or hiring eligibility."
    )
