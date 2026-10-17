"""Regression tests: title-only and employer-JD assessment modes."""
from app.services.job_matcher import compare_resume_to_job
from app.services.reports import render_html_report, render_pdf_report
from app.database.connection import initialize_database

RESUME = '''DATA ANALYST\nSKILLS: Python SQL Pandas Tableau Power BI Microsoft Excel Data Visualization Statistics\nEXPERIENCE: Created dashboards with Power BI and queried sales data with SQL.\n'''


def _db(tmp_path):
    db_path = tmp_path / 'test.sqlite3'
    initialize_database(db_path)
    return str(db_path)


def test_title_only_is_not_a_two_word_similarity_comparison(tmp_path):
    result = compare_resume_to_job(RESUME, '', job_title='Data Analyst', db_path=_db(tmp_path))
    assert result['analysis_mode'] == 'role-alignment'
    assert result['similarity_score'] is None
    assert result['match_score'] == result['skill_match_score']
    assert all(not result[k] for k in ('matched_required','missing_required','matched_preferred','missing_preferred'))
    assert b'Estimated role alignment' in render_html_report({**result, 'job_title':'Data Analyst'})
    assert b'No employer job description provided' in render_html_report({**result, 'job_title':'Data Analyst'})
    assert render_pdf_report({**result, 'job_title':'Data Analyst'}).startswith(b'%PDF')


def test_explicit_jd_splits_required_and_preferred(tmp_path):
    jd = 'Required skills:\n- Python\n- SQL\nPreferred skills:\n- Tableau\n- Kubernetes'
    result=compare_resume_to_job(RESUME, jd, job_title='Data Analyst', db_path=_db(tmp_path))
    assert result['analysis_mode'] == 'job-description'
    assert result['similarity_score'] is not None
    assert 'Python' in result['matched_required']
    assert 'SQL' in result['matched_required']
    assert 'Tableau' in result['matched_preferred']
    assert 'Kubernetes' in result['missing_preferred']
    html=render_html_report({**result,'job_title':'Data Analyst'})
    assert b'Estimated job compatibility' in html
    assert b'Kubernetes' in html
    assert b'%PDF' == render_pdf_report({**result, 'job_title':'Data Analyst'})[:4]
