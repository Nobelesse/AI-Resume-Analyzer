"""v3.1: same-occupation aliases and trustworthy display labels."""
from app.services.hybrid_intelligence import (
    _occupation_identity, _deduplicate_career_candidates,
    _professional_occupation_title, rank_careers,
)
from app.database.connection import connect, initialize_database


def _job(title, score, matched=('Microsoft Excel',)):
    evidence = {
        'title': title, 'skills_detected': list(matched),
        'core_skills_matched': [], 'evidence_source': 'ONET',
        'match_strength': score,
    }
    return (score, len(matched), title.casefold(), evidence)


def test_receptionist_alias_and_official_title_merge():
    assert _occupation_identity('receptionist') == _occupation_identity('Receptionists and Information Clerks')
    result = _deduplicate_career_candidates([
        _job('receptionist', 35.1),
        _job('Receptionists and Information Clerks', 35.0),
    ])
    assert len(result) == 1
    assert result[0][3]['title'] == 'Receptionists and Information Clerks'
    assert result[0][0] == 35.0


def test_strong_evidence_wins_even_if_lowercase_label():
    result = _deduplicate_career_candidates([
        _job('receptionist', 46.0, ('Microsoft Excel', 'Customer Service')),
        _job('Receptionists and Information Clerks', 21.0),
    ])
    assert len(result) == 1
    assert result[0][3]['title'] == 'receptionist'
    assert result[0][3]['skills_detected'] == ['Microsoft Excel', 'Customer Service']
    assert result[0][0] == 46.0


def test_related_but_different_occupations_are_not_merged():
    pairs = [
        ('receptionist', 'Medical Receptionists'),
        ('receptionist', 'Hotel, Motel, and Resort Desk Clerks'),
        ('administrative assistant', 'Executive Secretaries and Executive Administrative Assistants'),
        ('Web Developers', 'Web and Digital Interface Designers'),
        ('Web Developers', 'webmaster'),
        ('Data Analysts', 'Business Intelligence Analysts'),
        ('Accountants and Auditors', 'Bookkeeping, Accounting, and Auditing Clerks'),
    ]
    for left, right in pairs:
        assert _occupation_identity(left) != _occupation_identity(right), (left, right)


def test_occupation_title_formatting_preserves_acronyms_and_official_labels():
    assert _professional_occupation_title('webmaster') == 'Webmaster'
    assert _professional_occupation_title('administrative assistant') == 'Administrative Assistant'
    assert _professional_occupation_title('it support specialist') == 'IT Support Specialist'
    assert _professional_occupation_title('qa tester') == 'QA Tester'
    assert _professional_occupation_title('Receptionists and Information Clerks') == 'Receptionists and Information Clerks'


def test_catalog_results_do_not_show_duplicate_receptionist(tmp_path):
    db_path = tmp_path / 'occupation_v31.sqlite3'
    initialize_database(db_path)
    with connect(db_path) as db:
        skill_ids = {}
        for skill in ('Customer Service', 'Microsoft Excel', 'Microsoft Word', 'Communication', 'HTML', 'CSS'):
            skill_ids[skill] = db.execute(
                'INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)',
                ('ONET', skill, skill, skill.casefold()),
            ).lastrowid
        for index, title in enumerate(('receptionist', 'Receptionists and Information Clerks', 'webmaster', 'Web Developers')):
            occupation_id = db.execute(
                'INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES(?,?,?,?)',
                ('ONET', f'occ{index}', title, title.casefold()),
            ).lastrowid
            skills = ('Customer Service', 'Microsoft Excel', 'Microsoft Word') if 'eception' in title else ('HTML', 'CSS')
            for skill in skills:
                db.execute('INSERT INTO tax_links VALUES(?,?,?)', (occupation_id, skill_ids[skill], 'essential'))
    result = rank_careers(
        'SKILLS: customer service communication MS Excel MS Word HTML CSS. Experience: fresher.',
        db_path=db_path, limit=20,
    )
    identities = [_occupation_identity(job['title']) for job in result['jobs']]
    assert len(identities) == len(set(identities)), result['jobs']
    assert all(job['title'] != job['title'].lower() for job in result['jobs'])
