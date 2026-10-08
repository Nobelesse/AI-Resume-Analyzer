"""Phase 6.1 regression tests for title-only job matching."""
from app.database.connection import initialize_database
from app.services.job_matcher import compare_resume_to_job
from app.services.role_skills import suggest_for_title, suggest_with_ollama
import pytest


def test_title_only_python(tmp_path):
    db=tmp_path/'r.db';initialize_database(db)
    r=compare_resume_to_job('Python SQL Git Docker FastAPI', '', job_title='Python Developer',db_path=db)
    assert 'Python' in r['suggested_role_skills']
    assert 'Python' in r['matched_suggested']
    assert r['requirements_status']=='title-suggestions'
    assert r['match_score'] > 0


def test_title_only_nontechnical(tmp_path):
    db=tmp_path/'r.db';initialize_database(db)
    r=compare_resume_to_job('I use Excel for accounting and financial reporting.', '', job_title='Accountant',db_path=db)
    assert 'Accounting' in r['suggested_role_skills']
    assert r['requirements_status']=='title-suggestions'


def test_explicit_description_stays_explicit(tmp_path):
    db=tmp_path/'r.db';initialize_database(db)
    r=compare_resume_to_job('Python SQL Docker','Required:\nPython\nSQL\nPreferred:\nDocker',job_title='Python Developer',db_path=db)
    assert r['requirements_status']=='explicit-description'
    assert 'Python' in r['matched_required']
    assert 'Docker' in r['matched_preferred']


def test_unknown_role_not_fake_requirements(tmp_path):
    db=tmp_path/'r.db';initialize_database(db)
    r=compare_resume_to_job('Python SQL', '', job_title='Unfamiliar Space Role',db_path=db)
    assert not r['required_skills']
    assert r['requirements_status']=='unrecognized-role'
    assert r['skill_match_score'] is None


def test_optional_local_ollama_endpoint_safety():
    with pytest.raises(ValueError):
        suggest_with_ollama('Accountant',endpoint='https://example.com')


def test_role_aliases():
    assert suggest_for_title('Senior SDE')['role']=='software engineer'
