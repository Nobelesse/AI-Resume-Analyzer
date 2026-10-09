"""Phase 6.2: customer care and no-title input regressions."""
from app.database.connection import initialize_database
from app.services.job_matcher import compare_resume_to_job
from app.services.role_skills import suggest_for_title
from app.services.skills import extract_skills, seed_skills

def test_customer_care_title_and_aliases():
    for title in ("Customer Care Executive", "Customer Service Executive", "Senior Customer Care Associate", "Call Centre Executive"):
        result=suggest_for_title(title)
        assert result["skills"], title
        assert "Customer Service" in result["skills"]

def test_customer_care_matches_skills(tmp_path):
    db=tmp_path/'care.db'; initialize_database(db)
    result=compare_resume_to_job('Experienced in Customer Service, CRM, Active Listening and Email Support.', '', job_title='Customer Care Executive', db_path=db)
    assert result['requirements_status']=='title-suggestions'
    assert 'Customer Service' in result['matched_suggested']
    assert result['missing_suggested']

def test_new_customer_service_skills_seed(tmp_path):
    db=tmp_path/'care.db';initialize_database(db);seed_skills(db)
    assert 'Complaint Resolution' in extract_skills('Complaint Resolution and Data Entry',db_path=db)

def test_description_without_title(tmp_path):
    db=tmp_path/'care.db';initialize_database(db)
    result=compare_resume_to_job('Python SQL', 'Required:\nPython\nSQL',job_title='',db_path=db)
    assert 'Python' in result['matched_required']
