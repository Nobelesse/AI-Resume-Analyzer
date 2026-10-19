# Permanent single administrator — Version 1.5.9.9.9.4

The product supports precisely one administrator created by the interactive first-time setup command. Account Management displays the administrator in the directory as read-only and only exposes activation controls for ordinary users. Registration always creates an ordinary user.

SQLite triggers prevent a second administrator, promotion of a standard user to admin, updates to an existing admin (including name, email, password, role and active status), and deletion of the admin. These safeguards apply even if future application code accidentally attempts an unsupported operation. The initial admin bootstrap is permitted when the database contains no administrator. Existing administrators are retained without changes; databases containing more than one admin require manual review.

**Warning:** The administrator account is deliberately immutable, including its password. Store the credentials securely before enabling this policy; losing them requires an explicitly authorized recovery procedure and is not addressed by this release. Back up the private database before installation. This is application-level protection, not a defense against an attacker who has full write access to the SQLite file.

## First setup on Windows

```powershell
cd "E:\Projects\AI-Resume-Analyzer"
.\.venv\Scripts\python.exe scripts/create_admin.py
```

If an administrator already exists the setup refuses a replacement. Do not delete or replace an existing database. **Never publish** `.env`, `data/`, `datasets/`, or resume uploads.
