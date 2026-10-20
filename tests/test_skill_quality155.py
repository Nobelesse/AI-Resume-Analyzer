from app.services.career_intelligence155 import evidence_weight, useful_gaps, occupation_focus
from app.config import APP_VERSION

def test_version():
    assert APP_VERSION == '1.5.9.9.9.9'

def test_technical_evidence_outweighs_generic():
    assert evidence_weight('PostgreSQL') > evidence_weight('Science')
    assert evidence_weight('Docker') > evidence_weight('Active Listening')

def test_learning_topics_exclude_generic():
    gaps = useful_gaps({'Science', 'Docker', 'Git', 'Active Listening'}, {'Git'})
    assert 'Docker' in gaps and 'Science' not in gaps and 'Active Listening' not in gaps

def test_role_context_is_tiebreaker_not_mandatory():
    assert occupation_focus('Software Developers', 'Backend Developer using Python') == 1
    assert occupation_focus('Web Developers', 'Backend Developer using Python') == 0
