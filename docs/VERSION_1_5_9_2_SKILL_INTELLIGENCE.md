# Version 1.5.9.2 — Universal Skills Intelligence

Free, offline, reviewed terminology extensions for the curated SQLite `skills` and `skill_aliases` tables. The source is **locally curated aliases**, not an official O*NET or ESCO expansion. Existing O*NET skill and relation counts are unchanged. The imported taxonomy remains separate.

- Shared normalized skills across Career Finder, Job Studio and ATS Intelligence.
- Abbreviations MS Excel/MS Word/PowerBI/Postgres/JS and many others mapped to canonical labels.
- Additional categories include software, data analytics, administration, finance, marketing, health and infrastructure.
- Strict phrase boundaries to reduce false positives; skills absent from a resume are not confirmed missing competencies.
- Alias seed is idempotent. A maintainer can import further reviewed CSV datasets using `app.services.skills.import_skills_csv`.
- No automatic import of unreviewed external datasets or credentials.

Run `python -m pytest -q` and `python scripts/final_audit.py`. No API key is required.
