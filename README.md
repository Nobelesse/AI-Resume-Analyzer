# AI-Resume-Analyzer — Phase 5

Complete integrated Phase 1–5 local Streamlit university project. Python 3.11.0.

## Installation in Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

Admin initialization (only once):

```powershell
.\.venv\Scripts\python.exe scripts/create_admin.py
```

## Phase 5 features

* Protected personal resume analysis, saved analysis history, deterministic local ATS-readiness heuristics.
* 12 categories of curated starter skills, synonym aliases, SQLite indexed taxonomy and reviewed CSV bulk import.
* Supports 10,000+ skills without bundling fictitious/unverified entries. To expand, procure a trustworthy licensed skills taxonomy as CSV (`name,category,aliases`); then:

```powershell
.\.venv\Scripts\python.exe scripts/import_skills.py path\to\reviewed_skills.csv
```

* The sample **10,001 skills** capacity test uses synthetic data in a temporary test database only.
* A score is a reproducible heuristic, not a guarantee or real third-party ATS score.

## Updating a prior phase safely

Stop Streamlit. Back up `C:\Projects\AI-Resume-Analyzer` before merging. Copy source while excluding `.git`, `.venv`, `data`, `.env`, caches and local database files. Then install requirements, run tests and start Streamlit. **Do not delete the previous database or reinitialize admin accounts.**

## GitHub

```powershell
git status
git add app docs tests scripts README.md requirements.txt requirements-dev.txt
git diff --cached --name-only
git commit -m "Phase 5: ATS analysis and extensible skill catalog"
git push origin main
```

Private `data/`, `.env` and `.venv/` must never be committed.

## Phase 6 — Job matching

User portal: **Job Match Studio** and **Job Match History**. Requires a previously uploaded resume. Required/preferred sections may use `Required:` and `Preferred:` headings. Comparison results are saved in SQLite; PDF and HTML downloads are available. Run `python -m pytest -q` after installing `requirements-dev.txt` (which installs requirements.txt). See `docs/phase6.md`.
