# Phase 3 security design

- Public registration always creates a `user` account. A unique admin is bootstrapped through a one-time local CLI.
- Argon2id password hashes use unique salts and password policy checks. No plaintext credentials persist.
- Login attempts are throttled per role/email with a 15-minute lock after five failures; this is not IP-aware and is intended for local demonstration.
- Admin-only account directory calls `require_role` on the server before executing SQLite queries.
- SQLite parameter placeholders prevent SQL injection on user input.
- Streamlit session state stores a user ID and inactivity timestamp; each protected operation reloads the role from SQLite.
- This is a local demonstration, not a hardened Internet-facing identity provider. For public deployment use HTTPS, persistent signed session infrastructure, stronger rate limiting and threat-model review.
- SQLite files and uploads are excluded from Git via `.gitignore`; use OS file permissions and disk encryption for private data on shared computers.
