"""Regression: Career Finder skill lookup must use an indexed reverse link."""
from app.database.connection import connect, initialize_database
from app.services.taxonomy import ensure_tables

def test_reverse_skill_occupation_index_survives_repeat_initialization(tmp_path):
    path = tmp_path / "catalog.sqlite3"
    initialize_database(path)
    with connect(path) as db:
        ensure_tables(db)
        ensure_tables(db)
        indexes = {row[1] for row in db.execute("PRAGMA index_list('tax_links')")}
        assert "idx_tax_links_skill_occ" in indexes
        plan = db.execute(
            "EXPLAIN QUERY PLAN SELECT occupation_id FROM tax_links WHERE skill_id=?", (1,)
        ).fetchall()
        assert any("idx_tax_links_skill_occ" in str(row[3]) for row in plan), plan
