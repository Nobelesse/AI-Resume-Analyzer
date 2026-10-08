# AI-Resume-Analyzer — Phase 4 (integrated)

University project for **Python 3.11.0**, Streamlit and SQLite. Includes all Phase 1–3 UI/auth work plus secure Phase 4 resume uploads, extraction and protected resume records.

## Windows VS Code quickstart

From `C:\Projects\AI-Resume-Analyzer`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/create_admin.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

If an administrator already exists in the existing SQLite DB, do not rerun initial setup. **Run `app/main.py`, not root-level `main.py`.** The application assigns an explicit unique Streamlit URL path for every page.

## Workflow

1. Create a user account with **User Registration**; sign in through **User Login**.
2. Open **Upload Resume**, choose a PDF, DOCX, TXT, RTF or ODT of **at most 2,097,152 bytes**, and upload.
3. View your own documents and extracted text in **My Resumes**.
4. Sign in via **Admin Login**, then open **All Resumes** to view every applicant record and extracted text.
5. User accounts cannot query another user's resume or list all applicant records. Admin functions enforce access restrictions in database service functions.

## Storage and security

The SQLite DB is `data/resume_analyzer.sqlite3` and original files are in `data/uploads` with randomly generated names. Both are ignored by Git. Original filenames are never used as filesystem paths. No resumes go to external services. Stored extracted text is sensitive; this local university demo is not a production-grade multi-tenant deployment. Use OS-level account/disk protection and do not sync private folders publicly. For public deployment, add CSRF-aware identity/session infrastructure, malware scanning, document sandboxing, encryption at rest, retention controls and production-grade isolation.

PDF text extraction does not include OCR; image-only PDFs cannot be processed. RTF extraction is best-effort (plain paragraphs, without rich layouts). ZIP-based DOCX and ODT documents have bounded entry counts and expanded sizes.

## GitHub after upgrade

```powershell
git status
git add .
git diff --cached --name-only
git commit -m "Phase 4: Secure resume uploads and protected document records"
git push origin main
```

Check staged files for personal information before committing. A copy of the full project is included in each phase.
