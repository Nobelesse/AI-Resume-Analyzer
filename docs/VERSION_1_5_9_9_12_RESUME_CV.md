# Version 1.5.9.9.12 — Resume & CV support

- Select document type on upload. Resumes: **2,000,000 bytes**; CVs: **10,000,000 bytes**.
- Same supported formats: PDF, DOCX, TXT, RTF and ODT. Global Streamlit upload transport limit is 10 MB; Python validation and database constraints enforce the per-type limit.
- Existing rows migrate to `document_type=resume` with record IDs and dependent analyses retained. Migration checks foreign keys and rolls back on failure. **Make an offline database backup before starting this release**.
- User and admin document listings expose type. Existing ATS, Job Match and Career Finder accept documents of both types; no implied automatic understanding of academic publications.
- Parsed text limit remains 350,000 characters and PDF maximum 100 pages. The service does not OCR scanned PDFs.
- 10 MB means 10,000,000 bytes rather than 10 MiB.
