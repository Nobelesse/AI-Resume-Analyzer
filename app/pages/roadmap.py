"""University-ready walkthrough of the offline resume analysis workflow."""
import streamlit as st


def render():
    st.markdown("**SYSTEM WORKFLOW**")
    st.title("How AI-Resume-Analyzer Works")
    st.write(
        "Follow the journey from a resume upload to skill insights, job matching, "
        "and career recommendations—all within the local workspace."
    )
    st.caption("An overview of the actual user journey, not a development roadmap.")

    st.divider()
    st.subheader("From document to career insight")
    stages = [
        ("01", "Upload a Resume or CV", "A signed-in user uploads a supported document for private analysis.", "📄"),
        ("02", "Extract and Prepare Text", "The application processes the document and prepares its text for analysis.", "🔎"),
        ("03", "Identify Relevant Skills", "Resume evidence is compared with the local skills and occupation catalog.", "🧠"),
        ("04", "Evaluate Job Compatibility", "The matching tools highlight relevant strengths, gaps, and job requirements.", "🎯"),
        ("05", "Explore Career Recommendations", "Career Finder suggests occupational options based on resume evidence.", "🧭"),
        ("06", "Review and Export Results", "Users can review saved analysis information and available reports.", "📊"),
    ]
    for number, heading, detail, symbol in stages:
        left, right = st.columns([1, 12], vertical_alignment="center")
        with left:
            st.markdown(f"### {number}")
        with right:
            st.markdown(f"**{symbol} {heading}**")
            st.write(detail)
        st.divider()

    st.subheader("What makes this project useful")
    first, second, third = st.columns(3)
    with first:
        st.markdown("**🔐 Account-based privacy**")
        st.caption("User and administrator access are managed separately.")
    with second:
        st.markdown("**🗃️ Local information storage**")
        st.caption("SQLite retains the application's account and analysis data locally.")
    with third:
        st.markdown("**🧩 Explainable insights**")
        st.caption("Skill evidence and matching results help users understand recommendations.")

    st.info(
        "**University demo tip:** Sign in as a user, upload a sample resume, "
        "run an analysis, compare it with a job, and open Career Finder. "
        "Use your own sample data for the demonstration."
    )
