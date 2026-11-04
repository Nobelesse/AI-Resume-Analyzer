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
            # Serialize ID selection and insertion so concurrent registrations cannot collide.
            conn.execute("BEGIN IMMEDIATE")
            occupied = [row[0] for row in conn.execute(
                "SELECT id FROM users WHERE id > 0 ORDER BY id"
            ).fetchall()]
            user_id = 1
            for occupied_id in occupied:
                if occupied_id > user_id:
                    break
                if occupied_id == user_id:
                    user_id += 1
            conn.execute(
                "INSERT INTO users(id,email,display_name,password_hash,role) VALUES(?,?,?,?,'user')",
                (user_id, email, name, hashed),
            )
            conn.execute("INSERT INTO activity_logs(actor_id,event) VALUES(?,?)", (user_id, "registered"))
            return user_id
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
            cur = conn.execute("INSERT INTO users(id,email,display_name,password_hash,role) VALUES(0,?,?,?,'admin')", (email,name,hashed))
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

def get_user(user_id, *, db_path=None, include_session_guard=False):
    # A guard derived from the salted password hash changes whenever an ID is
    # reused. It is never returned to ordinary account/authorization callers.
    columns = "id,email,display_name,role,is_active,password_hash" if include_session_guard else "id,email,display_name,role,is_active"
    with connect(db_path) as conn:
        row = conn.execute(f"SELECT {columns} FROM users WHERE id=?", (user_id,)).fetchone()
    if not row or not row["is_active"]:
        return None
    result = {key:row[key] for key in ("id","email","display_name","role")}
    if include_session_guard:
        import hashlib
        result["_session_guard"] = hashlib.sha256(row["password_hash"].encode("utf-8")).hexdigest()
    return result

def audit_logout(user_id, *, db_path=None):
    with connect(db_path) as conn:
        conn.execute("INSERT INTO activity_logs(actor_id,event) VALUES(?,?)", (user_id,"logout"))
