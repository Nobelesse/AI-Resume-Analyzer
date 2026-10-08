"""Server-side authorization helpers (not merely visual navigation hiding)."""
from app.auth.service import get_user

class AccessDenied(PermissionError):
    pass

def require_role(user_id, role, *, db_path=None):
    user = get_user(user_id, db_path=db_path) if user_id is not None else None
    if not user or user["role"] != role:
        raise AccessDenied("You do not have permission to access this resource.")
    return user

def admin_list_accounts(admin_id, *, db_path=None):
    """Admin-only query; future protected queries should use the same pattern."""
    from app.database.connection import connect
    require_role(admin_id,"admin",db_path=db_path)
    with connect(db_path) as conn:
        rows=conn.execute("SELECT id,display_name,email,role,is_active,created_at FROM users ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]
