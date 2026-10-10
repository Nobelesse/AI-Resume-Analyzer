# Phase 8 Security Review

Controls verified: server-side role checks for resume reads; admin-only cross-user access; 2 MiB uploads; file extension/content parsing validation; private storage paths; Argon2id password hashing; login throttling; session idle expiry; logout clearing cached career/job results; bounded local Ollama endpoint/model allowlist and response bytes; no sensitive data in Git.

**Remaining limitations**: Local SQLite and raw resume files are not encrypted at rest. Uploaded document parsing is in-process, rather than isolated in an OS sandbox. A desktop-bound Streamlit server is suitable for local academic demonstration, not an internet-facing multi-tenant production service without hardened cookies, CSRF policy review, reverse-proxy HTTPS, stronger rate limiting, resource isolation, and security assessment. Ollama responses are unverified informational suggestions.

**Data handling**: Only fictional/test resumes should be included in screenshots and demonstration. Review staged Git files and public documentation for personally identifiable information. Backups may retain deleted records.
