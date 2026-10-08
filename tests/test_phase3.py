import sqlite3
import pytest
from app.database.connection import initialize_database,connect
from app.auth.security import hash_password,verify_password
from app.auth.service import register_user,create_initial_admin,authenticate,AuthError,get_user
from app.auth.permissions import require_role,admin_list_accounts,AccessDenied

@pytest.fixture
def db(tmp_path):
    path=tmp_path/'private.sqlite3'
    initialize_database(path)
    return path

def test_password_hash_and_policy():
    hashed=hash_password('correct-password-123')
    assert 'correct-password-123' not in hashed
    assert verify_password(hashed,'correct-password-123')
    assert not verify_password(hashed,'wrong-password-123')
    with pytest.raises(ValueError):hash_password('short1')

def test_register_normalizes_email_and_role_is_user(db):
    uid=register_user(' Person@Example.com ','Sample Person','safe-password-123',db_path=db)
    assert get_user(uid,db_path=db)['role']=='user'
    assert get_user(uid,db_path=db)['email']=='person@example.com'
    with pytest.raises(ValueError):register_user('person@example.com','Another Person','safe-password-123',db_path=db)

def test_distinct_portals_and_admin_bootstrap(db):
    uid=register_user('student@example.com','Student','user-password-123',db_path=db)
    aid=create_initial_admin('admin@example.com','Administrator','admin-password-123',db_path=db)
    assert authenticate('student@example.com','user-password-123','user',db_path=db)['id']==uid
    assert authenticate('admin@example.com','admin-password-123','admin',db_path=db)['id']==aid
    with pytest.raises(AuthError):authenticate('student@example.com','user-password-123','admin',db_path=db)
    with pytest.raises(AuthError):authenticate('admin@example.com','admin-password-123','user',db_path=db)
    with pytest.raises(ValueError):create_initial_admin('other@example.com','Other Admin','admin-password-123',db_path=db)

def test_admin_only_queries(db):
    user=register_user('user@example.com','User Name','user-password-123',db_path=db)
    admin=create_initial_admin('admin@example.com','Admin Name','admin-password-123',db_path=db)
    with pytest.raises(AccessDenied):admin_list_accounts(user,db_path=db)
    with pytest.raises(AccessDenied):require_role(None,'admin',db_path=db)
    assert len(admin_list_accounts(admin,db_path=db))==2
    assert 'password_hash' not in admin_list_accounts(admin,db_path=db)[0]

def test_rate_limited_login(db):
    register_user('user@example.com','User Name','user-password-123',db_path=db)
    for _ in range(5):
        with pytest.raises(AuthError):authenticate('user@example.com','bad', 'user',db_path=db,now=100000)
    with pytest.raises(AuthError,match='Too many attempts'):
        authenticate('user@example.com','user-password-123','user',db_path=db,now=100001)
    assert authenticate('user@example.com','user-password-123','user',db_path=db,now=100000+901)

def test_database_initialized_twice(db):
    initialize_database(db)
    with connect(db) as conn:
        assert conn.execute('PRAGMA user_version').fetchone()[0]==3

def test_inactive_user_rejected(db):
    uid=register_user('user@example.com','User Name','user-password-123',db_path=db)
    with connect(db) as conn:conn.execute('UPDATE users SET is_active=0 WHERE id=?',(uid,))
    assert get_user(uid,db_path=db) is None
    with pytest.raises(AuthError):authenticate('user@example.com','user-password-123','user',db_path=db)
