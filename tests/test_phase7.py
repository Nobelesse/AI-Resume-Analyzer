import pytest
from app.database.connection import initialize_database,connect
from app.auth.service import create_initial_admin,register_user
from app.auth.permissions import AccessDenied
from app.database.dashboard import (admin_overview,admin_resumes,admin_activity,admin_set_user_active,
                                    delete_resume,user_overview,csv_export)

@pytest.fixture
def sample(tmp_path):
    db=tmp_path/'app.sqlite3';uploads=tmp_path/'uploads';uploads.mkdir();initialize_database(db)
    admin=create_initial_admin('admin@example.com','Admin Owner','SecurePassword123!',db_path=db)
    a=register_user('alice@example.com','Alice User','SecurePassword123!',db_path=db)
    b=register_user('bob@example.com','Bob User','SecurePassword123!',db_path=db)
    with connect(db) as conn:
        cur=conn.execute('INSERT INTO resumes (owner_id,original_filename,storage_name,file_type,file_size,sha256,extracted_text) VALUES (?,?,?,?,?,?,?)',(a,'alice.txt','safe123.txt','txt',12,'abc','Python SQL'))
        resume_id=cur.lastrowid
        conn.execute('INSERT INTO analyses (owner_id,resume_id,score,result_json) VALUES (?,?,?,?)',(a,resume_id,70,'{}'))
        conn.execute('INSERT INTO job_matches (owner_id,resume_id,job_title,job_description,result_json) VALUES (?,?,?,?,?)',(a,resume_id,'Data Analyst','SQL','{}'))
    (uploads/'safe123.txt').write_text('Python SQL')
    return db,uploads,admin,a,b,resume_id

def test_admin_metrics_and_user_scoping(sample):
    db,_,admin,a,b,_=sample
    assert admin_overview(admin,db_path=db)['counts']['resumes']==1
    assert user_overview(a,db_path=db)['counts']['job_matches']==1
    assert user_overview(b,db_path=db)['counts']['resumes']==0
    with pytest.raises(AccessDenied):admin_overview(a,db_path=db)
    with pytest.raises(AccessDenied):user_overview(admin,db_path=db)

def test_filtered_records_private(sample):
    db,_,admin,a,_,_=sample
    assert len(admin_resumes(admin,db_path=db,search='alice'))==1
    assert len(admin_resumes(admin,db_path=db,search='nobody'))==0
    with pytest.raises(AccessDenied):admin_resumes(a,db_path=db)

def test_deactivate_cannot_touch_admin(sample):
    db,_,admin,a,_,_=sample
    admin_set_user_active(admin,a,False,db_path=db)
    with connect(db) as conn:assert conn.execute('SELECT is_active FROM users WHERE id=?',(a,)).fetchone()[0]==0
    with pytest.raises(ValueError):admin_set_user_active(admin,admin,False,db_path=db)
    with pytest.raises(AccessDenied):admin_set_user_active(a,admin,False,db_path=db)
    admin_set_user_active(admin,a,True,db_path=db)
    assert admin_activity(admin,db_path=db)[0]['event']=='admin.user.activate'

def test_delete_ownership_and_cascade(sample):
    db,uploads,admin,a,b,resume_id=sample
    with pytest.raises(AccessDenied):delete_resume(b,resume_id,db_path=db,uploads_dir=uploads)
    assert delete_resume(a,resume_id,db_path=db,uploads_dir=uploads)
    assert not (uploads/'safe123.txt').exists()
    with connect(db) as conn:
        assert conn.execute('SELECT COUNT(*) FROM analyses').fetchone()[0]==0
        assert conn.execute('SELECT COUNT(*) FROM job_matches').fetchone()[0]==0
    assert not delete_resume(admin,resume_id,db_path=db,uploads_dir=uploads)

def test_admin_delete(sample):
    db,uploads,admin,_,_,resume_id=sample
    assert delete_resume(admin,resume_id,db_path=db,uploads_dir=uploads)
    assert admin_activity(admin,db_path=db)[0]['event']=='admin.resume.delete'

def test_csv_formula_guard():
    output=csv_export([{'email':'=HYPERLINK("example")','id':1}],['id','email']).decode('utf-8-sig')
    assert "'=HYPERLINK" in output

def test_unique_paths():
    import ast
    from pathlib import Path
    tree=ast.parse((Path(__file__).parents[1]/'app'/'main.py').read_text(encoding='utf-8'))
    paths=[kw.value.value for node in ast.walk(tree) if isinstance(node,ast.Call) for kw in node.keywords if kw.arg=='url_path' and isinstance(kw.value,ast.Constant)]
    assert len(paths)==len(set(paths))
