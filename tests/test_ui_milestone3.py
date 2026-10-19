"""Admin UI milestone regression guards."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_admin_views_keep_server_side_guards():
    text=(ROOT/'app/pages/management_pages.py').read_text(encoding='utf-8')
    assert "_actor('admin')" in text
    assert 'page_header(' in text
    assert 'admin_resume_select_all' in text
    assert 'admin_delete_resume_bulk' in text
    assert 'admin_delete_resumes(' in text

def test_dashboard_role_and_navigation_stay_protected():
    text=(ROOT/'app/pages/secure_pages.py').read_text(encoding='utf-8')
    assert "_get('admin')" in text
    assert 'navigate(path)' in text

def test_admin_theme_respects_reduced_motion():
    css=(ROOT/'app/assets/styles.css').read_text(encoding='utf-8')
    assert 'UI 1.0 Milestone 3' in css
    assert 'prefers-reduced-motion:reduce' in css
