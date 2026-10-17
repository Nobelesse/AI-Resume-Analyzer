"""Deterministic, explainable ATS-readiness and job-compatibility assessments.

No proprietary ATS simulation, hiring predictions, or automatically verified credentials.
"""
import re
from app.services.ats import analyze_text
from app.services.job_matcher import compare_resume_to_job, requirement_evidence
from app.services.skills import extract_skills


def resume_readiness(text: str, *, db_path=None) -> dict:
    """Re-use established ATS readability checks; report evidence and limitations."""
    base = analyze_text(text, db_path=db_path)
    checks = []
    for section, detected in base['sections'].items():
        checks.append({'check': f'{section.title()} section', 'status': 'detected' if detected else 'not detected',
                       'detail': 'Section label recognized' if detected else 'Consider adding a clearly labeled section when relevant'})
    checks.extend([
        {'check': 'Contact email', 'status': 'detected' if re.search(r'\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b',text) else 'not detected', 'detail':'Text-based detection only'},
        {'check': 'Machine-readable content', 'status': 'detected' if len(text.split()) >= 30 else 'review', 'detail':'Extracted text length; PDF layout and reading order are not verified'},
    ])
    return {'score':base['score'], 'checks':checks, 'components':base['components'],
            'recommendations':base['recommendations'], 'skills':base['skills'],
            'word_count':base['word_count'], 'sections':base['sections'],
            'disclaimer':'Resume-readiness heuristic only; not an official ATS vendor score or guarantee of parsing in an employer system.'}


def job_compatibility(text: str, description: str, *, db_path=None) -> dict:
    """Only show a job-specific score when explicit job description evidence exists.

    Ambiguous or unsupported requirements remain manual-review items and are not
    silently marked as satisfied. Missing text evidence does not imply inability.
    """
    if not description.strip():
        raise ValueError('Paste a job description for a job-specific assessment.')
    if len(description) > 30000:
        raise ValueError('Job description cannot exceed 30,000 characters.')
    candidate = set(extract_skills(text, db_path=db_path))
    evidence = requirement_evidence(description, candidate, db_path=db_path)
    applicable = [r for r in evidence if r['status'] != 'unverified']
    required = [r for r in applicable if r['priority'] == 'required']
    preferred = [r for r in applicable if r['priority'] == 'preferred']
    def ratio(items):
        if not items:return None
        return sum((1.0 if r['status']=='evidenced' else 0.5 if r['status']=='partial' else 0.0) for r in items) / len(items)
    r, p = ratio(required), ratio(preferred)
    if r is None and p is None:
        score = None
    elif r is None: score = round(100*p)
    elif p is None: score = round(100*r)
    else: score = round(100*(0.8*r+0.2*p))
    return {
        'score':score,
        'score_available':score is not None,
        'required_count':len(required), 'preferred_count':len(preferred),
        'manual_review_count':len(evidence)-len(applicable),
        'requirements':evidence,
        'matched':sum(r['status']=='evidenced' for r in applicable),
        'partial':sum(r['status']=='partial' for r in applicable),
        'not_found':sum(r['status']=='not-found' for r in applicable),
        'methodology':'80% required / 20% preferred where both exist; requirement-line evidence only. Unverified requirements excluded from automatic scoring.',
        'disclaimer':'Not an employer ATS score, interview probability, or eligibility decision. Not found means absent from the document, not absent from the applicant.',
    }
