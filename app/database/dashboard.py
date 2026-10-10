"""Authorized administration, audit, dashboard statistics and deletion APIs."""
import csv
import io
import sqlite3
from pathlib import Path
from app.auth.permissions import require_role, AccessDenied
from app.database.connection import connect
from app.database.resumes import UPLOADS_DIR


def _audit(db, actor, event):
    db.execute('INSERT INTO activity_logs(actor_id,event) VALUES (?,?)', (actor, event))


def admin_overview(admin_id, *, db_path=None):
    require_role(admin_id, 'admin', db_path=db_path)
    with connect(db_path) as db:
        counts = {table: db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                  for table in ('users', 'resumes', 'analyses', 'job_matches', 'skills')}
        counts['active_users'] = db.execute("SELECT COUNT(*) FROM users WHERE role='user' AND is_active=1").fetchone()[0]
        daily = [dict(r) for r in db.execute('''SELECT substr(created_at,1,10) AS day, COUNT(*) AS count
                    FROM resumes GROUP BY substr(created_at,1,10) ORDER BY day DESC LIMIT 30''').fetchall()]
        types = [dict(r) for r in db.execute('SELECT file_type AS type,COUNT(*) AS count FROM resumes GROUP BY file_type').fetchall()]
    return {'counts':counts,'daily_uploads':list(reversed(daily)),'file_types':types}


def admin_resumes(admin_id, *, db_path=None, search='', owner_id=None, file_type=None, limit=300):
    require_role(admin_id,'admin',db_path=db_path)
    where=[];params=[]
    if search.strip():
        where.append('(r.original_filename LIKE ? OR u.email LIKE ?)')
        escaped='%' + search.strip()[:100].replace('%','\\%').replace('_','\\_') + '%'
        where[-1] = '(r.original_filename LIKE ? ESCAPE \'\\\' OR u.email LIKE ? ESCAPE \'\\\')'
        params.extend([escaped,escaped])
    if owner_id is not None:where.append('r.owner_id=?');params.append(int(owner_id))
    if file_type:where.append('r.file_type=?');params.append(file_type)
    clause=(' WHERE '+' AND '.join(where)) if where else ''
    with connect(db_path) as db:
        rows=db.execute('''SELECT r.id,r.owner_id,u.email AS owner_email,r.original_filename,
          r.file_type,r.file_size,r.created_at FROM resumes r JOIN users u ON u.id=r.owner_id'''+clause+
          ' ORDER BY r.id DESC LIMIT ?',(*params,min(max(int(limit),1),2000))).fetchall()
    return [dict(row) for row in rows]


def admin_activity(admin_id, *, db_path=None, event=None, limit=200):
    require_role(admin_id,'admin',db_path=db_path)
    with connect(db_path) as db:
        rows=db.execute('''SELECT a.id,a.actor_id,COALESCE(u.email,'[deleted account]') AS actor_email,
          a.event,a.created_at FROM activity_logs a LEFT JOIN users u ON u.id=a.actor_id
          WHERE (? IS NULL OR a.event=?) ORDER BY a.id DESC LIMIT ?''',
          (event,event,min(max(int(limit),1),1000))).fetchall()
    return [dict(r) for r in rows]


def admin_set_user_active(admin_id, target_id, enabled, *, db_path=None):
    require_role(admin_id,'admin',db_path=db_path)
    if admin_id==target_id:raise ValueError('Cannot change your own administrator status.')
    with connect(db_path) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT role FROM users WHERE id=?',(target_id,)).fetchone()
        if row is None:raise ValueError('Account not found.')
        if row['role']=='admin':raise AccessDenied('Administrator account changes are not available here.')
        db.execute('UPDATE users SET is_active=? WHERE id=?',(int(bool(enabled)),target_id))
        _audit(db,admin_id,'admin.user.activate' if enabled else 'admin.user.deactivate')


def delete_resume(actor_id,resume_id,*,db_path=None,uploads_dir=None):
    """Users delete their own resumes; admins can delete any; dependent analyses cascade."""
    from app.auth.service import get_user
    account=get_user(actor_id,db_path=db_path)
    if not account:raise AccessDenied('Authentication required.')
    with connect(db_path) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT owner_id,storage_name FROM resumes WHERE id=?',(resume_id,)).fetchone()
        if row is None:return False
        if account['role']!='admin' and row['owner_id']!=actor_id:raise AccessDenied('Cannot delete another user\'s resume.')
        db.execute('DELETE FROM resumes WHERE id=?',(resume_id,))
        _audit(db,actor_id,'admin.resume.delete' if account['role']=='admin' else 'resume.delete')
    # Delete only a generated storage basename after successful DB deletion.
    name=row['storage_name']
    if Path(name).name==name:
        location=Path(uploads_dir) if uploads_dir is not None else UPLOADS_DIR
        (location/name).unlink(missing_ok=True)
    return True


def user_overview(user_id,*,db_path=None):
    require_role(user_id,'user',db_path=db_path)
    with connect(db_path) as db:
        counts={table:db.execute(f'SELECT COUNT(*) FROM {table} WHERE {"owner_id" if table != "users" else "id"}=?',(user_id,)).fetchone()[0]
                for table in ('resumes','analyses','job_matches')}
        recent=[dict(r) for r in db.execute('''SELECT id,original_filename,created_at FROM resumes
            WHERE owner_id=? ORDER BY id DESC LIMIT 8''',(user_id,)).fetchall()]
        scores=[r[0] for r in db.execute('SELECT score FROM analyses WHERE owner_id=?',(user_id,)).fetchall()]
    return {'counts':counts,'recent_resumes':recent,'average_ats_score': round(sum(scores)/len(scores),1) if scores else None}


def csv_export(rows,fields):
    """Protect spreadsheet consumers from formula injection and omit sensitive columns."""
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader()
    for row in rows:
        writer.writerow({k: ("'"+str(row.get(k,'')) if isinstance(row.get(k),str) and row.get(k,'').lstrip().startswith(('=','+','-','@','\t','\r')) else row.get(k,'')) for k in fields})
    return out.getvalue().encode('utf-8-sig')
