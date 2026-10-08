import re
from pathlib import Path
import pytest
from app.database.connection import connect,initialize_database
from app.auth.service import register_user,create_initial_admin
from app.database.resumes import save_resume
from app.database.job_matches import save_job_match,list_job_matches,get_job_match
from app.services.job_matcher import compare_resume_to_job,cosine_similarity
from app.services.reports import render_html_report,render_pdf_report

JOB='Required:\nPython\nSQL\nPreferred:\nDocker\nKubernetes and Terraform for deployments.'

def setup(tmp_path):
    db=tmp_path/'db.sqlite';initialize_database(db)
    alice=register_user('alice@example.com','Alice Smith','strong-password-123',db_path=db)
    bob=register_user('bob@example.com','Bob Smith','strong-password-123',db_path=db)
    admin=create_initial_admin('boss@example.com','Administrator','strong-password-123',db_path=db)
    rid=save_resume(alice,'resume.txt',b'Python SQL Docker experienced backend developer with real APIs and cloud systems',db_path=db,uploads_dir=tmp_path/'uploads')
    return db,alice,bob,admin,rid

def test_matching_weighting(tmp_path):
    db,_,_,_,_=setup(tmp_path)
    result=compare_resume_to_job('Python SQL Docker backend experience',JOB,db_path=db)
    assert {'Python','SQL'}<=set(result['matched_required'])
    assert 'Docker' in result['matched_preferred']
    assert 'Kubernetes' in result['missing_preferred']
    assert 0<=result['match_score']<=100

def test_weight_effect(tmp_path):
    db,_,_,_,_=setup(tmp_path)
    low=compare_resume_to_job('Python SQL',JOB,db_path=db,required_weight=.5)
    high=compare_resume_to_job('Python SQL',JOB,db_path=db,required_weight=.95)
    assert high['skill_match_score']>low['skill_match_score']

def test_persistence_and_access(tmp_path):
    db,alice,bob,admin,rid=setup(tmp_path)
    result=save_job_match(alice,rid,'Backend Engineer',JOB,db_path=db)
    assert list_job_matches(alice,db_path=db)[0]['id']==result['match_id']
    assert get_job_match(alice,result['match_id'],db_path=db)['match_score']==result['match_score']
    with pytest.raises(PermissionError):get_job_match(bob,result['match_id'],db_path=db)
    with pytest.raises(PermissionError):save_job_match(bob,rid,'Backend Engineer',JOB,db_path=db)
    with pytest.raises(PermissionError):save_job_match(admin,rid,'Backend Engineer',JOB,db_path=db)
    assert get_job_match(admin,result['match_id'],db_path=db)['job_title']=='Backend Engineer'

def test_validation(tmp_path):
    db,alice,_,_,rid=setup(tmp_path)
    with pytest.raises(ValueError):save_job_match(alice,rid,'X','short',db_path=db)
    with pytest.raises(ValueError):compare_resume_to_job('Python','A'*30001,db_path=db)
    assert cosine_similarity('','test')==0.0

def test_reports_safe(tmp_path):
    db,alice,_,_,rid=setup(tmp_path)
    result=save_job_match(alice,rid,'<script>alert(1)</script>',JOB,db_path=db)
    html=render_html_report(result)
    assert b'&lt;script&gt;' in html
    assert b'<script>' not in html
    assert render_pdf_report(result).startswith(b'%PDF')

def test_unique_pages_and_schema(tmp_path):
    db,_,_,_,_=setup(tmp_path)
    with connect(db) as conn:
        assert conn.execute('PRAGMA user_version').fetchone()[0]==4
    paths=re.findall(r'url_path="([^"]+)"',Path('app/main.py').read_text(encoding='utf8'))
    assert len(paths)==len(set(paths))
    assert {'job-match','job-history'}.issubset(paths)
