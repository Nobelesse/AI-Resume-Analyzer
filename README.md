## UI 1.2.1 — Full-width interactive intelligence hero

The home hero now puts text over a full-width interactive network-sphere canvas; see `docs/UI_1_2_1.md`.

# AI-Resume-Analyzer — UI Upgrade 0.9.0

University-level local Streamlit application. Python 3.11, SQLite, Argon2id, secure resume upload (2 MB, PDF/DOCX/TXT/RTF/ODT), explainable ATS analysis, skill catalog, job comparisons, Ollama-assisted occupation profiles and career suggestions, and protected admin/user dashboards. The new overview has actual clickable workflow tiles, a darker futuristic presentation, and completed milestones.

## Launch on Windows

```powershell
cd "C:\Projects\AI-Resume-Analyzer"
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

For new installations, create a Python 3.11 venv using `py -3.11 -m venv .venv`, then initialize your first admin with `.\.venv\Scripts\python.exe scripts/create_admin.py`. Existing databases remain intact when upgrading.

## Available screens

**Admins**: Admin Dashboard, Resume Management, Account Management, Activity Log. **Users**: User Dashboard, Manage My Records, My Resumes, AI Resume Analysis, Job Match Studio, AI Career Finder and histories. Each Streamlit page has a unique pathname.

See `docs/phase7.md` for privacy/security notes; earlier phase documentation is retained in `docs/`.

## GitHub

The `.gitignore` excludes `.venv`, `.env`, databases, generated files and uploads. Always review `git diff --cached --name-only` before committing. Keep private candidate data out of public repositories.


## Phase 8 final checks

Run `python scripts/final_audit.py` and `python -m pytest -q`. See `docs/FINAL_UNIVERSITY_GUIDE.md` and `docs/SECURITY_FINAL.md` for demonstration, risk disclosures and handover details.

## UI 0.9.0
All eight project milestones display complete. The file upload limit is 2,000,000 bytes, enforced in server-side validation. The workspace tiles are accessible native buttons that navigate to pages registered for the current account. See `docs/UI_UPGRADE_0_9_0.md`.


## UI 1.0 — Milestone 1

A new cohesive visual shell and dashboard have been integrated. See `docs/UI_1_0_FOUNDATION.md`. The remaining UI 1.0 milestones will redesign tool-specific and admin pages.


## UI 1.0 — Milestone 2
Professional styling is now consistent across authentication, resume upload, ATS reports, job comparison and AI Career Finder. See `docs/UI_1_0_MILESTONE_2.md`.


## UI 1.0 Milestone 3
Admin dashboard, account management, applicant records and activity log have a refreshed consistent design. See `docs/UI_1_0_MILESTONE_3.md`.


## UI 1.1 Immersive Motion
Animated orbital hero, contextual panel depth and revamped Experience Center. See `docs/UI_1_1_MOTION.md`.

## v1.4 — Official occupation and skills catalog imports

See [Version 1.4 taxonomy guide](docs/VERSION_1_4_TAXONOMY.md). This release implements importers and matching for official CSV data; complete ESCO/O*NET datasets are not distributed inside the project. Run the source-verified imports separately, and use `scripts/taxonomy_stats.py` to report actual counts.

### Version 1.4.1 — Expanded O*NET data

Use existing O*NET 31.0 CSV extraction (no extra download):

```powershell
.\.venv\Scripts\python.exe scripts/import_taxonomy.py --onet-expanded "C:\Datasets\ONET\db_31_0_csv" --version "O*NET 31.0"
.\.venv\Scripts\python.exe scripts/taxonomy_stats.py
```

Admin users can open **Skills Catalog** for source-specific catalog statistics. See `docs/VERSION_1_4_1_ONET.md`.


UI 1.4.2.4: full-sphere camera framing, improved depth and cinematic motion. See `docs/VERSION_1_4_1_4_HERO.md`.

See `docs/VERSION_1_4_2_VISUAL.md` for the 1.4.2.4 hero refinements.


Version 1.4.2.5: true continuous orbit rendering for the cinematic hero, removing visible orbit breaks while preserving the dark-space UI. See `docs/VERSION_1_4_2_5_TRUE_CONTINUOUS_ORBIT.md`.


Version 1.4.2.6 — faster independent closed orbit rendering, see docs/VERSION_1_4_2_6_PERFORMANCE.md.
