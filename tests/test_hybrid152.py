"""Career domain separation regression with a small, independent catalog fixture."""
from app.database.connection import connect, initialize_database
from app.services.hybrid_intelligence import rank_careers


ROLES = {
    'Software Developers': ['Python', 'SQL', 'Git', 'Docker', 'PostgreSQL'],
    'Geneticists': ['Python', 'SQL', 'Statistics'],
    'Data Scientists': ['Python', 'SQL', 'Pandas', 'Statistics', 'Power BI'],
    'Biofuels Processing Technicians': ['SQL', 'Microsoft Excel'],
    'Search Marketing Strategists': ['Search Engine Optimization', 'Digital Marketing', 'Google Analytics', 'Marketing Analytics'],
    'Producers and Directors': ['Communication', 'Project Management'],
}


def _db(path):
    initialize_database(path)
    with connect(path) as db:
        for i, (title, skills) in enumerate(ROLES.items()):
            cur = db.execute('INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES(?,?,?,?)', ('ONET', str(i), title, title.casefold()))
            oid = cur.lastrowid
            for skill in skills:
                db.execute('INSERT OR IGNORE INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)', ('ONET', skill, skill, skill.casefold()))
                sid = db.execute('SELECT id FROM tax_skills WHERE normalized=?', (skill.casefold(),)).fetchone()[0]
                db.execute('INSERT OR IGNORE INTO tax_links VALUES(?,?,?)', (oid, sid, 'software-example'))


def test_backend_developer_over_genetics(tmp_path):
    path=tmp_path/'roles.sqlite3'; _db(path)
    result=rank_careers('Backend developer: Python SQL Git PostgreSQL Docker FastAPI REST API SQLAlchemy projects',db_path=path)
    titles=[r['title'] for r in result['jobs']]
    assert titles.index('Software Developers') < titles.index('Geneticists')
    assert result['jobs'][0]['domain_alignment']=='aligned'


def test_data_analyst_over_biofuels(tmp_path):
    path=tmp_path/'roles.sqlite3'; _db(path)
    result=rank_careers('Data Analyst: Python SQL Pandas Power BI Tableau statistics data visualization',db_path=path)
    titles=[r['title'] for r in result['jobs']]
    assert 'Data Scientists' in titles
    assert 'Biofuels Processing Technicians' not in titles


def test_marketing_domain_over_producers(tmp_path):
    path=tmp_path/'roles.sqlite3'; _db(path)
    result=rank_careers('Digital Marketing SEO Search Engine Optimization Google Analytics marketing analytics and content marketing, project management, communication',db_path=path)
    titles=[r['title'] for r in result['jobs']]
    assert 'Search Marketing Strategists' in titles
    assert 'Producers and Directors' not in titles


def test_coverage_remains_factual(tmp_path):
    path=tmp_path/'roles.sqlite3'; _db(path)
    result=rank_careers('Backend developer Python SQL FastAPI REST API',db_path=path)
    dev=next(r for r in result['jobs'] if r['title']=='Software Developers')
    assert dev['skills_coverage']==40
    assert dev['matched_skill_count']==2
