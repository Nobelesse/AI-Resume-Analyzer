"""One-time, prompted Supabase/PostgreSQL setup; never stores credentials.

Run only against a newly created private project. Requires --apply to write.
This tool DOES NOT switch the Streamlit app to PostgreSQL.
"""
from __future__ import annotations
import argparse
import getpass
import sqlite3
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'app' / 'cloud' / 'schema.sql'
TABLES = (
    'skills','skill_aliases','tax_occupations','tax_skills','tax_links',
    'tax_occupation_aliases','tax_skill_aliases','tax_imports',
)
# Dependency order must remain as above.
EXPECTED_COLUMNS = {
 'skills': ('id','name','normalized','category','source'),
 'skill_aliases': ('alias','skill_id'),
 'tax_occupations': ('id','source','source_id','name','normalized'),
 'tax_skills': ('id','source','source_id','name','normalized'),
 'tax_links': ('occupation_id','skill_id','relation'),
 'tax_occupation_aliases': ('source','alias','occupation_id'),
 'tax_skill_aliases': ('source','alias','skill_id'),
 'tax_imports': ('source','version','imported_at'),
}


def inspect_reference(path: Path) -> dict[str, int]:
    """Reject any reference file containing accounts, extra tables, or bad FKs."""
    if not path.is_file():
        raise FileNotFoundError('Reference-only local catalog does not exist')
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        tables = {row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if tables != set(TABLES):
            raise ValueError('Source must contain exactly the eight reference tables; no private data')
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Invalid SQLite reference database')
        if db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Reference database has invalid relations')
        for table, expected in EXPECTED_COLUMNS.items():
            actual = tuple(r[1] for r in db.execute(f'PRAGMA table_info("{table}")'))
            if actual != expected:
                raise ValueError(f'Unexpected catalog schema for {table}')
        counts = {table: db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                  for table in TABLES}
        if not all(counts[t] > 0 for t in ('tax_occupations','tax_skills','tax_links')):
            raise ValueError('Incomplete reference catalog')
        return counts


def _connect_prompted():
    import psycopg
    print('Enter only the Session pooler hostname and username (not the full URI).')
    host = input('Supabase session-pooler hostname: ').strip()
    username = input('Database username (postgres.PROJECT_REF): ').strip()
    password = getpass.getpass('Database password (hidden): ')
    if not host.endswith('.pooler.supabase.com') or '/' in host or ':' in host:
        raise ValueError('Invalid Supabase Session pooler hostname')
    if not username.startswith('postgres.'):
        raise ValueError('Expected a Supabase session-pooler username')
    try:
        return psycopg.connect(host=host, port=5432, dbname='postgres', user=username,
                               password=password, sslmode='require', connect_timeout=15)
    finally:
        password = None


def apply_schema():
    with _connect_prompted() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA.read_text(encoding='utf-8'))
        conn.commit()
    print('PASS: ara_cloud PostgreSQL schema installed (no admin or data imported)')


def import_catalog(reference: Path):
    from psycopg import sql
    counts = inspect_reference(reference)
    with _connect_prompted() as pg:
        with closing(sqlite3.connect(reference.as_uri() + '?mode=ro', uri=True)) as src:
            with pg.cursor() as dest:
                dest.execute('SET search_path TO ara_cloud, public')
                # Refuse partial/duplicate imports rather than overriding existing data.
                for table in TABLES:
                    dest.execute(sql.SQL('SELECT COUNT(*) FROM {}').format(sql.Identifier(table)))
                    if dest.fetchone()[0]:
                        raise RuntimeError(f'{table} already contains data; import refused')
                for table in TABLES:
                    columns = EXPECTED_COLUMNS[table]
                    quoted = sql.SQL(',').join(sql.Identifier(c) for c in columns)
                    statement = sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                        sql.Identifier(table), quoted, sql.SQL(',').join(sql.Placeholder() for _ in columns))
                    cursor = src.execute(f'SELECT * FROM "{table}"')
                    total = 0
                    while (rows := cursor.fetchmany(1000)):
                        dest.executemany(statement, rows)
                        total += len(rows)
                    if total != counts[table]:
                        raise RuntimeError(f'Partial import for {table}')
                    print(f'{table}: {total:,}')
                for table in ('skills','tax_occupations','tax_skills'):
                    dest.execute(sql.SQL("SELECT setval(pg_get_serial_sequence(%s, 'id'), COALESCE(MAX(id),1), MAX(id) IS NOT NULL) FROM {}")
                                 .format(sql.Identifier(table)), (f'ara_cloud.{table}',))
                for table in TABLES:
                    dest.execute(sql.SQL('SELECT COUNT(*) FROM {}').format(sql.Identifier(table)))
                    assert dest.fetchone()[0] == counts[table]
        pg.commit()
    print('PASS: Reference-only catalog transferred to Supabase. No private accounts copied.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schema', action='store_true', help='Install idempotent schema')
    parser.add_argument('--catalog', type=Path, help='Import verified local reference-only SQLite file')
    parser.add_argument('--apply', action='store_true', help='Actually contact and modify Supabase')
    args = parser.parse_args()
    if not args.schema and args.catalog is None:
        parser.error('Choose --schema or --catalog')
    if args.catalog is not None:
        counts = inspect_reference(args.catalog.resolve())
        print('Reference-only catalog verified:')
        for table, count in counts.items():
            print(f'  {table}: {count:,}')
        print('Before remote import, confirm publisher licenses and required attribution.')
    if not args.apply:
        print('DRY RUN: No remote data changed. Use --apply only when ready.')
        return
    if input('Type APPLY to allow modifications to your Supabase project: ').strip() != 'APPLY':
        raise SystemExit('Cancelled')
    if args.schema:
        apply_schema()
    if args.catalog is not None:
        import_catalog(args.catalog.resolve())


if __name__ == '__main__':
    main()
