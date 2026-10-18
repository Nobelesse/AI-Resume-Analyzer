from app.services.resume_evidence import extract_resume_evidence, career_evidence
from app.config import APP_VERSION

SAMPLE = """OBJECTIVE
To use my skills in accounting, communication, and customer service.
SKILLS
• HTML, CSS
• MS Word
• Basic MS Excel
• Basic Computer Knowledge
• Basic Accounting & Bookkeeping
• Good communication.
EDUCATION
2024 MCA running
2021-2024 BCA
WORK EXPERIENCE
Fresher
HOBBIES & INTERESTS
Travelling by Train
"""

def test_version():
    assert APP_VERSION == '1.5.9.9.3'

def test_fresher_resume_evidence():
    p = extract_resume_evidence(SAMPLE)
    for x in ('HTML','CSS','Microsoft Word','Microsoft Excel','Basic computer knowledge','Accounting','Bookkeeping','Communication'):
        assert x in p['skills']
    assert p['career_interests'] == ['Customer service']
    assert 'Microsoft Excel' in p['basic_skills']
    assert p['education'] == ['BCA', 'MCA (ongoing)']
    assert p['experience_level'] == 'Fresher (stated)'

def test_role_relevant_evidence_does_not_show_every_skill():
    p = extract_resume_evidence(SAMPLE)
    web = career_evidence('Web Developers', p)
    assert 'HTML' in web['relevant_skills'] and 'CSS' in web['relevant_skills']
    assert 'Accounting' not in web['relevant_skills']
    office = career_evidence('Secretaries and Administrative Assistants, Except Legal, Medical, and Executive', p)
    assert {'Microsoft Word','Microsoft Excel','Communication','Bookkeeping'} <= set(office['relevant_skills'])
    assert 'Customer service' in office['career_interests']

def test_no_false_qualification_claims():
    p = extract_resume_evidence('SKILLS\nHTML\nEDUCATION\nMCA\nEXPERIENCE\nNo details')
    assert p['experience_level'] == 'Not verified'
    assert 'MCA (completion not verified)' in p['education']
    assert 'Customer service' not in p['skills']

def test_personal_details_do_not_become_skills():
    p = extract_resume_evidence('SKILLS\nHTML\nPERSONAL DETAILS\nI live on Excel Street and travel to CSS Avenue')
    assert p['skills'] == ['HTML']
