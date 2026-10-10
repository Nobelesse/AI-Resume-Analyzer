# AI-Resume-Analyzer — final university demonstration guide

## Aim
Build a local Streamlit tool for authenticated resume uploads, explainable ATS-readiness evaluation, job-description matching, and suggested career paths.

## Demo (8–12 minutes)
1. Open the Command Center and explain Python 3.11, Streamlit, SQLite and Ollama architecture.
2. Register a standard user or sign in with a non-sensitive demonstration account.
3. Upload a fictional TXT/DOCX/PDF resume below 2 MB. Explain ownership checks and parsing constraints.
4. Open My Resumes and show the extracted text.
5. Run AI Resume Analysis and explain the rule-based ATS-readiness score and its limitations.
6. Enter `Software Tester` in Job Match Studio. Explain that title-only skills are suggestions; a real job posting takes precedence.
7. Enter a different title such as `Postman` and demonstrate the local Ollama fallback (may take minutes on 8 GB RAM).
8. Open AI Career Finder and inspect suggested alternative roles, clearly distinguishing detected keywords from verified proficiency.
9. Sign out, then sign in as administrator. Show protected resume management, exports, account deactivation and audit logs.
10. Run automated tests and `scripts/final_audit.py` in VS Code.

## Security boundaries and limits
- 2 MB per document, five supported formats, upload content checks and parsing limits.
- Original uploads and extracted text are sensitive data: store locally, keep out of GitHub, avoid uploading real candidates' resumes for public demonstration.
- Admin access to all records is intended by the project; students view only their own.
- Local SQLite files and backups are not encrypted at rest; safeguard the Windows account and disk.
- Rate limiting is local and account-keyed, not a replacement for production-grade edge controls.
- Session state uses Streamlit's server-side session model. Avoid public deployment without separate security review and HTTPS authentication strategy.
- Ollama-generated occupation details and career suggestions can be wrong. For regulated professions verify licensing, residency, training and local eligibility separately.
- No guarantee of real-world ATS screening, hiring probability or professional qualification.
- Scanned image-based PDFs require OCR (not included).

## Database architecture
SQLite tables: users, login_throttle, resumes, analyses, job_matches, skills, skill_aliases, activity_logs. Dependent records are deleted using referential integrity where configured.

## Validation commands
`python -m pytest -q`
`python scripts/final_audit.py`
`python -m compileall -q app scripts`
`python -m pip check`

## Suggested viva questions
- Why Streamlit instead of a client-server React setup?
- Why use Argon2id for password hashing?
- How is file ownership enforced below the UI layer?
- Why can a title-only suggested skill not be called an employer requirement?
- What does the 2 MB upload threshold prevent, and what risks remain?
- How do Ollama timeouts and 1B fallback work on an 8 GB PC?
- What does the scoring formula measure, and what does it not measure?
- How can the skill taxonomy be expanded with independently licensed datasets?
