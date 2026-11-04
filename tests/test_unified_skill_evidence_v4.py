"""v4: matching should be identity based, conservative and employer-JD led."""
from app.database.connection import initialize_database
from app.services.job_matcher import compare_resume_to_job
from app.services.alias_matching import canonical_key
from app.services.skill_evidence_v4 import unique_skill_labels


def _db(tmp_path):
    db = tmp_path / 'evidence-v4.sqlite3'
    initialize_database(db)
    return db


def test_duplicate_aliases_count_once(tmp_path):
    jd = 'Required Skills:\n- Python and Python (computer programming)\n- Microsoft Power BI and Power BI\n- Pandas and pandas'
    r = compare_resume_to_job('Python, PowerBI, Pandas', jd, db_path=_db(tmp_path))
    keys = [canonical_key(x) for x in r['required_skills']]
    assert len(keys) == len(set(keys)), r['required_skills']
    assert canonical_key('Power BI') in keys
    assert not r['missing_required']


def test_pivot_hyphen_and_analyst_evidence(tmp_path):
    resume = ('Data Analyst with 2 years of experience. SQL, Python, Microsoft Excel. '
              'Developed Power BI dashboards. Built Excel pivot-table reports. '
              'Presented regional sales trends and identified a revenue gap.')
    jd = ('Required Skills:\n- Data Analysis\n- Data Visualization\n- Pivot Tables\n'
          '- Communicate analytical insights')
    r = compare_resume_to_job(resume, jd, job_title='Data Analyst', db_path=_db(tmp_path))
    assert not r['missing_required'], r['missing_required']
    assert r['skill_match_score'] == 100
    assert r['requirement_coverage_score'] == 100


def test_no_hallucinated_javascript_from_java(tmp_path):
    r = compare_resume_to_job('Java, SQL, Excel', 'Required Skills:\n- JavaScript\n- Java', db_path=_db(tmp_path))
    assert 'JavaScript' in r['missing_required']
    assert 'Java' in r['matched_required']


def test_spreadsheets_task_is_grounded_in_excel(tmp_path):
    r = compare_resume_to_job('Microsoft Excel and basic office reporting',
                              'Required Skills:\n- use spreadsheets software', db_path=_db(tmp_path))
    assert 'use spreadsheets software' in r['matched_required']


def test_unrelated_resume_does_not_fake_analytics_evidence(tmp_path):
    r = compare_resume_to_job('Customer support, Canva, event planning.',
                              'Required Skills:\n- Pivot Tables\n- Data Analysis\n- Python', db_path=_db(tmp_path))
    assert r['missing_required']
    assert r['skill_match_score'] == 0
    assert r['match_score'] == 0


def test_similar_jd_rewrite_no_lexical_score_penalty(tmp_path):
    resume = 'Python SQL Pandas projects. Built reports using Excel and Power BI.'
    db = _db(tmp_path)
    first = compare_resume_to_job(resume, 'Required Skills:\n- SQL\n- Python\n- Power BI', db_path=db)
    second = compare_resume_to_job(resume, 'Essential competencies:\n- SQL for reporting\n- Python for analysis\n- Microsoft Power BI to build useful dashboards', db_path=db)
    assert first['match_score'] == second['match_score'] == 100
    assert first['scoring_methodology'].startswith('70%')


def test_unverified_degree_requirement_is_not_passed(tmp_path):
    r = compare_resume_to_job('Python project',
                              'Required Skills:\n- Python\n- 3+ years of professional experience', db_path=_db(tmp_path))
    assert any(row['status'] == 'unverified' for row in r['requirement_evidence'])
    assert 'manual review' in r['scoring_methodology']


def test_title_only_scoring_remains_separate(tmp_path):
    r = compare_resume_to_job('HTML CSS', '', job_title='Web Developer', db_path=_db(tmp_path))
    assert r['match_score'] == 29
    assert r['requirement_coverage_score'] is None


def test_equivalence_keeps_other_products_distinct():
    assert canonical_key('Microsoft Excel') != canonical_key('Google Sheets')
    assert canonical_key('JavaScript') != canonical_key('Java')
    assert canonical_key('Power BI') != canonical_key('Tableau')
    assert len(unique_skill_labels(['Microsoft Power BI', 'Power BI', 'PowerBI'])) == 1
