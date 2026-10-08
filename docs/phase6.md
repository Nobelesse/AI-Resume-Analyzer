# Phase 6: Explainable job matching

- Required versus preferred skills are inferred from job-description headings. Unmarked sections are treated as required. This heuristic may misclassify ambiguous prose.
- User can adjust required-skills weight (50–95%). Absent skill groups are omitted from weighted score.
- Match score combines 70% recognized skill coverage and 30% TF-IDF-like two-document cosine similarity, or pure similarity when no skills are detected.
- Skills are read from the expandable local SQLite catalog; the shipped catalog is a starter, not 10,000 verified skills.
- PDF/HTML reports can be downloaded; HTML output escapes user text.
- Match records contain the original job description, so treat SQLite backups as sensitive.
- Accounts and uploaded files remain in the original local database and uploads folder.
- No LLM, remote job scraping, or automatic hiring recommendation is used.
