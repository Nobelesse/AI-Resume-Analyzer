from app.services.ats_intelligence import resume_readiness, job_compatibility
import pytest
from app.database.connection import initialize_database

@pytest.fixture
def db_path(tmp_path):
    path=tmp_path / "ats.sqlite3"
    initialize_database(path)
    return path

RESUME = """PROFILE
Python developer
SKILLS
Python, SQL, Microsoft Excel
EXPERIENCE
Built Python tools and analyzed SQL data.
EDUCATION
BCA graduate.
"""

def test_independent_resume_readiness(db_path):
    result=resume_readiness(RESUME,db_path=db_path)
    assert 0 <= result['score'] <= 100
    assert result['components']
    assert result['checks']

def test_required_job_matching_and_manual_review(db_path):
    result=job_compatibility(RESUME,"""Required:
- Python
- SQL
- AWS certification
Preferred:
- Tableau""",db_path=db_path)
    assert result['score_available']
    assert result['manual_review_count'] >= 1
    assert result['matched'] >= 1
    assert any(x['status']=='unverified' for x in result['requirements'])

def test_unrecognized_job_requirements_not_falsely_scored(db_path):
    result=job_compatibility(RESUME,'Required:\n- 6 years of medical licensing experience',db_path=db_path)
    assert result['score'] is None
    assert result['manual_review_count'] >= 1

def test_missing_job_description():
    with pytest.raises(ValueError):job_compatibility(RESUME, '  ')
