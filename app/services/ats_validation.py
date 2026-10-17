"""Offline, privacy-safe regression benchmark for ATS assessment behavior.

These hand-reviewed synthetic contrasts test consistency and known error types;
they do not measure agreement with proprietary ATS systems.
"""
from __future__ import annotations

from app.services.ats_intelligence import job_compatibility, resume_readiness

GOOD_RESUME = '''Alex Example\nalex@example.test\n+91 9876543210\nSUMMARY\nBackend developer who built Python APIs and SQL applications.\nSKILLS\nPython, SQL, Docker, Git, FastAPI\nEXPERIENCE\n- Implemented 3 REST API projects for 20 users.\nEDUCATION\nBachelor degree in computer applications\nPROJECTS\n- Built a Python API and a SQL-backed reporting application.\n'''
UNRELATED_RESUME = '''Taylor Example\ntaylor@example.test\nSUMMARY\nContent creator focused on marketing campaigns.\nSKILLS\nCanva, Content Marketing, Graphic Design, Google Analytics\nEXPERIENCE\n- Created design assets for social media campaigns.\nEDUCATION\nBachelor degree\nPROJECTS\n- Created a marketing portfolio.\n'''
BACKEND_JOB = '''Required:\n- Python\n- SQL\n- Docker\nPreferred:\n- FastAPI\n- AWS certification\n'''
MARKETING_JOB = '''Required:\n- Canva\n- Content Marketing\nPreferred:\n- Google Analytics\n'''


def run_benchmark(*, db_path=None) -> dict:
    """Return checks with transparent pass/fail instead of an invented accuracy score."""
    backend = job_compatibility(GOOD_RESUME, BACKEND_JOB, db_path=db_path)
    unrelated = job_compatibility(UNRELATED_RESUME, BACKEND_JOB, db_path=db_path)
    marketing = job_compatibility(UNRELATED_RESUME, MARKETING_JOB, db_path=db_path)
    ready = resume_readiness(GOOD_RESUME, db_path=db_path)
    checks = {
        'related resume outranks unrelated resume for backend requirements': backend['score'] is not None and unrelated['score'] is not None and backend['score'] > unrelated['score'],
        'marketing resume ranks higher for marketing than backend role': marketing['score'] is not None and unrelated['score'] is not None and marketing['score'] > unrelated['score'],
        'certification remains manually unverified': backend['manual_review_count'] >= 1,
        'readiness does not claim PDF visual verification': any('layout and reading order are not verified' in row['detail'] for row in ready['checks']),
        'detected requirements retain evidence explanations': all('status' in row and 'text' in row for row in backend['requirements']),
    }
    return {'passed': sum(checks.values()), 'total': len(checks), 'checks': checks, 'limitations': 'Synthetic, reviewer-designed contrast checks only. These do not establish real-world validity or employer ATS accuracy.'}
