# Version 1.5.7.4 — Resume Evidence Integration

Career Finder now explains suggestions using explicitly stated, career-relevant resume skills and knowledge, separately displaying stated educational background, career interests and fresher status. These explanations complement but do not alter O*NET rankings. An aspiration is not proof of employment, and an educational qualification is not proof of mastery. Analysis remains offline and user-facing screens do not expose the underlying database or AI model.

## Windows install
Extract the ZIP and merge its project directory into `E:\Projects\AI-Resume-Analyzer` after backing up the existing directory. Exclude `.git`, `.venv`, `data`, `.env`, databases, and uploaded resumes. Verify with `python -m pytest -q` and `python scripts/final_audit.py` from the project root.
