"""Current product security and technology information (no legacy prototype claims)."""
import streamlit as st
from app.ui.components import section_heading


def render() -> None:
    section_heading(
        "PRIVACY & TECHNOLOGY", "Built for transparent, local analysis.",
        "Learn how the workspace processes resumes, protects roles, and explains its results.",
    )
    st.markdown("""### Private workspace
Resume files and saved results are handled by the configured application database and local storage. Access to user and administrator views is governed by role checks. Administrators have authorized management tools; standard users use their own workspace. **Protect your computer and database backups:** local operation does not guarantee security on a compromised machine.

### Explainable analysis
The application supports PDF, DOCX, TXT, RTF and ODT resumes (2 MB limit) and CVs (10 MB limit). It offers skill extraction, resume readiness, job comparisons, and career exploration. Results are estimates based on the evidence detected in the text; they are not employer ATS scores, hiring predictions, or verification of credentials.

### Offline-first tools
The core application uses Python, Streamlit and SQLite, with local skill and occupation catalogs. The resume and job matching workflows can operate without a paid language model. Some optional external integrations may require an internet connection.

### Responsible use
Always check imported datasets, extracted PDF reading order, job requirements and qualifications manually before making consequential career decisions. Do not rely on automated scores alone.
""")
