"""Server-authorized resume analysis persistence."""
import json
from app.database.connection import connect
from app.database.resumes import get_resume
from app.auth.permissions import require_role
from app.services.ats import analyze_text

def analyze_resume(actor_id,resume_id,*,db_path=None):
    require_role(actor_id,'user',db_path=db_path)
    resume=get_resume(actor_id,resume_id,db_path=db_path)
    if resume is None:raise ValueError('Resume does not exist')
    result=analyze_text(resume['extracted_text'],db_path=db_path)
    with connect(db_path) as db:
        cursor=db.execute('INSERT INTO analyses(resume_id,owner_id,score,result_json) VALUES(?,?,?,?)',(resume_id,actor_id,result['score'],json.dumps(result,ensure_ascii=False)))
        db.execute('INSERT INTO activity_logs(actor_id,event) VALUES(?,?)',(actor_id,'resume.analyze'))
        result['analysis_id']=cursor.lastrowid
    return result

def list_analyses(actor_id,*,db_path=None):
    require_role(actor_id,'user',db_path=db_path)
    with connect(db_path) as db:
        rows=db.execute("""SELECT a.id,a.resume_id,a.score,a.created_at,r.original_filename
        FROM analyses a JOIN resumes r ON r.id=a.resume_id WHERE a.owner_id=? ORDER BY a.id DESC""",(actor_id,)).fetchall()
    return [dict(row) for row in rows]

def get_analysis(actor_id,analysis_id,*,db_path=None):
    from app.auth.service import get_user
    actor=get_user(actor_id,db_path=db_path) if actor_id else None
    if not actor:raise PermissionError('Login required')
    with connect(db_path) as db:
        row=db.execute('SELECT * FROM analyses WHERE id=?',(analysis_id,)).fetchone()
    if row is None:return None
    if actor['role']!='admin' and row['owner_id']!=actor_id:raise PermissionError('Analysis belongs to another user')
    result=json.loads(row['result_json']);result.update({'analysis_id':row['id'],'created_at':row['created_at'],'resume_id':row['resume_id']})
    return result
