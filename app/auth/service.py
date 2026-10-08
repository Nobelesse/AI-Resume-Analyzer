"""Role-safe account registration, authentication and login throttling."""
import re
import sqlite3
import time
from app.database.connection import connect
from app.auth.security import hash_password, verify_password

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
LOCK_AFTER = 5
LOCK_SECONDS = 15 * 60

class AuthError(Exception):
    """Generic user-safe authentication error."""

def normalized_email(email):
    email = (email or "").strip().lower()
    if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("Provide a valid email address.")
    return email

def register_user(email, display_name, password, *, db_path=None):
    email = normalized_email(email)
    name = (display_name or "").strip()
    if not (2 <= len(name) <= 80):
        raise ValueError("Name must be between 2 and 80 characters.")
    hashed = hash_password(password)
    try:
        with connect(db_path) as conn:
            cursor = conn.execute("INSERT INTO users(email,display_name,password_hash,role) VALUES(?,?,?,'user')", (email, name, hashed))
            conn.execute("INSERT INTO activity_logs(actor_id,event) VALUES(?,?)", (cursor.lastrowid, "registered"))
            return int(cursor.lastrowid)
    except sqlite3.IntegrityError:
        raise ValueError("This email address is already registered.") from None

def create_initial_admin(email, display_name, password, *, db_path=None):
    email = normalized_email(email)
    name = (display_name or "").strip()
    if not (2 <= len(name) <= 80):
        raise ValueError("Name must be between 2 and 80 characters.")
    hashed = hash_password(password)
    with connect(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]:
            raise ValueError("An administrator already exists; bootstrap is disabled.")
        try:
            cur = conn.execute("INSERT INTO users(email,display_name,password_hash,role) VALUES(?,?,?,'admin')", (email,name,hashed))
        except sqlite3.IntegrityError:
            raise ValueError("Email is already in use.") from None
        conn.execute("INSERT INTO activity_logs(actor_id,event) VALUES(?,?)", (cur.lastrowid,"admin_bootstrap"))
        return int(cur.lastrowid)

def authenticate(email, password, expected_role, *, db_path=None, now=None):
    if expected_role not in ("admin", "user"):
        raise ValueError("Invalid login role")
    current = int(time.time() if now is None else now)
    try:
        email = normalized_email(email)
    except ValueError:
        raise AuthError("Invalid credentials or unavailable account.") from None
    # Throttle attempts against a single email separately for each portal.
    throttle_key = f"{expected_role}:{email}"
    with connect(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        throttle = conn.execute("SELECT failure_count, blocked_until FROM login_throttle WHERE identifier=?", (throttle_key,)).fetchone()
        if throttle and throttle["blocked_until"] > current:
            raise AuthError("Too many attempts. Try again in 15 minutes.")
        row = conn.execute("SELECT id,email,display_name,password_hash,role,is_active FROM users WHERE email=?", (email,)).fetchone()
        valid = bool(row and row["is_active"] and row["role"] == expected_role and verify_password(row["password_hash"],password))
        if not valid:
            count = (throttle["failure_count"] if throttle and throttle["blocked_until"] > 0 else (throttle["failure_count"] if throttle else 0)) + 1
            block = current + LOCK_SECONDS if count >= LOCK_AFTER else 0
            conn.execute("INSERT INTO login_throttle(identifier,failure_count,blocked_until) VALUES(?,?,?) ON CONFLICT(identifier) DO UPDATE SET failure_count=excluded.failure_count, blocked_until=excluded.blocked_until",(throttle_key,count,block))
            raise_later = True
        else:
            conn.execute("DELETE FROM login_throttle WHERE identifier=?", (throttle_key,))
            conn.execute("INSERT INTO activity_logs(actor_id,event) VALUES(?,?)", (row["id"],"login"))
            raise_later = False
            result = {key:row[key] for key in ("id","email","display_name","role")}
    if raise_later:
        raise AuthError("Invalid credentials or unavailable account.")
    return result

def get_user(user_id, *, db_path=None):
    with connect(db_path) as conn:
        row=conn.execute("SELECT id,email,display_name,role,is_active FROM users WHERE id=?", (user_id,)).fetchone()
    if not row or not row["is_active"]:
        return None
    return {key:row[key] for key in ("id","email","display_name","role")}

def audit_logout(user_id, *, db_path=None):
    with connect(db_path) as conn:
        conn.execute("INSERT INTO activity_logs(actor_id,event) VALUES(?,?)", (user_id,"logout"))
