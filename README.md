## Version 1.5.9.9.9.2 — Premium 3D globe and layered scroll motion

Overview now uses a transparent same-document canvas globe with perspective-projected rotating mesh and independent scroll motion for the hero layers. See [release and manual visual checks](docs/VERSION_1_5_9_9_9_PREMIUM_GLOBE.md).

## v1.5.9.9.6 — Real 3D Scroll Engine
Browser-driven 3D motion replaces invisible CSS view timelines. See `docs/VERSION_1_5_9_9_5_REAL_SCROLL_ENGINE.md`.

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


Version 1.4.2.7 — faster independent closed orbit rendering, see docs/VERSION_1_4_2_6_PERFORMANCE.md.

Version 1.4.2.8: Dark Abyss theme throughout the app with subtle gold highlights and optimized wider hero orbits. See docs/VERSION_1_4_2_8_DARK_ABYSS.md.

Version 1.4.2.9 — enlarged globe and rings with maintained radial clearance; see `docs/VERSION_1_4_2_9_GLOBE_ORBIT_SCALE.md`.

Version 1.4.3.0 — enlarged globe and both orbits with preserved relative clearance. See `docs/VERSION_1_4_3_0_LARGER_GLOBE.md`.


## Version 1.5.0 — Zero-cost Hybrid Career Intelligence
Offline O*NET/ESCO-ranked Career Finder and deterministic Job Studio by default, no Ollama requirement. No Gemini or other cloud AI dependency. Local Ollama is optional where explicitly supported. See `docs/VERSION_1_5_0_HYBRID_INTELLIGENCE.md`.

Version 1.5.1: evidence-ranked offline careers and transparent JD match methodology. See docs/VERSION_1_5_1_ACCURACY.md.

Version 1.5.2: Career relevance repair with domain-aligned catalog ranking. See docs/VERSION_1_5_2_CAREER_RELEVANCE.md.

Version 1.5.3: fixes stale career results on resume switches; distinguishes evidence ranking from raw skill coverage. See docs/VERSION_1_5_3_CAREER_STATE.md.


Version 1.5.4: occupation-specific score contributions and offline configuration status; see docs/VERSION_1_5_4.md.

Version 1.5.5 — Conservative skill quality and occupational relevance; see docs/VERSION_1_5_5_SKILL_QUALITY.md.

Version 1.5.6: occupation-aware catalog-grounded optional learning topics; see docs/VERSION_1_5_6_LEARNING_PRIORITIES.md.

Version 1.5.7: job description evidence and truthful improvement guidance (docs/VERSION_1_5_7_JOB_STUDIO.md).


Version 1.5.7.1: confidence-aware multi-domain Career Finder filtering. See docs/VERSION_1_5_7_1_RELIABILITY.md.


Version 1.5.7.2 adds verified O*NET aliases and a diagnostic breakdown; see docs/VERSION_1_5_7_2_SKILL_NORMALIZATION.md.


Version 1.5.7.3: simplified professional Career Finder presentation. See docs/VERSION_1_5_7_3_PRESENTATION.md.


Version 1.5.7.4: Career Finder displays role-relevant resume skills and separately identifies education, stated experience level, and career interests; see `docs/VERSION_1_5_7_4.md`.

## Version 1.5.8.1 — Advanced ATS Intelligence

The user-facing Resume Analysis route now offers separate resume-readiness and job-compatibility assessments, each with evidence and limits. A job description is required for a job-specific score. Existing Analysis History remains available. See `docs/VERSION_1_5_8_ADVANCED_ATS.md`.


### v1.5.9 ATS Validation
Adds a privacy-safe synthetic benchmark: `python scripts/ats_validation.py`. Details in `docs/VERSION_1_5_9_ATS_VALIDATION.md`. The model is not benchmark-calibrated to employer ATS systems.


### Version 1.5.9.1
Job Studio distinguishes exploratory title-only role alignment from job-description compatibility. The screen and downloadable reports label the active mode and do not show misleading zero requirement counts when no job description was provided.


Version 1.5.9.2 adds reviewed free offline skill aliases and categories. See `docs/VERSION_1_5_9_2_SKILL_INTELLIGENCE.md`.


### v1.5.9.4 — Global Dark Abyss starfield
The shared theme injects a layered CSS starfield on every guest, user and admin page, including sign-in, registration, dashboard, ATS, career matching and management. Twinkles use CSS opacity animations with no external service, JavaScript timer or extra Streamlit reruns. `prefers-reduced-motion` disables animation. No database migrations are required.


### 1.5.9.4 UI refinement
Borderless floating celestial layout throughout guest/user/admin pages. See `docs/VERSION_1_5_9_4_BORDERLESS_CELESTIAL_UI.md`.

### v1.5.9.6 — Seamless professional UI
Feathered floating hero, PLATFORM navigation, up-to-date privacy/capability pages and accessible CSS scroll depth. See `docs/VERSION_1_5_9_5_PRESENTATION_UI.md`.


## 1.5.9.7 — Native seamless hero correction

The Overview hero is now inline first-party markup, NOT a Streamlit component iframe. This prevents the black iframe backdrop shown in user browser screenshots. Animations use SVG/CSS only; scroll reveal uses CSS view timelines with a reduced-motion fallback. The original hero canvas remains in the repository for prior compatibility but is no longer rendered on Overview.

## Version 1.5.9.9 — Local-only intelligence and datasets

Gemini API support has been removed from executable source code. Analysis uses local, rule-based matching and downloaded O*NET/ESCO catalogs; some occupation features optionally use locally running Ollama. No Google API key or paid cloud AI is needed. See `docs/VERSION_1_5_9_8_LOCAL_DATASETS.md` for source links, installer commands, data limitations and licensing. A locally curated skill vocabulary (`datasets/curated_skills_1598.csv`) is included and can be imported safely with `scripts/import_skills.py`. Official O*NET/ESCO source datasets are NOT in this ZIP; obtain them from publishers using the links in documentation.

Version 1.5.9.9 adds `scripts/import_unified_datasets.py`. See `docs/VERSION_1_5_9_9_UNIFIED_DATASETS.md`.


### Version 1.5.9.9.1 — Sidebar scroll repair
Restores independent vertical scrolling in the Streamlit sidebar so Job Match Studio, AI Career Finder and admin links are reachable on smaller displays. See `docs/VERSION_1_5_9_9_1_SIDEBAR_SCROLL.md`.

### Version 1.5.9.9.3 — Clean ATS screen, detailed reporting

Advanced ATS Intelligence and Job Match Studio now show simple on-screen skill summaries instead of verbose line-level evidence. Downloadable PDF (and Job Studio HTML) reports retain the full requirements and explicit text-based detection details. The job-description parser ignores singular/plural requirement headings such as `Required Skill:`. See `docs/VERSION_1_5_9_9_2_CLEAN_ATS.md`.


## Version 1.5.9.9.3 — Celestial Scroll

Unified lightweight 3D-style scroll reveals for static content across guest, user and admin pages, using CSS view timelines and accessible reduced-motion fallback. No changes to skill databases or matching algorithms. See `docs/VERSION_1_5_9_9_3_CELESTIAL_SCROLL.md`.

## v1.5.9.9.4 — Celestial Spatial Journey
Geometric 3D scroll transformations replace fade reveals. See `docs/VERSION_1_5_9_9_4_SPATIAL_JOURNEY.md`.


### Version 1.5.9.9.8
Cinematic Depth Scroll refines the working scroll engine with visible upright 3D motion; see docs/VERSION_1_5_9_9_8_CINEMATIC_DEPTH.md.


## 1.5.9.9.9.2 globe visibility repair
The Overview hero has a built-in animated SVG fallback. Canvas replaces it only after a successful frame, avoiding an empty hero if JavaScript initialization fails.


## Premium Reference Globe (v1.5.9.9.9.2)
The Overview hero now uses an original, locally bundled transparent globe artwork that matches the approved design reference. It floats and features animated light accents without external requests. This is animated 2.5D artwork, not a true volumetric rotating Earth model. The working scrolling engine and offline datasets are unchanged.


## Version 1.5.9.9.9.3
The Overview now uses a prominent **Your Workspace** heading. The former Experience Center link is renamed **Getting Started**, providing a real guide to the user and administrator workflows rather than a demonstration scene.
