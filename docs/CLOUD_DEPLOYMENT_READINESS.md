# Cloud deployment preparation — AI Resume Analyzer

This branch preserves the **offline** application. The local Cloud working copy runs separately and should use only a *reference-only* catalog export and disposable accounts/documents. A source-only Git archive **does not include** the reference catalog (it is ignored).

## Local preparation (Windows PowerShell)

1. Put the previously verified reference-only export in `data/reference_catalog.sqlite3` in the **Cloud** worktree. Never use your original mixed user+taxonomy SQLite database as input. The preparation tool rejects any source with non-reference tables.
2. From `E:\Projects\AI-Resume-Analyzer-Cloud`, run:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_cloud_database.py
$env:ARA_DATABASE_PATH = "E:\Projects\AI-Resume-Analyzer-Cloud\data\cloud_app.sqlite3"
.\.venv\Scripts\python.exe scripts/cloud_preflight.py
.\.venv\Scripts\python.exe scripts/create_admin.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/main.py --server.port 8502
```

The preparation command intentionally refuses to overwrite an existing `data/cloud_app.sqlite3`. Don't run it against an existing admin database. If you're continuing from the previously tested `cloud_demo.sqlite3`, **keep using that database** and skip database preparation and admin creation.

## Unresolved before real hosted deployment

- **Reference data transport**: the reference-only SQLite catalog is not present in the source ZIP or GitHub; choose a source/packaging method compliant with *all* included publishers' licenses and attribution rules. O*NET 31.0 downloadable data is generally CC BY 4.0 with attribution; check ESCO and any other source separately.
- **Persistent accounts and uploads**: this app currently uses local `sqlite3` and `data/uploads`. Streamlit Community Cloud local disk is not guaranteed to persist across container restarts/redeployments, and multiple instances are not supported by the current file-based state model. Do not advertise real account/CV persistence until the backend has been migrated and tested.
- **Secure administrator provisioning**: creating an admin on your Windows PC does not create an admin in the remote deployment. Do not push administrator records or credentials to GitHub. Plan an explicit server-safe one-time bootstrap with secrets and persistent storage.
- **AI capability**: deterministic catalog matching works without local Ollama in tested functions. LLM-generated outputs will not be available on a standard hosted server without an independently connected AI service. Do not label deterministic answers as model-generated.
- **Privacy**: never upload real resumes or create real user accounts on a throwaway demonstration deployment.

The script and source ZIP are **a local preparation build**, not a production-ready hosted application. The offline version and Windows shortcuts are unchanged.
