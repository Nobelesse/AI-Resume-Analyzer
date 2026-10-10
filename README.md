# AI-Resume-Analyzer — Integrated Phase 7

University-level local Streamlit application. Python 3.11, SQLite, Argon2id, secure resume upload (2 MiB, PDF/DOCX/TXT/RTF/ODT), explainable ATS analysis, skill catalog, job comparisons, Ollama-assisted occupation profiles and career suggestions, and Phase 7 protected dashboards.

## Launch on Windows

```powershell
cd "C:\Projects\AI-Resume-Analyzer"
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

For new installations, create a Python 3.11 venv using `py -3.11 -m venv .venv`, then initialize your first admin with `.\.venv\Scripts\python.exe scripts/create_admin.py`. Existing databases remain intact when upgrading.

## Phase 7 screens

**Admins**: Admin Dashboard, Resume Management, Account Management, Activity Log. **Users**: User Dashboard, Manage My Records, My Resumes, AI Resume Analysis, Job Match Studio, AI Career Finder and histories. Each Streamlit page has a unique pathname.

See `docs/phase7.md` for privacy/security notes; earlier phase documentation is retained in `docs/`.

## GitHub

The `.gitignore` excludes `.venv`, `.env`, databases, generated files and uploads. Always review `git diff --cached --name-only` before committing. Keep private candidate data out of public repositories.
