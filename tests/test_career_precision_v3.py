"""Regression tests: conservative career deduplication and shared skill evidence."""
from app.database.connection import connect, initialize_database
from app.services.hybrid_intelligence import (
    rank_careers, _occupation_identity, _deduplicate_career_candidates,
    _domain_evidence,
)
from app.services.job_matcher import compare_resume_to_job

RESUME = ('OBJECTIVE: accounting communication customer service. '
          'SKILLS HTML CSS basic MS Excel MS Word basic accounting bookkeeping. '
          'BCA MCA ongoing. Fresher.')


def _fixture(path):
    initialize_database(path)
    occupations = {
        'web developer': ('HTML', 'CSS', 'JavaScript', 'React'),
        'Web Developers': ('HTML', 'CSS', 'JavaScript', 'Git', 'Responsive Design'),
        'webmaster': ('HTML', 'CSS', 'Website Management'),
        'Bookkeeping, Accounting, and Auditing Clerks': ('Accounting', 'Bookkeeping', 'Microsoft Excel'),
        'Computer User Support Specialists': ('Troubleshooting', 'Technical Support', 'Ticketing Systems'),
    }
    with connect(path) as db:
        skills = {}
        for index, (title, names) in enumerate(occupations.items()):
            oid = db.execute('INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES(?,?,?,?)',
                             ('ONET', f'occ{index}', title, title.casefold())).lastrowid
            for skill in names:
                if skill not in skills:
                    skills[skill] = db.execute('INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)',
                                               ('ONET', f'skill{len(skills)}', skill, skill.casefold())).lastrowid
                db.execute('INSERT INTO tax_links VALUES(?,?,?)', (oid, skills[skill], 'essential'))


def test_plural_and_case_variant_only():
    assert _occupation_identity('Web Developers') == _occupation_identity('web developer')
    assert _occupation_identity('Web Developers') != _occupation_identity('webmaster')
    assert _occupation_identity('Web Developers') != _occupation_identity('Web and Digital Interface Designers')
    assert _occupation_identity('Data Analysts') != _occupation_identity('Business Intelligence Analysts')


def test_duplicate_title_merged_with_catalog_evidence(tmp_path):
    path = tmp_path / 'fixtures.db'
    _fixture(path)
    result = rank_careers(RESUME, db_path=path, limit=20)
    titles = [j['title'] for j in result['jobs']]
    web = [j for j in result['jobs'] if _occupation_identity(j['title']) == 'web developer']
    assert len(web) == 1, titles
    assert result['diagnostics']['unique_occupations'] < result['diagnostics']['occupations_after_filter']
    assert web[0]['core_skill_coverage'] == 29
    assert set(web[0]['core_skills_matched']) == {'HTML', 'CSS'}
    assert 'JavaScript' in web[0]['core_skills_not_detected']
    studio = compare_resume_to_job(RESUME, '', job_title='Web Developer', db_path=path)
    assert studio['match_score'] == web[0]['core_skill_coverage'] or abs(studio['match_score'] - web[0]['core_skill_coverage']) <= 1
    assert 'Bookkeeping, Accounting, and Auditing Clerks' in titles
    assert 'Computer User Support Specialists' not in titles


def test_degree_is_not_technical_support_skill_evidence():
    assert _domain_evidence('BCA graduate MCA ongoing fresher basic computer knowledge', set())['it_support'] == 0


def test_dedup_prefers_publisher_style_when_scores_nearly_equal():
    a = (35.2, 2, 'web developer', {'title': 'web developer'})
    b = (34.9, 2, 'web developers', {'title': 'Web Developers'})
    c = (32.0, 2, 'webmaster', {'title': 'webmaster'})
    dedup = _deduplicate_career_candidates([a, b, c])
    assert {entry[3]['title'] for entry in dedup} == {'Web Developers', 'webmaster'}
