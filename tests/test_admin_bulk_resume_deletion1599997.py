"""Administrator bulk deletion must preserve accounts and cascade related data."""
import pytest
from app.auth.permissions import AccessDenied
from app.auth.service import create_initial_admin, register_user
from app.database.connection import connect, initialize_database
from app.database.dashboard import admin_delete_resumes, admin_activity


@pytest.fixture
def workspace(tmp_path):
    db = tmp_path / 'bulk.sqlite3'
    uploads = tmp_path / 'uploads'
    uploads.mkdir()
    initialize_database(db)
    admin = create_initial_admin('admin@example.com', 'Admin Owner', 'SecurePassword123!', db_path=db)
    user = register_user('user@example.com', 'Regular User', 'SecurePassword123!', db_path=db)
    ids = []
    with connect(db) as conn:
        for n in range(3):
            name = f'doc{n}.txt'
            (uploads / name).write_text('resume')
            cur = conn.execute('INSERT INTO resumes (owner_id,original_filename,storage_name,file_type,file_size,sha256,extracted_text) VALUES (?,?,?,?,?,?,?)',
                               (user, name, name, 'txt', 6, 'sha', 'Python'))
            resume_id = cur.lastrowid
            ids.append(resume_id)
            conn.execute('INSERT INTO analyses (owner_id,resume_id,score,result_json) VALUES (?,?,?,?)',(user,resume_id,80,'{}'))
            conn.execute('INSERT INTO job_matches (owner_id,resume_id,job_title,job_description,result_json) VALUES (?,?,?,?,?)',(user,resume_id,'Analyst','Python','{}'))
    return db,uploads,admin,user,ids


def test_bulk_selected_only_and_cascades(workspace):
    db,uploads,admin,user,ids=workspace
    assert admin_delete_resumes(admin,[ids[0],ids[2],ids[0]],db_path=db,uploads_dir=uploads)==2
    with connect(db) as conn:
        remaining={r[0] for r in conn.execute('SELECT id FROM resumes')}
        assert remaining=={ids[1]}
        assert conn.execute('SELECT COUNT(*) FROM analyses').fetchone()[0]==1
        assert conn.execute('SELECT COUNT(*) FROM job_matches').fetchone()[0]==1
        assert conn.execute('SELECT COUNT(*) FROM users WHERE id=?',(user,)).fetchone()[0]==1
    assert not (uploads/'doc0.txt').exists()
    assert (uploads/'doc1.txt').exists()
    assert not (uploads/'doc2.txt').exists()
    assert admin_activity(admin,db_path=db)[0]['event']=='admin.resume.bulk_delete'


def test_bulk_all_and_reject_invalid_or_non_admin(workspace):
    db,uploads,admin,user,ids=workspace
    with pytest.raises(AccessDenied):
        admin_delete_resumes(user,ids,db_path=db,uploads_dir=uploads)
    for invalid in ([],[ids[0],999999],['junk'], '1', [0]):
        with pytest.raises(ValueError):
            admin_delete_resumes(admin,invalid,db_path=db,uploads_dir=uploads)
    with connect(db) as conn:
        assert conn.execute('SELECT COUNT(*) FROM resumes').fetchone()[0]==3
    assert admin_delete_resumes(admin,ids,db_path=db,uploads_dir=uploads)==3
    assert not list(uploads.iterdir())
    with connect(db) as conn:
        assert conn.execute('SELECT COUNT(*) FROM resumes').fetchone()[0]==0
        assert conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]==2
