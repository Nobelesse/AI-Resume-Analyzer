# Phase 9 — Supabase/PostgreSQL integration foundation

**Status:** Foundation only. Do not deploy as a fully persistent app yet.

## Confirmed architecture

Offline `main` continues using its existing SQLite backend and Ollama. The
`cloud-deploy` branch now contains an isolated, fail-closed PostgreSQL schema,
private-storage client, and reference-only catalog import. **The Streamlit
pages still call the SQLite persistence modules**. A future phase must port
those modules (auth, database, admin, reports) and verify production behavior.

## Safety

- **Never** upload the local `cloud_demo.sqlite3`, source `resume_analyzer.sqlite3`,
  uploaded files, passwords, Supabase keys, or `.env` files to Git.
- `ARA_SUPABASE_SERVICE_KEY` is a **server-side secret** with privileged bucket
  access. It must never appear in Streamlit HTML, JS or logs.
- Keep `resume-documents` private and enforce ownership before any file read or delete.
- Database writes in `ara_cloud` must occur only via the server-side PostgreSQL
  connection and a trusted credential. Do not grant `anon` or `authenticated`
  roles this schema, and do not add `ara_cloud` to exposed PostgREST schemas.
- O*NET/ESCO reference-only data remains excluded from Git. Check exact data
  publishers' licensing/attribution before any upload or redistribution.
- Session pooler port 5432. Passwords are prompted (never in command arguments).
- The connection code currently uses `sslmode=require`, which encrypts the
  session but does **not** authenticate the server's certificate chain. Before
  deploying, configure certificate validation (`verify-full`) against the
  supported Supabase CA / connection type.

## Step A — Inspect locally, no server writes

```powershell
cd 'E:\Projects\AI-Resume-Analyzer-Cloud'
.\.venv\Scripts\python.exe scripts/cloud_pg_setup.py --catalog data/reference_catalog.sqlite3
.\.venv\Scripts\python.exe -m pytest -q
```

## Step B — Optional schema installation on an EMPTY Supabase project

Only if you intend to begin remote integration testing: review
`app/cloud/schema.sql` first. On your computer, run:

```powershell
.\.venv\Scripts\python.exe scripts/cloud_pg_setup.py --schema --apply
```

The script requests an explicit `APPLY` confirmation and securely prompts for
the pooler host, user and password. It creates the `ara_cloud` schema and
empty tables. This is **not** yet a running online application.

## Step C — Optional reference catalog import, after license review

```powershell
.\.venv\Scripts\python.exe scripts/cloud_pg_setup.py --catalog data/reference_catalog.sqlite3 --apply
```

This requires the schema from Step B. It rejects mixed/private SQLite source
files and non-empty target reference tables. It is transactional, checks row
counts, and does not copy users or resumes. The import has NOT been tested
against the user's live Supabase instance and must be considered experimental
until verified with read-only queries and rollback/resume handling.

## To complete the cloud deployment

1. Wire **every** Streamlit data operation to PostgreSQL in cloud mode,
   retaining SQLite behavior on `main`.
2. Use the private storage client from server-side paths only. Implement
   deletion reconciliation and authorization, and test interrupted uploads.
3. Provision the single administrator with the existing password hashing and
   audit safeguards, then test all user/admin workflows on PostgreSQL.
4. Make the dashboard and taxonomy queries PostgreSQL compatible; validate
   offline fallback with the catalog, without relying on Ollama.
5. Configure Streamlit secrets for DB and storage credentials; verify TLS
   certificate and least-privilege permissions.
6. Test migrations, concurrency, persistence after restart, security,
   2 MB/10 MB document rules, 262+ regression tests, and actual live hosting.

Keep the existing `cloud_demo.sqlite3` for local demonstrations. Do not
attempt to use it as persistent Streamlit Community Cloud storage.
