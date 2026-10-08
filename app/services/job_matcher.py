"""Explainable, offline job-description to resume comparison."""
from __future__ import annotations
import math
import re
from collections import Counter
from app.services.skills import extract_skills

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

def compare_resume_to_job(resume_text: str, description: str, *,db_path=None,required_weight:float=0.75) -> dict:
    if not resume_text.strip():raise ValueError('Resume has no extractable text')
    if len(description.strip())<30 or len(description)>30000:raise ValueError('Job description must contain 30–30,000 characters')
    if not 0.5<=required_weight<=0.95:raise ValueError('Required weight must be between 0.50 and 0.95')
    required_text,preferred_text=split_requirements(description)
    required=set(extract_skills(required_text,db_path=db_path))
    preferred=set(extract_skills(preferred_text,db_path=db_path))-required
    candidate=set(extract_skills(resume_text,db_path=db_path))
    matched_required=sorted(required&candidate)
    missing_required=sorted(required-candidate)
    matched_preferred=sorted(preferred&candidate)
    missing_preferred=sorted(preferred-candidate)
    req_score=len(matched_required)/len(required) if required else None
    pref_score=len(matched_preferred)/len(preferred) if preferred else None
    if req_score is None and pref_score is None:skill_score=None
    elif req_score is None:skill_score=pref_score
    elif pref_score is None:skill_score=req_score
    else:skill_score=required_weight*req_score+(1-required_weight)*pref_score
    similarity=cosine_similarity(resume_text,description)
    overall=round(100*(0.7*skill_score+0.3*similarity)) if skill_score is not None else round(similarity*100)
    explanations=[]
    if missing_required:explanations.append('Required skills not explicitly found: '+', '.join(missing_required[:15]))
    if matched_required:explanations.append('Required skills recognized in the resume: '+', '.join(matched_required[:15]))
    if missing_preferred:explanations.append('Optional skills not explicitly found: '+', '.join(missing_preferred[:15]))
    if not required and not preferred:explanations.append('No catalog skills detected in the job description; this score uses text similarity only.')
    explanations.append('Missing skills mean not detected in the document, not proof the candidate lacks them.')
    return {'match_score':overall,'similarity_score':round(similarity*100), 'skill_match_score':round(skill_score*100) if skill_score is not None else None,
      'required_weight':required_weight,'resume_skills':sorted(candidate),'required_skills':sorted(required),'preferred_skills':sorted(preferred),
      'matched_required':matched_required,'missing_required':missing_required,'matched_preferred':matched_preferred,'missing_preferred':missing_preferred,
      'explanations':explanations,'disclaimer':'Heuristic estimate, not a hiring decision, ATS certification, or reliable measure of candidate ability.'}
