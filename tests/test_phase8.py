"""Phase 8 security and integration checks."""
import io
import json
import pytest
from app.services.resume_parser import extract_resume, ResumeValidationError
from app.services.ollama_client import _clean_json, clean_strings, health_check, generate_json, LocalAIError
from app.auth.service import register_user, create_initial_admin
from app.auth.permissions import AccessDenied
from app.database.connection import initialize_database
from app.database.resumes import save_resume, get_resume
from scripts.final_audit import audit

def test_final_audit():
    assert audit() == 0

def test_ollama_json_validation():
    assert _clean_json('```json\n{"skills":["Python"]}\n```')['skills'] == ['Python']
    with pytest.raises(LocalAIError): _clean_json('not JSON')
    assert clean_strings(['Python','python','SQL',123]) == ['Python','SQL']

def test_local_model_allowlist():
    with pytest.raises(ValueError): generate_json('x',model='unsafe-model')

def test_ollama_healthcheck_graceful(monkeypatch):
    import urllib.request
    def fail(*args,**kwargs): raise OSError('offline')
    monkeypatch.setattr(urllib.request,'urlopen',fail)
    assert health_check()['available'] is False

def test_owner_isolation_and_admin_access(tmp_path):
    db=tmp_path/'db.sqlite3'
    initialize_database(db)
    alice=register_user('a@example.com','Alice Jones','VeryStrongPassword123!',db_path=db)
    bob=register_user('b@example.com','Robert James','VeryStrongPassword123!',db_path=db)
    admin=create_initial_admin('admin@example.com','Admin User','VeryStrongPassword123!',db_path=db)
    resume_id=save_resume(alice,'resume.txt',b'Python SQL resume with experience',db_path=db,uploads_dir=tmp_path/'uploads')
    assert get_resume(alice,resume_id,db_path=db)['owner_id']==alice
    with pytest.raises(AccessDenied):get_resume(bob,resume_id,db_path=db)
    assert get_resume(admin,resume_id,db_path=db)['owner_id']==alice

def test_upload_rejects_oversize():
    with pytest.raises(ResumeValidationError): extract_resume('file.txt',b'a'*(2097152+1))
