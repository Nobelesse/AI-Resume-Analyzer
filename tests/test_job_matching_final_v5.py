"""Offline cross-profession adversarial checks; no private resumes included."""
from app.database.connection import initialize_database
from app.services.job_matcher import compare_resume_to_job, requirement_evidence

DATA_RESUME = '''Data Analyst. SQL, Python, Pandas, NumPy, Microsoft Excel,
Power BI, DAX, Tableau, Power Query, ETL, A/B Testing, Statistics.
Built Excel pivot-table reports and Power BI dashboards.
Presented regional sales trends and investigated customer retention.'''
MARKETING_RESUME = '''Marketing Coordinator. Content Marketing, Copywriting,
SEO, Email Marketing, Canva, Google Analytics, Google Ads, Meta Ads, CRM.
Coordinated digital campaigns and social media marketing across Instagram.
Created content calendars and monitored marketing performance.'''
DATA_JD = '''**Required Skills:**
- SQL and Python
- Microsoft Excel, Power BI, and Tableau
- Data Visualization and Pivot Tables
**Preferred Skills:**
- DAX and Power Query
**Responsibilities:**
- Build data dashboards and explain sales trends'''
MARKETING_JD = '''Required Skills:*
- Content Marketing and Copywriting
- Search Engine Optimization and Google Analytics
- Canva and Social Media Marketing
**Preferred Skills:**
- Meta Ads and Email Marketing
Responsibilities:*
- Coordinate promotional campaigns'''


def _db(tmp_path):
    path=tmp_path/'v5.sqlite3'
    initialize_database(path)
    return path


def test_metadata_headings_are_never_requirements(tmp_path):
    db = _db(tmp_path)
    for jd in (DATA_JD, MARKETING_JD):
        result = compare_resume_to_job(DATA_RESUME, jd, db_path=db)
        text = ' '.join(r['text'] for r in result['requirement_evidence'])
        assert 'Required Skills:' not in text
        assert 'Responsibilities:' not in text
        assert all('Required Skills:' not in s and 'Responsibilities:' not in s
                   for s in result['improvement_suggestions'])


def test_evidence_excerpts_are_real_source_substrings(tmp_path):
    result = compare_resume_to_job(DATA_RESUME, DATA_JD, db_path=_db(tmp_path))
    excerpts = result['matched_skill_evidence']
    assert excerpts
    assert 'SQL' in excerpts
    assert all(excerpt in DATA_RESUME for excerpt in excerpts.values())
    assert 'Unobserved skill' not in excerpts


def test_cross_profession_positive_outperforms_negative(tmp_path):
    db = _db(tmp_path)
    analyst_data = compare_resume_to_job(DATA_RESUME, DATA_JD, db_path=db)['match_score']
    marketer_data = compare_resume_to_job(MARKETING_RESUME, DATA_JD, db_path=db)['match_score']
    marketer_marketing = compare_resume_to_job(MARKETING_RESUME, MARKETING_JD, db_path=db)['match_score']
    analyst_marketing = compare_resume_to_job(DATA_RESUME, MARKETING_JD, db_path=db)['match_score']
    assert analyst_data > marketer_data, (analyst_data, marketer_data)
    assert marketer_marketing > analyst_marketing, (marketer_marketing, analyst_marketing)
    assert analyst_data >= 50
    assert marketer_marketing >= 50


def test_no_technology_skill_invention(tmp_path):
    result=compare_resume_to_job('Java programming and MS Excel',
        'Required Skills:\n- JavaScript\n- Google Analytics\n- Microsoft Excel', db_path=_db(tmp_path))
    assert 'JavaScript' in result['missing_required']
    assert 'Google Analytics' in result['missing_required']
    assert 'Microsoft Excel' in result['matched_required']
    assert 'JavaScript' not in result['matched_skill_evidence']


def test_section_sensitive_preferred_weighting(tmp_path):
    result=compare_resume_to_job('SQL, Python',
        'Required Skills:\n- SQL\nPreferred Skills:\n- Python\n- Tableau', db_path=_db(tmp_path))
    assert 'SQL' in result['required_skills']
    assert 'Python' in result['preferred_skills']
    assert 'Tableau' in result['missing_preferred']
    assert 'Tableau' not in result['missing_required']
