# Version 1.5.9.9 — Unified ESCO + O*NET data integration

No paid API or network call. Local CSV files remain on the user's E: drive; not bundled in this ZIP.

**Required directories:** `datasets/ESCO` containing `skills_en.csv`, `occupations_en.csv`, `occupationSkillRelations_en.csv`; `datasets/ONET` containing `software_skills.csv`, `essential_skills.csv`. Supports nested ESCO extraction directories.

From `E:\Projects\AI-Resume-Analyzer` after installing the ZIP:

```powershell
.\.venv\Scripts\python.exe scripts/import_unified_datasets.py
.\.venv\Scripts\python.exe scripts/import_unified_datasets.py --apply
.\.venv\Scripts\python.exe scripts/final_audit.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

The first command validates headers **without writing anything**. The second creates a timestamped SQLite backup then imports ESCO skills, alternate/hidden labels, occupations and occupation-skill relations and the two O*NET supplemental files. Repeat imports use unique source IDs and do not multiply stored rows. Counts printed by the script report scanned rows, not necessarily newly inserted rows. O*NET `essential_skills.csv` can contain multiple scales per skill; the relationship is de-duplicated by the database. Scaling and skill proficiency are **not** inferred from `Data Value`.

ESCO alternate labels are not guaranteed unique. Short, ambiguous acronyms are excluded from free-text catalog detection, and context-specific false matches must be reviewed before using results as evidence. The additional occupation catalog increases coverage but does not prove job eligibility or proprietary ATS accuracy.

If anything fails during import, preserve the backup and inspect the exception. Imports run in SQLite transactions, while ESCO and O*NET are separate stages. Restore backup with Streamlit stopped if you need a complete rollback. Never commit `data/`, `datasets/ESCO/` or `datasets/ONET/` to GitHub without assessing redistribution and repository size.
