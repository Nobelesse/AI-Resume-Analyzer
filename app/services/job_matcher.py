"""Explainable, offline job-description to resume comparison."""
from __future__ import annotations
import math
import re
from collections import Counter
from app.services.skills import extract_skills, seed_skills
from app.services.role_skills import suggest_for_title, suggest_with_ollama

STOP = set('the and for are with from this that you your our have will work team experience years year job role in on of a an to is as or be by at it we they can using required preferred plus must should ability knowledge skills strong excellent good including such related'.split())

def tokens(text: str) -> list[str]:
    return [x for x in re.findall(r"[a-z0-9][a-z0-9+#.]*", text.casefold()) if x not in STOP and len(x)>1]

def cosine_similarity(first: str, second: str) -> float:
    """Local TF-IDF cosine over a two-document corpus; 0..1."""
    a,b=Counter(tokens(first)),Counter(tokens(second))
    if not a or not b:return 0.0
    vocabulary=set(a)|set(b)
    weighted=[]
    for counts in (a,b):
        weighted.append({key:(1+math.log(counts[key]))*(1+math.log((3)/(1+int(key in a)+int(key in b)))) for key in vocabulary if counts[key]})
    x,y=weighted
    dot=sum(x[k]*y.get(k,0) for k in x)
    norm=math.sqrt(sum(v*v for v in x.values())*sum(v*v for v in y.values()))
    return round(dot/norm,4) if norm else 0.0

def split_requirements(description: str) -> tuple[str,str]:
    """Section-sensitive split; ambiguous/unmarked descriptions count as required."""
    required,preferred=[],[]
    current='required'
    for line in description.splitlines():
        content=line.strip()
        if not content:continue
        match=re.match(r'^(required|must.have|minimum qualifications|essential|requirements|preferred|nice.to.have|bonus|desirable|optional)(?: skills| qualifications| experience)?\s*[:\-–]?\s*(.*)$',content,re.I)
        if match:
            current='preferred' if match.group(1).lower() in ('preferred','nice to have','nice-to-have','bonus','desirable','optional') else 'required'
            if match.group(2): (preferred if current=='preferred' else required).append(match.group(2))
            continue
        (preferred if current=='preferred' else required).append(content)
    return '\n'.join(required),'\n'.join(preferred)

def compare_resume_to_job(resume_text: str, description: str, *,db_path=None,required_weight:float=0.75, job_title:str="", use_local_ai:bool=False, ollama_model:str="llama3.2") -> dict:
    if not resume_text.strip():raise ValueError('Resume has no extractable text')
    if len(description)>30000:raise ValueError('Job description cannot exceed 30,000 characters')
    if not (description.strip() or job_title.strip()):raise ValueError('Enter a job title or job description')
    if len(job_title)>150:raise ValueError('Job title cannot exceed 150 characters')
    if not 0.5<=required_weight<=0.95:raise ValueError('Required weight must be between 0.50 and 0.95')
    # Always load the maintained starter catalog even for a database imported from an older phase.
    seed_skills(db_path)
    required_text,preferred_text=split_requirements(description)
    role=suggest_for_title(job_title.strip() or description.strip().splitlines()[0][:150])
    if use_local_ai:
        role=suggest_with_ollama(job_title.strip() or description.strip().splitlines()[0][:150],model=ollama_model)

    required=set(extract_skills(required_text,db_path=db_path))
    preferred=set(extract_skills(preferred_text,db_path=db_path))-required
    # If there are no explicitly stated skills, provide *suggestions*, never
    # falsely label generic role-based suggestions as employer requirements.
    suggested=set(role['skills'])
    candidate=set(extract_skills(resume_text,db_path=db_path))
    suggested_matched=sorted(suggested & candidate)
    suggested_missing=sorted(suggested - candidate)
    if not required and not preferred and not suggested:
        status='unrecognized-role'
    elif required or preferred:
        status='explicit-description'
    else:
        status='title-suggestions'

    matched_required=sorted(required&candidate)
    missing_required=sorted(required-candidate)
    matched_preferred=sorted(preferred&candidate)
    missing_preferred=sorted(preferred-candidate)
    req_score=len(matched_required)/len(required) if required else None
    pref_score=len(matched_preferred)/len(preferred) if preferred else None
    if req_score is None and pref_score is None:skill_score=(len(suggested_matched)/len(suggested) if suggested else None)
    elif req_score is None:skill_score=pref_score
    elif pref_score is None:skill_score=req_score
    else:skill_score=required_weight*req_score+(1-required_weight)*pref_score
    similarity=cosine_similarity(resume_text,description or job_title)
    overall=round(100*(0.7*skill_score+0.3*similarity)) if skill_score is not None else round(similarity*100)
    explanations=[]
    if missing_required:explanations.append('Required skills not explicitly found: '+', '.join(missing_required[:15]))
    if matched_required:explanations.append('Required skills recognized in the resume: '+', '.join(matched_required[:15]))
    if missing_preferred:explanations.append('Optional skills not explicitly found: '+', '.join(missing_preferred[:15]))
    if not required and not preferred and suggested:explanations.append('No employer-stated skills detected. Showing typical occupation skills from a role library or optional local model; verify against an actual job posting.')
    if not required and not preferred and not suggested:explanations.append('Role not recognized in the offline catalog. Paste a detailed job description or optionally use a locally installed Ollama model for suggestions.')
    explanations.append('Missing skills mean not detected in the document, not proof the candidate lacks them.')
    return {'match_score':overall,'similarity_score':round(similarity*100), 'skill_match_score':round(skill_score*100) if skill_score is not None else None,
      'required_weight':required_weight,'resume_skills':sorted(candidate),'required_skills':sorted(required),'preferred_skills':sorted(preferred),
      'matched_required':matched_required,'missing_required':missing_required,'matched_preferred':matched_preferred,'missing_preferred':missing_preferred,
      'suggested_role_skills':sorted(suggested),'matched_suggested':suggested_matched,'missing_suggested':suggested_missing,
      'inference_source':role['source'],'inference_confidence':role['confidence'],'requirements_status':status,
      'explanations':explanations,'disclaimer':'Heuristic estimate. Suggested role skills are not employer-confirmed requirements; not a hiring decision or certified ATS score.'}
