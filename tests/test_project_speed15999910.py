from app.config import APP_VERSION
from app.services.skills import extract_skills
from app.services.taxonomy import detect_catalog_skills
from app.database.connection import initialize_database

def test_release_version():
    assert APP_VERSION == '1.5.9.9.11'

def test_regex_boundary_remains_conservative(tmp_path):
    db = tmp_path / 'fast.sqlite3'
    initialize_database(db)
    assert 'Java' not in extract_skills('JavaScript', db_path=db)
    assert 'Go' not in extract_skills('ongoing', db_path=db)
    assert 'Java' in extract_skills('Java developer', db_path=db)
    assert detect_catalog_skills('No listed abilities here', db_path=db) == []
