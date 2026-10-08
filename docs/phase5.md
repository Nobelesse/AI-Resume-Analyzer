# Phase 5 — Resume Intelligence

- `skills` and `skill_aliases` are indexed SQLite tables; curated starter dataset is seeded on startup.
- CSV importer supports verified data catalogs with 10,000+ entries; capacity is tested with synthetic fixtures, which are NOT deployed as real skills.
- Imported catalogs must be reviewed for accuracy and licensing. CSV schema: `name,category,aliases`; pipe separates aliases.
- Resume extraction matches explicitly stated skill names and aliases only, without asserting skill proficiency.
- Score is an explainable local rubric (sections 35, contact 15, skills 20, substance 15, bullets 10, quantified results 5).
- Only signed-in standard users can analyze resumes they own. Admin users can inspect saved analyses using authorized service functions.
- Existing account and resume records survive the additive schema upgrade.
- Known limits: no semantic embedding model, no OCR, no verified third-party 10k taxonomy bundled, and no claim that the score predicts real ATS outcomes.
