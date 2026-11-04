"""Regression: web-fresher realistic title alignment and consistent core evidence."""
from app.database.connection import connect, initialize_database
from app.services.job_matcher import compare_resume_to_job
from app.services.hybrid_intelligence import rank_careers
from app.services.role_profiles import core_skills

RESUME = ("OBJECTIVE: accounting communication customer service. "
          "SKILLS HTML CSS basic MS Excel MS Word basic accounting bookkeeping. "
          "BCA MCA ongoing Fresher.")


def test_web_title_only_uses_reviewed_core_even_with_large_import(tmp_path):
    path=tmp_path/'web.sqlite3'; initialize_database(path)
    with connect(path) as db:
        oid=db.execute("INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES('ONET','web','Web Developers','web developers')").lastrowid
        for i in range(90):
            skill=f'Unrelated software package {i:03}'
            sid=db.execute('INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)',('ONET',str(i),skill,skill.casefold())).lastrowid
            db.execute('INSERT INTO tax_links VALUES(?,?,?)',(oid,sid,'software'))
        for i,skill in enumerate(('Hypertext markup language HTML','Cascading style sheets CSS'),100):
            sid=db.execute('INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)',('ONET',str(i),skill,skill.casefold())).lastrowid
            db.execute('INSERT INTO tax_links VALUES(?,?,?)',(oid,sid,'essential'))
    r=compare_resume_to_job(RESUME,'',job_title='Web Developer',db_path=path)
    assert r['analysis_mode']=='role-alignment'
    assert r['inference_source']=='curated-role-core'
    assert set(r['matched_suggested'])=={'HTML','CSS'}
    assert {'JavaScript','Git'} <= set(r['missing_suggested'])
    assert 20<=r['match_score']<=40
    assert len(r['suggested_role_skills'])==len(core_skills('web developer'))
    career=rank_careers(RESUME,db_path=path)
    web=next(item for item in career['jobs'] if item['title']=='Web Developers')
    assert 'HTML' in web['core_skills_matched'] and 'CSS' in web['core_skills_matched']
    assert web['core_skill_coverage']==r['match_score'] or abs(web['core_skill_coverage']-r['match_score'])<=1


def test_unknown_catalog_role_not_overridden(tmp_path):
    path=tmp_path/'other.sqlite3';initialize_database(path)
    with connect(path) as db:
        oid=db.execute("INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES('ESCO','some','Laser Engineer','laser engineer')").lastrowid
        sid=db.execute("INSERT INTO tax_skills(source,source_id,name,normalized) VALUES('ESCO','laser','Laser Alignment','laser alignment')").lastrowid
        db.execute('INSERT INTO tax_links VALUES(?,?,?)',(oid,sid,'essential'))
    r=compare_resume_to_job('Laser Alignment','',job_title='Laser Engineer',db_path=path)
    assert r['match_score']==100 and r['inference_source']=='ESCO-imported'


def test_explicit_jd_keeps_its_own_requirements(tmp_path):
    path=tmp_path/'jd.sqlite3';initialize_database(path)
    r=compare_resume_to_job(RESUME,'Required skills:\nHTML\nCSS\nJavaScript',job_title='Web Developer',db_path=path)
    assert r['analysis_mode']=='job-description'
    assert set(r['matched_required'])=={'HTML','CSS'}
    assert 'JavaScript' in r['missing_required']


def test_unrelated_java_not_equivalent_to_javascript(tmp_path):
    path=tmp_path/'java.sqlite3';initialize_database(path)
    r=compare_resume_to_job('Java developer','',job_title='Web Developer',db_path=path)
    assert 'JavaScript' not in r['matched_suggested']
