# Version 1.4.1 — Expanded O*NET Import

This update works with the official O*NET 31.0 **CSV** archive that you have already extracted. It does **not** download or bundle the datasets. No synthetic skills are generated.

The original Version 1.4 importer remains available. `--onet-expanded` reads `occupation_data.csv`, `content_model_reference.csv`, `job_titles.csv` (or alternate title file), `essential_skills.csv`, and `knowledge.csv`. The metadata file resolves O*NET element codes to readable names. Missing optional files are skipped; missing `occupation_data.csv` raises an error. Data is merged into SQLite idempotently.

**Note:** O*NET essential skills and knowledge can have several rating/scale records for one element and occupation. These are collapsed into unique occupation-to-skill relationships. The importer does not interpret the numeric rating values as expertise scores. `software_skills.csv` remains available through the existing `--onet` import.

## On Windows PowerShell

Stop Streamlit. Back up the project `data` folder and preserve `.env`, `.venv`, `.git`, uploads and personal resumes during the upgrade.

```powershell
cd C:\Projects\AI-Resume-Analyzer
$onet = 'C:\Datasets\ONET\db_31_0_csv'
Test-Path "$onet\occupation_data.csv"
Get-ChildItem $onet -Filter '*.csv' | Where-Object Name -Match 'essential_skills|knowledge|content_model_reference|job_titles'
.\.venv\Scripts\python.exe scripts/import_taxonomy.py --onet-expanded $onet --version 'O*NET 31.0'
.\.venv\Scripts\python.exe scripts/taxonomy_stats.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

Sign in as an administrator and open **Skills Catalog**. That page shows real imported counts, publishers, relations, aliases and import timestamp. It does not expose stored resumes or applicant data.

## Source and scope

O*NET 31.0: https://www.onetcenter.org/database.html. Respect O*NET licensing and attribution conditions when distributing derivative catalogs. Do not commit downloaded CSVs or personal application databases to GitHub. The expanded importer handles official supplemental O*NET records, but does not claim to support every O*NET table or every job-title synonym.
