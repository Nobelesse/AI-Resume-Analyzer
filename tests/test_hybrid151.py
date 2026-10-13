from app.database.connection import connect, initialize_database
from app.services.taxonomy import ensure_tables
from app.services.hybrid_intelligence import rank_careers
from app.services.job_matcher import compare_resume_to_job


def _catalog(path):
    initialize_database(path)
    with connect(path) as db:
        ensure_tables(db)
        for k,title in [('dev','Backend Developer'),('tiny','One Skill Role')]:
            db.execute('INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES(?,?,?,?)',('ONET',k,title,title.lower()))
        for skill in ['Python','SQL','Git','React','Docker']:
            db.execute('INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)',('ONET',skill,skill,skill.lower()))
        for title, skills in [('Backend Developer',['Python','SQL','Git','Docker']),('One Skill Role',['Python'])]:
            oid=db.execute('SELECT id FROM tax_occupations WHERE name=?',(title,)).fetchone()[0]
            for skill in skills:
                sid=db.execute('SELECT id FROM tax_skills WHERE name=?',(skill,)).fetchone()[0]
                db.execute('INSERT INTO tax_links VALUES(?,?,?)',(oid,sid,'software'))


def test_evidence_breadth_and_coverage(tmp_path):
    path=tmp_path/'careers.db'; _catalog(path)
    output=rank_careers('Python SQL Git developer projects',db_path=path)
    assert output['jobs'][0]['title']=='Backend Developer'
    assert output['jobs'][0]['matched_skill_count']==3
    assert output['jobs'][0]['catalog_skill_count']==4
    assert output['jobs'][0]['skills_coverage']==75
    assert 'methodology' in output


def test_missing_skill_not_inferred(tmp_path):
    path=tmp_path/'careers.db'; _catalog(path)
    result=rank_careers('Python and SQL',db_path=path)
    job=next(j for j in result['jobs'] if j['title']=='Backend Developer')
    assert 'Docker' in job['skills_not_detected']
    assert 'Docker' not in job['skills_detected']


def test_job_scoring_explains_basis(tmp_path):
    path=tmp_path/'careers.db'; _catalog(path)
    result=compare_resume_to_job('Python SQL Git', 'Required:\nPython\nDocker', db_path=path)
    assert result['scoring_basis']=='employer-stated'
    assert 'Docker' in result['missing_required']
    assert '70%' in result['scoring_methodology']
