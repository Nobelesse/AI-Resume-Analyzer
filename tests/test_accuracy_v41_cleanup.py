"""Offline v4.1 regression checks: keep distinct skills, skip JD headings."""
from app.database.connection import initialize_database
from app.services.alias_matching import canonical_key
from app.services.job_matcher import compare_resume_to_job
from app.services.role_skills import suggest_for_title
from app.services.skill_evidence_v4 import unique_skill_labels


def _db(tmp_path):
    path = tmp_path / 'v41.sqlite3'
    initialize_database(path)
    return path


def test_python_catalog_name_deduplicates():
    assert canonical_key('Python (computer programming)') == canonical_key('Python')
    assert unique_skill_labels(['Python', 'Python (computer programming)']) == ['Python']
    assert canonical_key('JavaScript') != canonical_key('Java')


def test_generic_google_removed_but_specific_products_remain():
    assert unique_skill_labels(['Google', 'Google Analytics', 'Google Ads']) == ['Google Ads', 'Google Analytics']
    assert canonical_key('Google Ads') != canonical_key('Google Analytics')


def test_jd_section_headings_not_manually_reviewed(tmp_path):
    jd = ('Required Skills:\n- SQL\n- Power BI\nPreferred Skills:\n- Tableau\n'
          'Experience:\n- 1-3 years of analytics experience\nResponsibilities:\n'
          '- Build dashboards for management reporting')
    result = compare_resume_to_job('SQL, Power BI and Tableau. Built dashboards.', jd, db_path=_db(tmp_path))
    statements = [r['text'] for r in result['requirement_evidence']]
    assert 'Required Skills:' not in statements
    assert 'Preferred Skills:' not in statements
    assert 'Experience:' not in statements
    assert 'Responsibilities:' not in statements
    assert any('years' in text for text in statements)
    assert all('Required Skills:' not in suggestion for suggestion in result['improvement_suggestions'])
    assert 'Tableau' in result['preferred_skills']


def test_marketing_coordinator_known_offline_without_catalog(tmp_path):
    role = suggest_for_title('Marketing Coordinator', db_path=_db(tmp_path))
    assert role['source'] == 'curated-role-library'
    assert {'Content Marketing', 'Social Media Marketing', 'Google Analytics'} <= set(role['skills'])
    actual = compare_resume_to_job('Canva, Google Analytics, SEO, Social Media Marketing', '',
                                   job_title='Marketing Coordinator', db_path=_db(tmp_path))
    assert actual['requirements_status'] == 'title-suggestions'
    assert actual['match_score'] is not None


def test_no_automatic_transfer_from_google_analytics_to_google_ads(tmp_path):
    result = compare_resume_to_job('Google Analytics reports',
                                   'Required Skills:\n- Google Analytics\n- Google Ads', db_path=_db(tmp_path))
    assert 'Google Analytics' in result['matched_required']
    assert 'Google Ads' in result['missing_required']
