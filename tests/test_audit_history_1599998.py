"""Identity snapshots survive removal of the account to which an event belonged."""
from app.database.connection import initialize_database, connect
from app.database.dashboard import admin_activity, admin_delete_user
from app.auth.service import create_initial_admin, register_user, authenticate

def test_deleted_users_retain_historical_actor_email(tmp_path):
    db = tmp_path / 'history.sqlite3'
    initialize_database(db)
    admin_id = create_initial_admin('admin@example.org', 'Admin', 'SecurePass!123', db_path=db)
    user_id = register_user('former@example.org', 'Former User', 'SecurePass!123', db_path=db)
    authenticate('former@example.org', 'SecurePass!123', 'user', db_path=db)
    admin_delete_user(admin_id, user_id, db_path=db, uploads_dir=tmp_path)
    items = [a for a in admin_activity(admin_id, db_path=db) if a['event'] in ('login', 'registered')]
    assert items
    assert all(a['actor_email'] == 'former@example.org' for a in items)
    assert all(a['actor_id'] == user_id for a in items)
    with connect(db) as conn:
        assert conn.execute('SELECT 1 FROM users WHERE id=?', (user_id,)).fetchone() is None

def test_previously_deleted_identity_not_fabricated(tmp_path):
    db=tmp_path/'older.sqlite3'
    initialize_database(db)
    admin_id=create_initial_admin('admin@example.org', 'Admin', 'SecurePass!123', db_path=db)
    with connect(db) as conn:
        conn.execute("INSERT INTO activity_logs(actor_id,event) VALUES (NULL,'legacy.event')")
    initialize_database(db)
    row=next(a for a in admin_activity(admin_id, db_path=db) if a['event']=='legacy.event')
    assert row['actor_email']=='[historical identity unavailable]'
    assert row['actor_id'] is None

def test_migration_backfills_existing_live_actor(tmp_path):
    db=tmp_path/'migrate.sqlite3'
    initialize_database(db)
    admin_id=create_initial_admin('admin@example.org', 'Admin', 'SecurePass!123', db_path=db)
    with connect(db) as conn:
        conn.execute("UPDATE activity_logs SET actor_email_snapshot=NULL,actor_original_id=NULL WHERE actor_id=?", (admin_id,))
    initialize_database(db)
    rows=admin_activity(admin_id,db_path=db)
    assert rows[0]['actor_email']=='admin@example.org'
    assert rows[0]['actor_id']==admin_id
