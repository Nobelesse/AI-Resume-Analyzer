import re
import pytest
from app.database.connection import initialize_database,connect
from app.database.resumes import save_resume
from app.database.analyses import analyze_resume,get_analysis,list_analyses
from app.auth.service import register_user,create_initial_admin
from app.services.skills import skill_count,extract_skills,import_skills_csv
from app.services.ats import analyze_text

def test_catalog_and_aliases(tmp_path):
    db=tmp_path/'test.db';initialize_database(db)
    assert skill_count(db)>200
    assert {'Python','JavaScript','PostgreSQL'}.issubset(set(extract_skills('Python, JS and postgres',db_path=db)))
    assert 'Java' not in extract_skills('JavaScript',db_path=db)

def test_readiness(tmp_path):
    db=tmp_path/'test.db';initialize_database(db)
    score=analyze_text('Summary\nSkills\nPython SQL\nEducation\nProjects\nExperience\nEmail: x@example.com',db_path=db)
    assert 0<=score['score']<=100
    assert 'Python' in score['skills']
    assert score['sections']['summary']
    assert score['disclaimer']

def test_authorized_analysis_and_history(tmp_path):
    db=tmp_path/'private.db';initialize_database(db)
    a=register_user('a@ex.com','Alice','safe-password-123',db_path=db)
    b=register_user('b@ex.com','Bob','safe-password-123',db_path=db)
    admin=create_initial_admin('admin@ex.com','Boss','safe-password-123',db_path=db)
    rid=save_resume(a,'cv.txt',b'Python SQL data analysis and project management',db_path=db,uploads_dir=tmp_path/'uploads')
    with pytest.raises(PermissionError):analyze_resume(b,rid,db_path=db)
    with pytest.raises(PermissionError):analyze_resume(admin,rid,db_path=db)
    result=analyze_resume(a,rid,db_path=db)
    assert result['analysis_id']
    assert len(list_analyses(a,db_path=db))==1
    with pytest.raises(PermissionError):get_analysis(b,result['analysis_id'],db_path=db)
    assert get_analysis(admin,result['analysis_id'],db_path=db)['score']==result['score']

def test_csv_10000_capacity(tmp_path):
    db=tmp_path/'db.sqlite';initialize_database(db)
    csv=tmp_path/'skills.csv'
    csv.write_text('name,category,aliases\n'+'\n'.join(f'Synthetic Test Skill {i},Tests,STS{i}' for i in range(10001)),encoding='utf8')
    assert import_skills_csv(csv,db_path=db)==10001
    assert skill_count(db)>=10001
    assert 'Synthetic Test Skill 500' in extract_skills('experience in STS500',db_path=db)

def test_routes_unique():
    from pathlib import Path
    urls=re.findall(r'url_path="([^"]+)"',Path('app/main.py').read_text(encoding='utf8'))
    assert len(urls)==len(set(urls))
    assert {'resume-analysis','analysis-history'}.issubset(set(urls))
