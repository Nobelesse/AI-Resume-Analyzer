from pathlib import Path
from app.config import APP_VERSION

UI = Path('app/pages/job_pages.py').read_text(encoding='utf-8')
CAREER = UI.split('def career_finder():', 1)[1]


def test_version_1573():
    assert APP_VERSION == '1.5.9.1'


def test_student_ui_has_no_diagnostic_panel_or_provider_branding():
    for internal in ('O*NET matching diagnostics', 'curated-offline-catalog',
                     'gemini_connection_status', 'O*NET query terms',
                     'catalog_skill_matches', "data['source']", 'ai_opt_in',
                     'ranking contributions', 'Catalog coverage'):
        assert internal not in CAREER


def test_career_backend_and_resume_isolation_preserved():
    assert "recommend_careers(record['extracted_text'])" in CAREER
    assert '_career_selection_changed' in CAREER
    assert '_career_current_results' in CAREER
    assert "st.session_state['career_result_identity']" in CAREER


def test_no_false_claims_about_learning_or_eligibility():
    assert 'not confirmed requirements' in CAREER
    assert 'do not verify job eligibility' in CAREER
