# Historical activity log identity (v1.5.9.9.9.8)

- Existing database upgrades automatically on startup; back up the SQLite database before first startup.
- Only the administrator can access Activity Log.
- Each audit event stores actor email and original user ID snapshots; no password, resume contents, or files are stored in audit snapshots.
- Deleting a user preserves historical actor details while cascading account-related personal records.
- Events from accounts deleted before this migration cannot be reliably recovered from the current database if `actor_id` had been nulled. Such records display `[historical identity unavailable]`.
- Displayed actor email is an historical label, not an existing active account.
- If applicable, publish a retention/deletion policy because audit entries retain identifiers after account deletion.
