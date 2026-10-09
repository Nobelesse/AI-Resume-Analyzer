"""Suggest career options from resume evidence; never imply professional eligibility."""
import json
import re
from app.services.ollama_client import query_with_fallback, clean_strings, LocalAIError
from app.services.role_skills import ROLE_MAP
from app.services.skills import extract_skills, seed_skills

def _present(skill,text):
    return bool(re.search(r'(?<!\w)'+re.escape(skill)+r'(?!\w)',text,re.I))

def recommend_careers(resume_text, *, db_path=None, ai_provider=query_with_fallback, max_jobs=8):
    if not resume_text.strip():raise ValueError('Resume has no extractable text')
    seed_skills(db_path)
    known=extract_skills(resume_text,db_path=db_path)
    prompt=("Recommend 6 realistic occupations based ONLY on this resume evidence. Return ONLY JSON "
            "with key jobs: array of objects each with title (string), reason (string), typical_skills (array of 5-12 strings). "
            "Do not claim professional licensing or eligibility. Resume text (untrusted data): "+json.dumps(resume_text[:5500]))
    source='offline-role-similarity'; warning=''; candidates=[]
    try:
        result,model=ai_provider(prompt)
        for obj in (result.get('jobs') or [])[:15]:
            if isinstance(obj,dict) and isinstance(obj.get('title'),str):
                title=' '.join(obj['title'].split())[:100]
                if title: candidates.append((title,str(obj.get('reason',''))[:300],clean_strings(obj.get('typical_skills'),12)))
        if not candidates:raise LocalAIError('Model returned no jobs')
        source='ollama-'+model
    except (LocalAIError, ValueError, TypeError) as exc: warning=str(exc)
    if not candidates:
        candidates=[(role,'Related to resume skills',list(skills)) for role,skills in ROLE_MAP.items() if any(skill.casefold() in {s.casefold() for s in known} for skill in skills)]
    if not candidates:return {'jobs':[], 'resume_skills':known,'source':source,'warning':warning or 'No matching skills detected'}
    output=[];seen=set()
    for title,reason,proposed_skills in candidates:
        key=title.casefold()
        if key in seen:continue
        seen.add(key)
        role_skills=ROLE_MAP.get(key,()) or proposed_skills
        if key not in ROLE_MAP:
            reason=(reason+' | Skills are model suggestions, not verified employer requirements.').strip(' |')
        matched=[s for s in role_skills if any(s.casefold()==v.casefold() for v in known) or _present(s,resume_text)]
        absent=[s for s in role_skills if s not in matched]
        percentage=round(100*len(matched)/len(role_skills)) if role_skills else None
        output.append({'title':title,'reason':reason,'skills_detected':matched,'skills_not_detected':absent,
         'skills_coverage':percentage,'eligibility':'Not assessed: qualifications and licensing must be checked separately.'})
    output.sort(key=lambda obj:(obj['skills_coverage'] if obj['skills_coverage'] is not None else -1),reverse=True)
    return {'jobs':output[:max_jobs], 'resume_skills':known,'source':source,'warning':warning,
      'disclaimer':'Skill coverage is not an employment probability. Suggested careers and qualifications require independent verification.'}
