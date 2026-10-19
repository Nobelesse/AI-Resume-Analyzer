# Version 1.5.9.9.9.5 — Standard-user permanent deletion

In administrator **Account Management**, select a standard user, then type that account's exact email and acknowledge irreversible deletion. Deletion is restricted by server-side admin permissions and cannot target the permanent admin. SQLite foreign-key cascades remove owned resumes, ATS analyses and job comparisons; stored upload files are removed after the transaction. The action is logged as `admin.user.delete`, without storing the deleted user's email in the audit event. The action is irreversible; take a database backup before use.

Run `python -m pytest -q` and `python scripts/final_audit.py` before upgrading on Windows. The `data/`, `datasets/`, `.venv`, `.env`, `.git` and uploaded resumes in the existing installation must be preserved. Do not run the admin-creation script again when one admin already exists.
