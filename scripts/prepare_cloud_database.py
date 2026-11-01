"""Prepare a local, isolated Cloud-worktree SQLite DB from reference-only data.

This is a LOCAL preparation utility, not durable storage for hosted users.
Never accepts a source database containing private application tables.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REFERENCE_TABLES = frozenset({
    "skills", "skill_aliases", "tax_occupations", "tax_skills",
    "tax_links", "tax_occupation_aliases", "tax_skill_aliases", "tax_imports",
})
PRIVATE_TABLES = frozenset({
    "users", "resumes", "analyses", "job_matches", "activity_logs", "login_throttle",
})


def _user_tables(db: sqlite3.Connection) -> set[str]:
    return {row[0] for row in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )}


def _verify_reference(db: sqlite3.Connection) -> dict[str, int]:
    tables = _user_tables(db)
    if tables != REFERENCE_TABLES:
        raise ValueError(
            "Source must be a reference-only export with exactly eight tables. "
            f"Missing: {sorted(REFERENCE_TABLES - tables)}; "
            f"unexpected: {sorted(tables - REFERENCE_TABLES)}"
        )
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise ValueError("Source database integrity check failed")
    if db.execute("PRAGMA foreign_key_check").fetchall():
        raise ValueError("Source database foreign-key check failed")
    counts = {t: db.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
              for t in sorted(REFERENCE_TABLES)}
    if any(counts[t] == 0 for t in ("tax_occupations", "tax_skills", "tax_links")):
        raise ValueError("Source reference catalog has no occupations, skills, or links")
    return counts


def prepare(source: Path, destination: Path) -> dict[str, int]:
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if source == destination:
        raise ValueError("Source and destination must be different")
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name + ".creating")
    if temp.exists():
        raise FileExistsError(f"Temporary file already exists: {temp}")

    try:
        with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as src:
            counts = _verify_reference(src)
            with closing(sqlite3.connect(temp)) as dst:
                src.backup(dst)
        # initialize_database uses a SQLite transaction context manager, which
        # commits but does not close the connection. Initialize in a child
        # process so Windows releases its file handle before os.replace().
        bootstrap = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; from app.database.connection import initialize_database; "
                "initialize_database(sys.argv[1])",
                str(temp),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        if bootstrap.returncode:
            raise RuntimeError(
                "Cloud database schema initialization failed:\n"
                + (bootstrap.stderr or bootstrap.stdout).strip()
            )
        with closing(sqlite3.connect(temp)) as db:
            tables = _user_tables(db)
            if not (REFERENCE_TABLES | PRIVATE_TABLES).issubset(tables):
                raise RuntimeError("Expected application and reference tables were not created")
            for table in PRIVATE_TABLES:
                if db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]:
                    raise RuntimeError(f"Private records unexpectedly present in {table}")
            for table, n in counts.items():
                if db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] != n:
                    raise RuntimeError(f"Catalog count changed unexpectedly: {table}")
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("Destination integrity check failed")
            if db.execute("PRAGMA foreign_key_check").fetchall():
                raise RuntimeError("Destination has invalid foreign keys")
        os.replace(temp, destination)
        return counts
    except BaseException:
        # Close all connections before attempting to remove files on Windows.
        try:
            temp.unlink(missing_ok=True)
        except PermissionError:
            # Preserve the original error; a locked temporary file can be
            # inspected and removed once its external handle is released.
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=ROOT / "data" / "reference_catalog.sqlite3")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "cloud_app.sqlite3")
    args = parser.parse_args()
    try:
        counts = prepare(args.reference, args.output)
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
        parser.exit(1, f"Cloud database preparation refused: {exc}\n")
    print("PASS: Reference-only catalog verified and isolated app database initialized")
    for table, count in sorted(counts.items()):
        print(f"{table}: {count:,}")
    print("Database:", args.output.resolve())
    print("NOTE: This file is local and ephemeral when deployed to Streamlit Community Cloud.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
