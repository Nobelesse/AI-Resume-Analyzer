# AI-Resume-Analyzer

University-level Streamlit resume intelligence project for GitHub user **Nobelesse**.

## Phase 1 status

Available now: a branded Streamlit landing page, architecture and roadmap pages, foundational settings, style definitions, and smoke tests.

**Not implemented yet:** authentication, uploading, parsing, ATS scoring, SQLite, and job matching. Please do not upload private resume data until security and upload features are complete.

## Requirements

- Windows 10/11, VS Code, Git
- Python **3.11.0** (64-bit recommended)

## Installation (PowerShell in project folder)

```powershell
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
```

## Start

```powershell
.\run.ps1
```

Open http://localhost:8501 .

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q app
```

## Privacy

`.gitignore` excludes `.env`, `.streamlit/secrets.toml`, virtual environments, SQLite databases, and uploaded resume files. Keep private data out of commits.

## Project plan

Eight phases: foundation, interface, authentication/database, parsing, skills/ATS analysis, job matching/reports, dashboards, testing/release.
