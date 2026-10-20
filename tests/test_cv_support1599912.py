"""CV size, document metadata, migration, and referential integrity tests."""
import io
import sqlite3
import zipfile

import pytest
from docx import Document

from app.config import MAX_RESUME_BYTES, MAX_CV_BYTES
from app.database.connection import connect, initialize_database
from app.database.resumes import save_resume, get_resume, list_user_resumes
from app.auth.service import register_user
from app.services.resume_parser import extract_resume, ResumeValidationError


def _large_docx():
    document = Document()
    document.add_paragraph('Research experience, machine learning, publications and Python.')
    output = io.BytesIO()
    document.save(output)
    output.seek(0)
    # Extra benign media entry makes the uploaded document exceed 2 MB without
    # bloating the text extraction or exceeding the archive extraction budget.
    with zipfile.ZipFile(output, 'a') as archive:
        archive.writestr('word/media/demo.bin', b'\x00' * 2_100_000, compress_type=zipfile.ZIP_STORED)
    return output.getvalue()


def test_document_size_and_type_enforced():
    payload = _large_docx()
    assert MAX_RESUME_BYTES < len(payload) <= MAX_CV_BYTES
    with pytest.raises(ResumeValidationError):
        extract_resume('academic.docx', payload)
    assert 'Research experience' in extract_resume('academic.docx', payload, document_type='cv')
    for kind in ('cv', 'unknown'):
        with pytest.raises(ResumeValidationError):
            extract_resume('academic.txt', b'x' * (MAX_CV_BYTES + 1), document_type=kind)
    with pytest.raises(ResumeValidationError):
        extract_resume('tiny.txt', b'Hello', document_type='something_else')


def test_cv_saved_and_old_resume_default(tmp_path):
    db = tmp_path / 'documents.sqlite3'
    initialize_database(db)
    user = register_user('cv-applicant@example.com', 'Applicant', 'SecurePass!987', db_path=db)
    user_id = user['id'] if isinstance(user, dict) else user
    original = save_resume(user_id, 'resume.txt', b'Python SQL professional experience', db_path=db, uploads_dir=tmp_path/'uploads')
    cv = save_resume(user_id, 'academic.docx', _large_docx(), document_type='cv', db_path=db, uploads_dir=tmp_path/'uploads')
    rows = list_user_resumes(user_id, db_path=db)
    assert {r['id']: r['document_type'] for r in rows} == {original: 'resume', cv: 'cv'}
    assert get_resume(user_id, cv, db_path=db)['document_type'] == 'cv'
    with connect(db) as conn:
        assert conn.execute('PRAGMA foreign_key_check').fetchall() == []
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute('UPDATE resumes SET document_type=? WHERE id=?', ('resume', cv))


def test_legacy_schema_migration_keeps_related_records(tmp_path):
    path = tmp_path/'legacy.sqlite3'
    conn = sqlite3.connect(path)
    conn.executescript('''
      PRAGMA foreign_keys=ON;
      CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT);
      CREATE TABLE resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        original_filename TEXT NOT NULL, storage_name TEXT NOT NULL UNIQUE,
        file_type TEXT NOT NULL CHECK(file_type IN ('pdf','docx','txt','rtf','odt')),
        file_size INTEGER NOT NULL CHECK(file_size > 0 AND file_size <= 2097152),
        sha256 TEXT NOT NULL, extracted_text TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
      );
      CREATE TABLE analyses (id INTEGER PRIMARY KEY, resume_id INTEGER REFERENCES resumes(id));
      CREATE TABLE job_matches (id INTEGER PRIMARY KEY, resume_id INTEGER REFERENCES resumes(id));
      INSERT INTO users VALUES (1, 'someone@example.com');
      INSERT INTO resumes (id,owner_id,original_filename,storage_name,file_type,file_size,sha256,extracted_text)
        VALUES (42,1,'old.txt','abc.txt','txt',99,'hash','Python');
      INSERT INTO analyses VALUES (3,42);
      INSERT INTO job_matches VALUES (4,42);
    ''')
    conn.close()
    # Migration needs to work independently before the full app schema init.
    from app.database.connection import _migrate_documents
    _migrate_documents(path)
    _migrate_documents(path)
    with sqlite3.connect(path) as verify:
        row = verify.execute('SELECT id,document_type,file_size FROM resumes').fetchone()
        assert row == (42, 'resume', 99)
        assert verify.execute('SELECT resume_id FROM analyses').fetchone() == (42,)
        assert verify.execute('SELECT resume_id FROM job_matches').fetchone() == (42,)
        assert verify.execute('PRAGMA foreign_key_check').fetchall() == []
