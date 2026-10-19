import tempfile
import gc
from pathlib import Path
from app.database.connection import initialize_database
from app.services.skills import extract_skills, seed_skills
from app.services.job_matcher import compare_resume_to_job
from app.services.ats_intelligence import job_compatibility
from app.services.skill_intelligence import phrase_present


def _db():
    t=tempfile.TemporaryDirectory()
    path=Path(t.name)/'test.sqlite3'
    initialize_database(path)
    seed_skills(path)
    return t,path


def test_aliases_and_false_positives():
    t,path=_db()
    try:
        got=set(extract_skills('MS Excel, MS Word, PowerBI, Postgres, HTML and CSS',db_path=path))
        assert {'Microsoft Excel','Microsoft Word','Power BI','PostgreSQL','HTML','CSS'} <= got
        assert 'Java' not in extract_skills('JavaScript developer',db_path=path)
        assert 'Go' not in extract_skills('ongoing communication',db_path=path)
        assert 'Customer service and support software' not in extract_skills('Customer service',db_path=path)
        assert 'Bookkeeping software' not in extract_skills('Bookkeeping',db_path=path)
    finally:
        gc.collect()
        t.cleanup()


def test_jobstudio_ats_use_same_aliases():
    t,path=_db()
    try:
        resume='Used MS Excel, PowerBI and Postgres for analytics dashboards.'
        jd='Required Skills:\n- Microsoft Excel\n- Power BI\n- PostgreSQL'
        match=compare_resume_to_job(resume,jd,db_path=path)
        assert {'Microsoft Excel','Power BI','PostgreSQL'} <= set(match['matched_required'])
        ats=job_compatibility(resume,jd,db_path=path)
        assert ats['matched'] >= 3
    finally:
        gc.collect()
        t.cleanup()


def test_prefixes_do_not_imply_skills():
    assert not phrase_present('JavaScript', 'Java')
    assert not phrase_present('ongoing', 'go')
    assert not phrase_present('WordPress', 'word')
