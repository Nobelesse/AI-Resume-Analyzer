"""SQLite connectivity and idempotent schema upgrades."""
import sqlite3
from pathlib import Path
from app.config import DATABASE_PATH

SCHEMA_VERSION = 7

def connect(path=None):
    db_path = Path(path) if path is not None else DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(db_path), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys=ON')
    connection.execute('PRAGMA busy_timeout=10000')
    return connection

def initialize_database(path=None):
    with connect(path) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT NOT NULL UNIQUE COLLATE NOCASE,
          display_name TEXT NOT NULL,
          password_hash TEXT NOT NULL,
          role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
          is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS login_throttle (
          identifier TEXT PRIMARY KEY,
          failure_count INTEGER NOT NULL DEFAULT 0,
          blocked_until INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS activity_logs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
          event TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_activity_actor ON activity_logs(actor_id);
        CREATE TABLE IF NOT EXISTS resumes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          original_filename TEXT NOT NULL,
          storage_name TEXT NOT NULL UNIQUE,
          file_type TEXT NOT NULL CHECK(file_type IN ('pdf','docx','txt','rtf','odt')),
          file_size INTEGER NOT NULL CHECK(file_size > 0 AND file_size <= 2097152),
          sha256 TEXT NOT NULL,
          extracted_text TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_resumes_owner ON resumes(owner_id, id DESC);
        CREATE TABLE IF NOT EXISTS skills (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          normalized TEXT NOT NULL UNIQUE,
          category TEXT NOT NULL,
          source TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
        CREATE TABLE IF NOT EXISTS skill_aliases (
          alias TEXT PRIMARY KEY,
          skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_alias_skill ON skill_aliases(skill_id);
        CREATE TABLE IF NOT EXISTS analyses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
          owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 100),
          result_json TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_analyses_owner ON analyses(owner_id,id DESC);
        CREATE TABLE IF NOT EXISTS job_matches (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
          job_title TEXT NOT NULL,
          job_description TEXT NOT NULL,
          result_json TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_matches_owner ON job_matches(owner_id,id DESC);
        """)
        # Preserve a minimal historical actor identity when users are deleted.
        # Existing rows for accounts already deleted cannot be reconstructed.
        columns = {row['name'] for row in conn.execute('PRAGMA table_info(activity_logs)').fetchall()}
        if 'actor_email_snapshot' not in columns:
            conn.execute('ALTER TABLE activity_logs ADD COLUMN actor_email_snapshot TEXT')
        if 'actor_original_id' not in columns:
            conn.execute('ALTER TABLE activity_logs ADD COLUMN actor_original_id INTEGER')
        conn.execute("""UPDATE activity_logs
            SET actor_email_snapshot=(SELECT email FROM users WHERE users.id=activity_logs.actor_id),
                actor_original_id=actor_id
            WHERE actor_id IS NOT NULL AND (actor_email_snapshot IS NULL OR actor_original_id IS NULL)""")
        conn.executescript("""
        CREATE TRIGGER IF NOT EXISTS ara_audit_actor_snapshot_insert
        AFTER INSERT ON activity_logs WHEN NEW.actor_id IS NOT NULL
        BEGIN
          UPDATE activity_logs SET
            actor_email_snapshot=(SELECT email FROM users WHERE id=NEW.actor_id),
            actor_original_id=NEW.actor_id
          WHERE id=NEW.id;
        END;
        CREATE TRIGGER IF NOT EXISTS ara_audit_snapshot_before_user_delete
        BEFORE DELETE ON users
        BEGIN
          UPDATE activity_logs SET
            actor_email_snapshot=COALESCE(actor_email_snapshot, OLD.email),
            actor_original_id=COALESCE(actor_original_id, OLD.id)
          WHERE actor_id=OLD.id;
        END;
        """)
        from app.services.taxonomy import ensure_tables
        ensure_tables(conn)
        from app.services.skills import seed_skills
        seed_skills(path)
        # Enforce the single, permanent administrator at the SQLite layer.
        # Fail closed if a pre-existing database already has multiple admins;
        # do not silently remove, demote, or overwrite any account.
        count = conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
        if count > 1:
            raise RuntimeError("Multiple administrators detected. Manual review required; no accounts changed.")
        conn.executescript("""
        CREATE TRIGGER IF NOT EXISTS ara_one_admin_insert
        BEFORE INSERT ON users WHEN NEW.role='admin'
          AND EXISTS (SELECT 1 FROM users WHERE role='admin')
        BEGIN SELECT RAISE(ABORT, 'Exactly one administrator is permitted'); END;

        CREATE TRIGGER IF NOT EXISTS ara_one_admin_no_promotion
        BEFORE UPDATE OF role ON users WHEN OLD.role!='admin' AND NEW.role='admin'
        BEGIN SELECT RAISE(ABORT, 'Administrator promotion is disabled'); END;

        CREATE TRIGGER IF NOT EXISTS ara_permanent_admin_no_update
        BEFORE UPDATE ON users WHEN OLD.role='admin'
        BEGIN SELECT RAISE(ABORT, 'Permanent administrator cannot be modified'); END;

        CREATE TRIGGER IF NOT EXISTS ara_permanent_admin_no_delete
        BEFORE DELETE ON users WHEN OLD.role='admin'
        BEGIN SELECT RAISE(ABORT, 'Permanent administrator cannot be deleted'); END;
        """)
        conn.execute(f'PRAGMA user_version={SCHEMA_VERSION}')
