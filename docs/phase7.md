# Phase 7 — Dashboard and Data Management

The Phase 7 upgrade extends the existing single-user-machine SQLite system without resetting existing accounts or uploaded documents. Database schema version 5 is idempotent and preserves all previous records.

## Features

- Admin overview counters: registered accounts, resumes, ATS analyses, job matches, skill catalog size and active users.
- Daily resume upload and document-format charts.
- Admin resume list with filename/email and file-format filters, bounded query results and CSV download.
- Admin ability to deactivate/reactivate standard user accounts; admin accounts cannot be disabled from this interface.
- Admin audit log and CSV export. Existing auth, uploads, analyses and comparisons already write some audit entries. Phase 7 adds delete and account-state events.
- User dashboard counters, recent uploads and average ATS-readiness score.
- Users may delete their own resumes; admins may delete any resume. Linked analyses/job comparisons are automatically removed through SQLite cascades. Uploaded original files are unlinked after successful database deletion.
- All access-control checks are performed in database APIs, not just UI navigation. CSV formula-prefixed values are escaped.

## Limitations and local privacy

This is a local development project, not an internet-ready identity service. Admin CSV exports contain applicant metadata and must be handled securely. Database records are not encrypted at rest. Deletes are not secure wipes, and filesystem deletion can fail after a successful database commit (e.g. antivirus lock); backups also retain copies. Ensure offline backups before maintenance. The audit log does not record every document view or contain immutable tamper evidence. Session management remains Streamlit-local, not a production authentication solution.

## Run

From your root folder, `python -m streamlit run app/main.py`. Never use `streamlit run main.py` from the root. Install packages using `python -m pip install -r requirements-dev.txt` and run `python -m pytest -q`.
