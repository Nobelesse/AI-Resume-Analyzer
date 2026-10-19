import pytest
from app.database.connection import connect, initialize_database
from app.auth.service import create_initial_admin, register_user
from app.auth.permissions import AccessDenied
from app.database.dashboard import admin_delete_user, admin_activity


def test_deletion_removes_regular_user_dependents_and_upload(tmp_path):
    db=tmp_path/'test.sqlite3'; uploads=tmp_path/'uploads'; uploads.mkdir()
    initialize_database(db)
    admin=create_initial_admin('admin@example.com','Admin','SecurePassword123!',db_path=db)
    user=register_user('user@example.com','Member','SecurePassword123!',db_path=db)
    with connect(db) as conn:
        rid=conn.execute('INSERT INTO resumes (owner_id,original_filename,storage_name,file_type,file_size,sha256,extracted_text) VALUES (?,?,?,?,?,?,?)',
             (user,'file.txt','safe-456.txt','txt',5,'abc','data')).lastrowid
        conn.execute('INSERT INTO analyses (owner_id,resume_id,score,result_json) VALUES (?,?,?,?)',(user,rid,50,'{}'))
        conn.execute('INSERT INTO job_matches (owner_id,resume_id,job_title,job_description,result_json) VALUES (?,?,?,?,?)',(user,rid,'Role','JD','{}'))
    (uploads/'safe-456.txt').write_text('data')
    assert admin_delete_user(admin,user,db_path=db,uploads_dir=uploads)
    assert not (uploads/'safe-456.txt').exists()
    with connect(db) as conn:
        assert conn.execute('SELECT COUNT(*) FROM users WHERE id=?',(user,)).fetchone()[0]==0
        for table in ('resumes','analyses','job_matches'):
            assert conn.execute(f'SELECT COUNT(*) FROM {table} WHERE owner_id=?',(user,)).fetchone()[0]==0
        assert conn.execute('SELECT role,is_active FROM users WHERE id=?',(admin,)).fetchone()['role']=='admin'
    assert admin_activity(admin,db_path=db)[0]['event']=='admin.user.delete'


def test_admin_cannot_delete_admin_or_missing_user(tmp_path):
    db=tmp_path/'test.sqlite3';initialize_database(db)
    admin=create_initial_admin('admin@example.com','Admin','SecurePassword123!',db_path=db)
    user=register_user('user@example.com','Member','SecurePassword123!',db_path=db)
    with pytest.raises(AccessDenied):admin_delete_user(admin,admin,db_path=db)
    with pytest.raises(AccessDenied):admin_delete_user(user,admin,db_path=db)
    with pytest.raises(AccessDenied):admin_delete_user(user,user,db_path=db)
    with pytest.raises(ValueError):admin_delete_user(admin,999999,db_path=db)
    with connect(db) as conn:
        assert conn.execute('SELECT role FROM users WHERE id=?',(admin,)).fetchone()[0]=='admin'
