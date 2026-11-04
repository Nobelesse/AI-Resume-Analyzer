"""Regression coverage for persisting and revisiting Advanced ATS assessments."""
import json
import pytest
from pathlib import Path

from app.database.connection import initialize_database, connect
from app.database.resumes import save_resume
from app.database.analyses import (
    analyze_advanced_ats, analyze_resume, get_analysis, list_analyses,
)
from app.auth.service import register_user, create_initial_admin


@pytest.fixture
def accounts(tmp_path):
    db = tmp_path / 'ats-history.sqlite3'
    initialize_database(db)
    owner = register_user('owner@example.test', 'Owner', 'test-password-123', db_path=db)
    other = register_user('other@example.test', 'Other', 'test-password-123', db_path=db)
    admin = create_initial_admin('admin@example.test', 'Admin', 'test-password-123', db_path=db)
    text = b'Summary\nPython SQL project work\nSkills\nPython SQL Excel\nEducation\nExperience\nProjects\nemail: owner@example.test\n- Completed three projects'
    resume_id = save_resume(owner, 'sample.txt', text, db_path=db, uploads_dir=tmp_path / 'uploads')
    return db, owner, other, admin, resume_id


def test_advanced_assessment_saves_and_reopens(accounts):
    db, owner, other, admin, resume_id = accounts
    result = analyze_advanced_ats(owner, resume_id, 'Required skills: Python and SQL', db_path=db)
    assert result['format'] == 'advanced_ats_v1'
    assert result['analysis_id'] >= 1
    assert result['readiness']['score'] >= 0
    assert result['compatibility'] is not None
    loaded = get_analysis(owner, result['analysis_id'], db_path=db)
    assert loaded['readiness'] == result['readiness']
    assert loaded['compatibility'] == result['compatibility']
    assert loaded['resume_filename'] == 'sample.txt'
    assert loaded['resume_id'] == resume_id
    assert len(list_analyses(owner, db_path=db)) == 1
    assert not list_analyses(other, db_path=db)
    with connect(db) as conn:
        row=conn.execute('SELECT owner_id,resume_id,score,result_json FROM analyses WHERE id=?',(result['analysis_id'],)).fetchone()
    assert row['owner_id'] == owner and row['resume_id'] == resume_id
    assert row['score'] == result['readiness']['score']
    assert json.loads(row['result_json'])['format'] == 'advanced_ats_v1'


def test_no_jd_and_no_accidental_save(accounts):
    db, owner, other, admin, resume_id=accounts
    assert list_analyses(owner, db_path=db) == []
    result=analyze_advanced_ats(owner, resume_id, db_path=db)
    assert result['compatibility'] is None
    assert result['job_description_provided'] is False
    assert len(list_analyses(owner, db_path=db)) == 1


def test_ownership_protected_and_no_outsider_records(accounts):
    db, owner, other, admin, resume_id=accounts
    with pytest.raises(PermissionError):
        analyze_advanced_ats(other, resume_id, 'Python SQL', db_path=db)
    with pytest.raises(PermissionError):
        analyze_advanced_ats(admin, resume_id, 'Python SQL', db_path=db)
    result=analyze_advanced_ats(owner, resume_id, 'Python SQL', db_path=db)
    with pytest.raises(PermissionError):
        get_analysis(other, result['analysis_id'], db_path=db)
    assert get_analysis(admin, result['analysis_id'], db_path=db)['format']=='advanced_ats_v1'
    assert not list_analyses(other, db_path=db)


def test_invalid_description_does_not_write(accounts):
    db, owner, other, admin, resume_id=accounts
    for description in ('x'*30001, None):
        with pytest.raises(ValueError):
            analyze_advanced_ats(owner,resume_id, description, db_path=db)
    with pytest.raises(ValueError):
        analyze_advanced_ats(owner,999999,'Python',db_path=db)
    assert list_analyses(owner,db_path=db)==[]


def test_legacy_history_preserved_and_delete_cascades(accounts):
    db, owner, other, admin, resume_id=accounts
    legacy=analyze_resume(owner,resume_id,db_path=db)
    advanced=analyze_advanced_ats(owner,resume_id,'Python SQL',db_path=db)
    assert get_analysis(owner,legacy['analysis_id'],db_path=db)['score']==legacy['score']
    assert get_analysis(owner,advanced['analysis_id'],db_path=db)['format']=='advanced_ats_v1'
    assert len(list_analyses(owner,db_path=db))==2
    with connect(db) as conn:
        conn.execute('DELETE FROM resumes WHERE id=?',(resume_id,))
    assert list_analyses(owner,db_path=db)==[]
    with connect(db) as conn:
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_pages_show_both_history_formats():
    source=Path('app/pages/analysis_pages.py').read_text(encoding='utf-8')
    assert "if result.get('format') == 'advanced_ats_v1':" in source
    assert '_show_advanced_ats(result)' in source
    assert '_show(result)' in source
    assert 'analyze_advanced_ats(user[\'id\'],selected,description)' in source
