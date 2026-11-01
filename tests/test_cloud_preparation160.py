"""Cloud-only preparation must never import private user tables."""
import sqlite3
from pathlib import Path
import pytest

from app.database.connection import initialize_database
from scripts.prepare_cloud_database import REFERENCE_TABLES, prepare


def _catalog(path: Path):
    with sqlite3.connect(path) as db:
        # Minimal valid reference-only database; the real export has larger counts.
        db.execute('CREATE TABLE tax_occupations(id INTEGER PRIMARY KEY, name TEXT)')
        db.execute('CREATE TABLE tax_skills(id INTEGER PRIMARY KEY, name TEXT)')
        db.execute('CREATE TABLE tax_links(occupation_id INTEGER, skill_id INTEGER, relation TEXT)')
        for table in REFERENCE_TABLES - {'tax_occupations','tax_skills','tax_links'}:
            db.execute(f'CREATE TABLE "{table}" (dummy TEXT)')
        db.execute("INSERT INTO tax_occupations VALUES (1, 'Data Analyst')")
        db.execute("INSERT INTO tax_skills VALUES (1, 'SQL')")
        db.execute("INSERT INTO tax_links VALUES (1, 1, 'essential')")


def test_rejects_private_mixed_database(tmp_path):
    db = tmp_path / 'mixed.sqlite3'
    initialize_database(db)
    target = tmp_path / 'out.sqlite3'
    with pytest.raises(ValueError, match='reference-only'):
        prepare(db, target)
    assert not target.exists()


def test_refuses_overwriting_existing_database(tmp_path):
    src = tmp_path / 'reference.sqlite3'
    _catalog(src)
    dest = tmp_path / 'keep.sqlite3'
    dest.write_bytes(b'DO NOT OVERWRITE')
    with pytest.raises(FileExistsError):
        prepare(src, dest)
    assert dest.read_bytes() == b'DO NOT OVERWRITE'


def test_prepared_catalog_has_no_private_records(tmp_path):
    src = tmp_path / 'reference.sqlite3'
    initialize_database(src)
    with sqlite3.connect(src) as db:
        db.execute("PRAGMA foreign_keys=OFF")
        for t in ('analyses', 'job_matches', 'resumes', 'activity_logs', 'login_throttle', 'users'):
            db.execute(f'DROP TABLE IF EXISTS "{t}"')
        db.execute("INSERT INTO tax_occupations(id,source,source_id,name,normalized) "
                   "VALUES (1,'test','d1','Data Analyst','data analyst')")
        db.execute("INSERT INTO tax_skills(id,source,source_id,name,normalized) "
                   "VALUES (1,'test','s1','SQL','sql')")
        db.execute("INSERT INTO tax_links VALUES (1,1,'essential')")
    dest = tmp_path / 'prepared.sqlite3'
    counts = prepare(src, dest)
    assert counts['tax_links'] == 1
    with sqlite3.connect(dest) as db:
        assert db.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0
        assert db.execute('SELECT COUNT(*) FROM tax_occupations').fetchone()[0] == 1
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
