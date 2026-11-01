"""PostgreSQL connection settings for a server-side Supabase backend.

No database or key is bundled.  A configured server must receive ARA_PG_DSN
in its environment/secrets.  Do not use this module in the browser.
"""
from __future__ import annotations
import os
from contextlib import contextmanager


def database_dsn() -> str:
    dsn = os.environ.get("ARA_PG_DSN", "").strip()
    if not dsn:
        raise RuntimeError("ARA_PG_DSN is not configured; no hosted DB operation was made")
    if not (dsn.startswith("postgresql://") or dsn.startswith("postgres://")):
        raise ValueError("ARA_PG_DSN must be a PostgreSQL connection URI")
    return dsn


@contextmanager
def postgres_connection(*, readonly=False):
    """Close on both success and failure. Never log the DSN or credentials."""
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(database_dsn(), connect_timeout=15,
                         sslmode="require", row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO ara_cloud, public")
            cursor.execute("SET statement_timeout TO '30s'")
            if readonly:
                cursor.execute("SET TRANSACTION READ ONLY")
        yield conn
