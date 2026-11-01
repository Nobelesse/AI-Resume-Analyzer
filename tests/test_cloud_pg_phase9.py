"""Non-network tests for Phase 9 backend foundations."""
import sqlite3
from pathlib import Path
import pytest
from app.cloud import postgres, storage
from scripts.cloud_pg_setup import inspect_reference, EXPECTED_COLUMNS


def test_postgres_requires_explicit_secret(monkeypatch):
    monkeypatch.delenv('ARA_PG_DSN', raising=False)
    with pytest.raises(RuntimeError, match='not configured'):
        postgres.database_dsn()
    monkeypatch.setenv('ARA_PG_DSN', 'sqlite:///wrong')
    with pytest.raises(ValueError):
        postgres.database_dsn()


def test_storage_requires_private_key(monkeypatch):
    monkeypatch.delenv('ARA_SUPABASE_SERVICE_KEY', raising=False)
    monkeypatch.setenv('ARA_SUPABASE_URL', 'https://example.supabase.co')
    with pytest.raises(storage.StorageError):
        storage.get_private('a' * 32 + '.pdf')


def test_storage_rejects_unsafe_object_names():
    for bad in ('../users.sqlite3','user.pdf','a'*32+'.exe','/etc/passwd'):
        with pytest.raises(ValueError):
            storage._object_path(bad)
    assert storage._object_path('a'*32+'.pdf') == 'a'*32+'.pdf'


def test_storage_rejects_invalid_data_before_network():
    with pytest.raises(ValueError):
        storage.put_private('a'*32+'.pdf', b'', 'application/pdf')
    with pytest.raises(ValueError):
        storage.put_private('a'*32+'.pdf', b'%PDF', 'image/png')


def test_catalog_inspection_fails_closed_for_extra_tables(tmp_path):
    path = tmp_path / 'catalog.sqlite3'
    with sqlite3.connect(path) as db:
        for table, cols in EXPECTED_COLUMNS.items():
            db.execute(f'CREATE TABLE "{table}" (' + ', '.join(f'"{col}" TEXT' for col in cols) + ')')
        db.execute('CREATE TABLE users (password_hash TEXT)')
    with pytest.raises(ValueError, match='exactly the eight'):
        inspect_reference(path)


def test_sql_schema_guards_administrator():
    ddl = (Path(__file__).parents[1] / 'app/cloud/schema.sql').read_text()
    assert 'CREATE UNIQUE INDEX IF NOT EXISTS ara_one_admin' in ddl
    assert 'Permanent administrator cannot be deleted' in ddl
    assert 'Administrator promotion is disabled' in ddl
    assert 'REVOKE ALL ON SCHEMA ara_cloud FROM PUBLIC' in ddl
