# v1.5.0 — Zero-budget Hybrid Career Intelligence

The core experience operates offline with the existing skills catalog, SQLite and imported official O*NET/ESCO occupation links. Imported files are **not packaged**: keep your existing `data/` database.

**Career Finder** now ranks roles using evidence of extracted resume skills and O*NET/ESCO occupation associations, with deterministic coverage and explicit source labeling. If no imported catalog exists, it falls back to curated roles.

**Job Studio** uses explicit role requirements, local skills and TF-IDF job similarity; no Ollama process is required. **ATS readiness** remains a separate transparent formatting/skill-evidence heuristic, not a vendor ATS score.

**Optional Gemini** guidance is opt-in; the client requires an API key and sends only shortlisted career titles with matched/missing skills, not full resume text. Free-tier quota/eligibility varies by region and model and may change. No Gemini call is required to use the product; Google may process supplied information.

For a zero-budget Windows run, create/activate your original `.venv`, use your existing `data/` and `python -m streamlit run app/main.py`. Optional AI: set `ARA_GEMINI_API_KEY` in your Windows process environment, do **not** paste into source control.

Scoring limitations: skill mention does not prove mastery, licensing/education are not checked, and no score predicts hiring. API suggestions are not verified facts.
