"""Read-only audit of a Cloud-worktree DB. Does not expose records or credentials."""
from __future__ import annotations
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import DATABASE_PATH


def main() -> int:
    print("Cloud source:", ROOT)
    print("Configured DB:", DATABASE_PATH)
    if not DATABASE_PATH.is_relative_to(ROOT):
        print("FAIL: Database is outside the Cloud worktree")
        return 1
    if not DATABASE_PATH.is_file():
        print("FAIL: App database not found. Run scripts/prepare_cloud_database.py first.")
        return 1
    with sqlite3.connect(DATABASE_PATH.as_uri() + "?mode=ro", uri=True) as db:
        try:
            values = {t: db.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
                      for t in ("tax_occupations", "tax_skills", "tax_links")}
            admins = db.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
        except sqlite3.Error as exc:
            print("FAIL: Incomplete Cloud database:", exc)
            return 1
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            print("FAIL: Database integrity check")
            return 1
    for key, n in values.items():
        print(f"{key}: {n:,}")
    print("Admin count:", admins)
    if not all(values.values()):
        print("FAIL: Empty reference catalog")
        return 1
    print("PASS: Local Cloud-worktree database preflight")
    print("WARNING: SQLite and uploaded files are NOT durable on Community Cloud.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
