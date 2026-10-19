"""Database-level tests for a single immutable administrator."""
import sqlite3
import pytest
from app.database.connection import connect, initialize_database
from app.auth.service import create_initial_admin, register_user
from app.database.dashboard import admin_set_user_active
from app.auth.permissions import AccessDenied


def test_only_one_permanent_administrator(tmp_path):
    db = tmp_path / "admins.sqlite3"
    initialize_database(db)
    admin_id = create_initial_admin("admin@example.com", "Owner", "SecurePassword123!", db_path=db)
    user_id = register_user("user@example.com", "User", "SecurePassword123!", db_path=db)
    with pytest.raises(ValueError):
        create_initial_admin("second@example.com", "Second", "SecurePassword123!", db_path=db)
    with connect(db) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO users(email,display_name,password_hash,role) VALUES ('other@example.com','Other','hash','admin')")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
        for sql, params in [
            ("UPDATE users SET is_active=0 WHERE id=?", (admin_id,)),
            ("UPDATE users SET role='user' WHERE id=?", (admin_id,)),
            ("UPDATE users SET email='new@example.com' WHERE id=?", (admin_id,)),
            ("DELETE FROM users WHERE id=?", (admin_id,)),
        ]:
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(sql, params)
        assert conn.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND is_active=1").fetchone()[0] == 1
    with pytest.raises((ValueError, AccessDenied)):
        admin_set_user_active(admin_id, admin_id, False, db_path=db)
    admin_set_user_active(admin_id, user_id, False, db_path=db)
    admin_set_user_active(admin_id, user_id, True, db_path=db)


def test_admin_constraints_survive_reinitialization(tmp_path):
    db=tmp_path / "persistent.sqlite3"
    initialize_database(db)
    admin_id=create_initial_admin("admin@example.com", "Owner", "SecurePassword123!", db_path=db)
    initialize_database(db)
    with connect(db) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM users WHERE id=?", (admin_id,))
