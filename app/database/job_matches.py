"""Authorization-enforced persisted job comparisons."""
import json
from app.auth.permissions import require_role,AccessDenied
from app.auth.service import get_user
from app.database.connection import connect
from app.database.resumes import get_resume
from app.services.job_matcher import compare_resume_to_job

def save_job_match(actor_id,resume_id,title,description,*,db_path=None,required_weight=0.75):
    require_role(actor_id,'user',db_path=db_path)
    if not 2<=len(title.strip())<=150:raise ValueError('Job title must be between 2 and 150 characters')
    resume=get_resume(actor_id,resume_id,db_path=db_path)
    if resume is None:raise ValueError('Resume not found')
    result=compare_resume_to_job(resume['extracted_text'],description,db_path=db_path,required_weight=required_weight)
    with connect(db_path) as db:
        cur=db.execute('INSERT INTO job_matches(owner_id,resume_id,job_title,job_description,result_json) VALUES (?,?,?,?,?)',
            (actor_id,resume_id,title.strip(),description,json.dumps(result,ensure_ascii=False)))
        db.execute('INSERT INTO activity_logs(actor_id,event) VALUES (?,?)',(actor_id,'job.compare'))
        result.update({'match_id':cur.lastrowid,'job_title':title.strip(),'resume_id':resume_id})
    return result

def list_job_matches(actor_id,*,db_path=None):
    require_role(actor_id,'user',db_path=db_path)
    with connect(db_path) as db:
        rows=db.execute('SELECT id,resume_id,job_title,created_at FROM job_matches WHERE owner_id=? ORDER BY id DESC',(actor_id,)).fetchall()
    return [dict(row) for row in rows]

def get_job_match(actor_id,match_id,*,db_path=None):
    actor=get_user(actor_id,db_path=db_path) if actor_id else None
    if not actor:raise AccessDenied('Sign in required')
    with connect(db_path) as db:
        row=db.execute('SELECT * FROM job_matches WHERE id=?',(match_id,)).fetchone()
    if row is None:return None
    if actor['role']!='admin' and row['owner_id']!=actor_id:raise AccessDenied('Comparison belongs to another user')
    result=json.loads(row['result_json'])
    result.update({'match_id':row['id'],'job_title':row['job_title'],'resume_id':row['resume_id'],'created_at':row['created_at']})
    return result
