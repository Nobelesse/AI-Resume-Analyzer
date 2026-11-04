"""Offline recognition/occupation aliases: deterministic, no model or internet."""
from app.database.connection import initialize_database, connect
from app.services.skills import seed_skills, extract_skills
from app.services.job_matcher import compare_resume_to_job
from app.services.hybrid_intelligence import rank_careers
from app.services.taxonomy import lookup_occupation
from app.services.alias_matching import canonical_key


def test_excel_aliases_and_job_match_consistency(tmp_path):
    db = tmp_path / 'skills.sqlite3'
    initialize_database(db)
    seed_skills(db)
    resume = 'SKILLS: MS Excel, PowerBI, postgres and Python.'
    jd = 'Required Skills:\nMicrosoft Excel\nMicrosoft Power BI\nPostgreSQL'
    result = compare_resume_to_job(resume, jd, db_path=db)
    assert {'Microsoft Excel', 'PostgreSQL'} <= set(result['matched_required'])
    assert canonical_key('Microsoft Power BI') in {canonical_key(x) for x in result['matched_required']}
    assert not result['missing_required']
    assert canonical_key('excel') == canonical_key('MS-Excel') == canonical_key('Microsoft Excel')


def test_occupation_title_variants_resolve_to_imported_role(tmp_path):
    db = tmp_path / 'titles.sqlite3'
    initialize_database(db)
    with connect(db) as conn:
        conn.execute("INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES('ONET','x1','Software Quality Assurance Analysts and Testers','software quality assurance analysts and testers')")
    result=lookup_occupation('QA Tester',db_path=db)
    assert result and result[0]['name'] == 'Software Quality Assurance Analysts and Testers'


def test_career_finder_resolves_alias_to_catalog_skill(tmp_path):
    db = tmp_path / 'careers.sqlite3'
    initialize_database(db)
    with connect(db) as conn:
        occ = conn.execute("INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES('ONET','da','Business Intelligence Analysts','business intelligence analysts')").lastrowid
        for i, name in enumerate(('Microsoft Excel', 'Microsoft Power BI', 'PostgreSQL')):
            sid = conn.execute('INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)', ('ONET',f's{i}',name,name.casefold())).lastrowid
            conn.execute('INSERT INTO tax_links(occupation_id,skill_id,relation) VALUES(?,?,?)',(occ,sid,'essential'))
    result=rank_careers('Data analyst projects: MS Excel, PowerBI and Postgres dashboards.',db_path=db)
    assert result['diagnostics']['catalog_skill_matches'] >= 3
    assert result['jobs'] and result['jobs'][0]['title'] == 'Business Intelligence Analysts'
    assert result['jobs'][0]['matched_skill_count'] >= 3


def test_imported_publisher_alias_is_used_by_career_finder(tmp_path):
    db = tmp_path / 'publisher.sqlite3'
    initialize_database(db)
    with connect(db) as conn:
        occ = conn.execute("INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES('ESCO','o','Database Analysts','database analysts')").lastrowid
        for i, name in enumerate(('Microsoft Excel', 'Power BI', 'PostgreSQL')):
            sid = conn.execute('INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)', ('ESCO',f's{i}',name,name.casefold())).lastrowid
            if i == 0:
                conn.execute("INSERT INTO tax_skill_aliases(source,alias,skill_id) VALUES('ESCO','microsoft excel spreadsheets',?)",(sid,))
            conn.execute('INSERT INTO tax_links(occupation_id,skill_id,relation) VALUES(?,?,?)',(occ,sid,'essential'))
    result=rank_careers('Excel, Power BI and PostgreSQL project experience.',db_path=db)
    assert result['diagnostics']['catalog_skill_matches'] >= 3


def test_not_merging_unrelated_skills():
    assert canonical_key('Java') != canonical_key('JavaScript')
    assert canonical_key('Microsoft Excel') != canonical_key('Google Sheets')
    assert canonical_key('Python') != canonical_key('Pandas')
    assert canonical_key('Apache Spark') != canonical_key('PySpark')
