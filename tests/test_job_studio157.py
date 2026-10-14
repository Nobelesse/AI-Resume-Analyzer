from app.database.connection import initialize_database
from app.services.job_matcher import compare_resume_to_job, requirement_evidence


def test_job_studio157_requirement_evidence(tmp_path):
    db=tmp_path/'sample.db';initialize_database(db)
    jd='Required:\n- Python and SQL\n- AWS architecture certification\nPreferred:\n- Docker\n- Tableau'
    report=compare_resume_to_job('Python, SQL, Docker and FastAPI project',jd,job_title='Data Engineer',db_path=db)
    rows=report['requirement_evidence']
    assert len(rows)==4
    assert rows[0]['priority']=='required' and rows[0]['status']=='evidenced'
    assert rows[1]['priority']=='required' and rows[1]['status']=='unverified'
    assert rows[2]['priority']=='preferred' and rows[2]['status']=='evidenced'
    assert rows[3]['priority']=='preferred' and rows[3]['status']=='not-found'
    assert 'Tableau' in report['missing_preferred']
    assert report['improvement_suggestions']


def test_job_studio157_inline_cues_and_no_hallucination(tmp_path):
    db=tmp_path/'sample.db';initialize_database(db)
    rows=requirement_evidence('Must have Python\nNice to have Tableau\nFive years of verified experience', {'Python'},db_path=db)
    assert rows[0]['priority']=='required' and rows[0]['status']=='evidenced'
    assert rows[1]['priority']=='preferred' and rows[1]['status']=='not-found'
    assert rows[2]['status']=='unverified'


def test_job_studio157_empty_profile_not_perfect(tmp_path):
    db=tmp_path/'sample.db';initialize_database(db)
    report=compare_resume_to_job('Python', 'Required:\n- Registered medical license', job_title='Nurse',db_path=db)
    assert report['requirement_evidence'][0]['status']=='unverified'
    assert any('could not be evaluated' in e for e in report['explanations'])
