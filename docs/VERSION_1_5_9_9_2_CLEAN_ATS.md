# Version 1.5.9.9.2 — Clean ATS Screen and Detailed Reporting

## User-facing behavior
- Advanced ATS Intelligence presents readiness, compatibility, resume quality, matched skills, undetected skills and improvement advice. Line-by-line requirement status, evidence counts and methodology are reserved for its detailed PDF.
- Job Match Studio presents the score, matched skills, skills to improve and role overview. Full requirement-by-requirement data remains accessible from PDF and HTML downloads; it is not rendered as expandable evidence sections on screen.
- A heading such as `Required Skill:` or `Preferred Skills:` is a section heading, not a requirement. Both requirement segmentation and line-level evidence extraction recognize singular and plural heading variants.

## Limits
- The engine extracts named skills from resume text; it does not verify competence, qualification or actual employment. 'Not detected' does not imply a candidate does not possess a skill.
- Rule-based readiness and compatibility estimates are not certified employer ATS outcomes.
- Detailed reports use the assessment result for the selected resume and job description; no external AI or paid service is needed.

## Install and safety
Preserve your `data/`, `datasets/`, `uploads/`, `.env`, `.venv` and `.git` directories when copying the release over an existing installation. Do not reimport O*NET or ESCO merely to install the UI update. Existing SQLite backups should be kept until verification.

## Checks
Run `python -m pytest -q` and `python scripts/final_audit.py` under Python 3.11; verify the two report downloads in your browser.
