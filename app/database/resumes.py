"""Resume persistence and ownership checks enforced below the UI layer."""
from __future__ import annotations
import hashlib
import sqlite3
import uuid
from pathlib import Path
from app.auth.permissions import require_role, AccessDenied
from app.config import DATABASE_PATH, PROJECT_ROOT
from app.database.connection import connect
from app.services.resume_parser import extract_resume

UPLOADS_DIR = PROJECT_ROOT / 'data' / 'uploads'

def _ensure_valid_user(user_id, db_path):
    return require_role(user_id,'user',db_path=db_path)

def save_resume(user_id: int, filename: str, content: bytes, *, db_path=None, uploads_dir=None):
    """Parse before storing; never use untrusted user-supplied name as a path."""
    _ensure_valid_user(user_id,db_path)
    extracted=extract_resume(filename,content)
    ext=filename.rsplit('.',1)[-1].lower()
    digest=hashlib.sha256(content).hexdigest()
    storage_name=f'{uuid.uuid4().hex}.{ext}'
    location=Path(uploads_dir) if uploads_dir is not None else UPLOADS_DIR
    location.mkdir(parents=True,exist_ok=True)
    target=location/storage_name
    try:
        with target.open('xb') as file:
            file.write(content)
        try: target.chmod(0o600)
        except OSError: pass
        with connect(db_path) as conn:
            cur=conn.execute("""INSERT INTO resumes
                (owner_id, original_filename, storage_name, file_type, file_size, sha256, extracted_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id,Path(filename.replace('\\','/')).name,storage_name,ext,len(content),digest,extracted))
            resume_id=cur.lastrowid
            conn.execute('INSERT INTO activity_logs (actor_id,event) VALUES (?,?)',(user_id,'resume.upload'))
        return resume_id
    except Exception:
        target.unlink(missing_ok=True)
        raise

def list_user_resumes(user_id: int, *, db_path=None):
    _ensure_valid_user(user_id,db_path)
    with connect(db_path) as conn:
        rows=conn.execute("""SELECT id,original_filename,file_type,file_size,created_at
            FROM resumes WHERE owner_id=? ORDER BY id DESC""",(user_id,)).fetchall()
    return [dict(row) for row in rows]

def list_all_resumes(admin_id: int, *, db_path=None):
    require_role(admin_id,'admin',db_path=db_path)
    with connect(db_path) as conn:
        rows=conn.execute("""SELECT r.id,r.original_filename,r.file_type,r.file_size,
            r.created_at,u.email AS owner_email,u.display_name AS owner_name
            FROM resumes r JOIN users u ON u.id=r.owner_id ORDER BY r.id DESC""").fetchall()
    return [dict(row) for row in rows]

def get_resume(actor_id: int, resume_id: int, *, db_path=None):
    """Admins can view any resume; users may view only their own."""
    from app.auth.service import get_user
    actor=get_user(actor_id,db_path=db_path) if actor_id else None
    if actor is None or actor['role'] not in ('admin','user'):
        raise AccessDenied('Sign in to access resume records.')
    with connect(db_path) as conn:
        record=conn.execute("""SELECT r.id,r.owner_id,r.original_filename,r.file_type,
            r.file_size,r.sha256,r.extracted_text,r.created_at,u.email AS owner_email
            FROM resumes r JOIN users u ON u.id=r.owner_id WHERE r.id=?""",(resume_id,)).fetchone()
    if not record:
        return None
    if actor['role']!='admin' and record['owner_id']!=actor_id:
        raise AccessDenied('This resume belongs to another account.')
    return dict(record)
