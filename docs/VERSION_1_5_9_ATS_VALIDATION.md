# Version 1.5.9 — ATS quality validation

This release adds a **reproducible synthetic validation harness** for the existing ATS-readiness and job-compatibility rules. It deliberately does not claim official ATS accuracy or calibrate to a third-party vendor.

Run `python scripts/ats_validation.py` to test contrasting backend and marketing profiles, known skill gaps, manual-review credentials, and explainability. Run `python -m pytest -q` and `python scripts/final_audit.py`.

## Findings and limitations
- Resume Readiness scores are deterministic text heuristics; they do not inspect original PDF reading order or graphical structure.
- Job Compatibility is a description-specific evidence estimate. Certification, years of experience and education remain manual review.
- A benchmark on synthetic examples tests invariants, **not** recruiter agreement or hiring outcomes.
- No real resumes or identifying information are bundled.
- The next validation step requires independently reviewed, consented and redacted resume–job pairs with recorded reviewer labels and disagreement analysis.

## E: drive upgrade
Unzip into a temporary location, back up `E:\Projects\AI-Resume-Analyzer`, merge excluding `.git`, `.venv`, `data`, `.env`, and local DBs. Run the validation script and full test suite before committing.
