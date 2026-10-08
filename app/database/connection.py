"""SQLite connectivity and idempotent schema upgrades."""
import sqlite3
from pathlib import Path
from app.config import DATABASE_PATH

SCHEMA_VERSION = 4

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
        from app.services.skills import seed_skills
        seed_skills(path)
        conn.execute(f'PRAGMA user_version={SCHEMA_VERSION}')
