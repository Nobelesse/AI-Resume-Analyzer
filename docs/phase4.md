# Phase 4 architecture

- Parsing service: `app/services/resume_parser.py` performs 2 MB validation and extracts text from PDF, DOCX, TXT, RTF, ODT.
- Persistence: `app/database/resumes.py` owns all file writing and DB reads. Records include sha256, size, normalized extension, extracted text, and owner ID.
- Security: `require_role` validates active users against the database. `get_resume` prevents cross-account reads; admin listing verifies admin role.
- DB schema upgrade: `initialize_database` creates `resumes` with an owner FK, indexes, and increments SQLite `user_version` without erasing accounts.
- View: protected Streamlit pages use service methods and never read DB rows directly.
- Limitations: PDF OCR and AV scanning are not yet included; do not process untrusted documents in exposed production servers without further isolation.
