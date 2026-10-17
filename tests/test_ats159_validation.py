"""Synthetic rubric sanity checks; not a claim of hiring-prediction validity."""
import pytest
from app.database.connection import initialize_database
from app.services.ats_validation import run_benchmark
from app.services.ats_intelligence import job_compatibility

@pytest.fixture
def db_path(tmp_path):
    path=tmp_path/'ats_159.sqlite3'
    initialize_database(path)
    return path

def test_controlled_benchmark(db_path):
    output=run_benchmark(db_path=db_path)
    assert output['total']>=5
    assert output['passed']==output['total'], output['checks']

def test_absent_explicit_skills_do_not_get_credit(db_path):
    result=job_compatibility('Canva design and content marketing.', 'Required:\n- Python\n- SQL', db_path=db_path)
    assert result['score']==0
    assert result['not_found']==2

def test_certification_not_assumed_from_technology(db_path):
    result=job_compatibility('Used AWS in college projects.', 'Required:\n- AWS certification', db_path=db_path)
    assert result['score'] is None
    assert result['manual_review_count']==1

def test_empty_description_rejected(db_path):
    with pytest.raises(ValueError):
        job_compatibility('Python', '\n ', db_path=db_path)
