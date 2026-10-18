# Version 1.5.9.8 — Local Intelligence & Additional Datasets

## What changed

Gemini runtime functions, remote endpoints, status checks and API key settings are removed. Career Finder uses a deterministic local ranking algorithm. Occupation Intelligence can use a local Ollama model when explicitly invoked, and otherwise uses offline data. No paid services.

## Included in this ZIP

`datasets/curated_skills_1598.csv`: local curated vocabulary, not publisher O*NET/ESCO data. Import with:

```powershell
cd 'E:\Projects\AI-Resume-Analyzer'
.\.venv\Scripts\python.exe scripts/import_skills.py datasets/curated_skills_1598.csv
```

This does NOT by itself add new official occupation mappings. Your existing local `data/resume_analyzer.sqlite3` and imported O*NET mappings are preserved.

## Publisher datasets (download separately — not bundled)

- O*NET 31.0 CSV (all tables): https://www.onetcenter.org/database.html
- O*NET software skills CSV: https://www.onetcenter.org/dl_files/database/db_31_0_csv/software_skills.csv
- O*NET essential skills CSV: https://www.onetcenter.org/dl_files/database/db_31_0_csv/essential_skills.csv
- O*NET occupational data CSV: https://www.onetcenter.org/dl_files/database/db_31_0_csv/occupation_data.csv
- ESCO English CSV: https://esco.ec.europa.eu/en/use-esco/download (choose classification / en / csv; ESCO sends a download link after acceptance and email entry).

Refer to the respective data licenses, and check whether files already exist in your original O*NET 31.0 extraction. Do not import untrusted substitute catalog files.

To import O*NET occupation and software links from a directory of CSVs:

```powershell
.\.venv\Scripts\python.exe scripts/import_taxonomy.py --onet 'C:\Datasets\ONET\occupation_data.csv' 'C:\Datasets\ONET\software_skills.csv' --version '31.0'
.\.venv\Scripts\python.exe scripts/import_taxonomy.py --onet-expanded 'C:\Datasets\ONET' --version '31.0'
.\.venv\Scripts\python.exe scripts/taxonomy_stats.py
```

**Important**: import scripts modify your configured SQLite database. Back up `data/` before an import, and run the importer only once or after confirming its idempotency. O*NET occupations describe US jobs and may not cover India-specific qualifications or job requirements. There is no guarantee a downloaded dataset makes ATS scores objectively accurate; benchmark with reviewed examples.
