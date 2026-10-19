"""Ensure the local-only release does not reintroduce cloud API calls."""
from pathlib import Path
from app.database.connection import initialize_database
from app.services.skills import import_skills_csv, extract_skills
from app.config import APP_VERSION
ROOT = Path(__file__).resolve().parents[1]

def test_version_and_no_gemini_runtime():
    assert APP_VERSION == '1.5.9.9.9'
    for filename in ('app/services/hybrid_intelligence.py', 'app/pages/job_pages.py', '.env.example'):
        source = (ROOT / filename).read_text(encoding='utf-8')
        assert 'ARA_GEMINI_API_KEY' not in source
        assert 'generativelanguage.googleapis.com' not in source

def test_bundled_curated_dataset_import(tmp_path):
    db = tmp_path / 'skills.sqlite3'
    initialize_database(db)
    count = import_skills_csv(ROOT / 'datasets/curated_skills_1598.csv', db_path=db, source='curated-1598')
    assert count > 200
    known = set(extract_skills('MS Excel, PowerBI, Python, and PostgreSQL', db_path=db))
    assert {'Microsoft Excel', 'Power BI', 'Python', 'PostgreSQL'} <= known

def test_no_false_equivalence(tmp_path):
    db = tmp_path / 'skills.sqlite3'
    initialize_database(db)
    import_skills_csv(ROOT / 'datasets/curated_skills_1598.csv', db_path=db, source='curated-1598')
    known = set(extract_skills('JavaScript and customer service', db_path=db))
    assert 'Java' not in known
    assert 'QuickBooks' not in known
