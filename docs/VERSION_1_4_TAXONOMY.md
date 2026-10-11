# Version 1.4 — Source-attributed occupational taxonomy

## What ships

A complete SQLite schema and **CSV importer** for official ESCO and O*NET datasets, alias lookup, occupation-to-skill relations, matching integration, and regression tests. **The full published catalog is NOT bundled in this ZIP:** this build environment could not download the official files. Do not claim 10,000 genuine skills have been imported until you run the importer and verify counts.

## Official sources

- ESCO (EU European Commission): https://esco.ec.europa.eu/en/use-esco/download — select English CSV **classification** package. Files generally named `occupations_en.csv`, `skills_en.csv`, and `occupationSkillRelations_en.csv`. Use the exact paths on your machine.
- ESCO CSV specification: https://esco.ec.europa.eu/en/structure-esco-downloadable-datasets
- O*NET 31.0 (U.S. Department of Labor / USDOL/ETA): https://www.onetcenter.org/database.html — choose CSV files: **Occupation Data** and **Software Skills**. This importer intentionally uses technology examples only; it does not pretend they represent every occupational ability.
- O*NET license: https://www.onetcenter.org/license_db.html — CC BY 4.0 with attribution and source/version disclosure; O*NET® is a USDOL/ETA trademark. See licensing exceptions and do not imply endorsement.
- ESCO usage/attribution requirements: consult official source terms when redistributing data.

### Commands (VS Code PowerShell)

Stop Streamlit before bulk import. Run in the project root, with your existing `.venv`:

```powershell
# ESCO: replace each path with your own CSV locations
.\.venv\Scripts\python.exe scripts/import_taxonomy.py --esco "C:\Datasets\ESCO\occupations_en.csv" "C:\Datasets\ESCO\skills_en.csv" "C:\Datasets\ESCO\occupationSkillRelations_en.csv" --version "ESCO official English download"

# Optional O*NET (distinct source and source IDs, does not overwrite ESCO)
.\.venv\Scripts\python.exe scripts/import_taxonomy.py --onet "C:\Datasets\ONET\occupation_data.csv" "C:\Datasets\ONET\software_skills.csv" --version "31.0"

.\.venv\Scripts\python.exe scripts/taxonomy_stats.py
```

The source documents sometimes use download filenames with capitalization/spaces, especially O*NET. Quote them as needed. Import is additive and idempotent by publisher ID; source-specific concepts remain distinct, so totals represent **source rows**, not a deduplicated universal skills count.

## Matching behavior

- Occupation title/alias lookup consults imported official sources first. In the absence of an imported match, the curated role library and automatic local Ollama remain available.
- Skills extraction recognizes imported names and aliases, with punctuation boundaries. It remains **keyword evidence**, not verified proficiency.
- Career recommendations can leverage official role skill relations where imported.
- A title-only match shows occupation skills as **typical taxonomy associations**, not confirmed employer requirements or legal qualifications.

## Limitations

- ESCO and O*NET cover different jurisdictions and have different granularities. Do not equate their skill rows to verified candidate ability.
- Importing source CSVs may include multiple synonyms that represent one concept. Statistics show source records, not unique cross-source skills.
- Very large catalogs increase extraction time; the current matcher runs locally, without cloud services. Future speed work can use lexical automata or FTS tokenization. This release does not guarantee real-time performance on very large inputs.
- No official data was added to git. Store downloaded datasets under a separate private data folder, not the repository.
- Medical, legal and public safety occupations may require licensing and qualifications beyond matching skills.
