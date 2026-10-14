"""Version 1.5.7.1: realistic fresher and low-evidence protections."""
from app.database.connection import connect, initialize_database
from app.services.hybrid_intelligence import rank_careers


def test_realistic_fresher_finds_relevant_careers_only(tmp_path):
    path = tmp_path / 'fixture.sqlite3'
    initialize_database(path)
    occupations = {
        'Customer Service Representatives': ['Customer Service', 'Communication', 'Microsoft Excel'],
        'Bookkeeping, Accounting, and Auditing Clerks': ['Bookkeeping', 'Accounting', 'Microsoft Excel'],
        'Web Developers': ['HTML', 'CSS', 'JavaScript'],
        'Crematory Operators': ['Communication'],
        'Taxi Drivers': ['Communication'],
    }
    with connect(path) as db:
        for i, (title, skills) in enumerate(occupations.items()):
            oid = db.execute('INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES(?,?,?,?)', ('ONET',str(i),title,title.casefold())).lastrowid
            for skill in skills:
                db.execute('INSERT OR IGNORE INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)', ('ONET',skill,skill,skill.casefold()))
                sid = db.execute('SELECT id FROM tax_skills WHERE normalized=?',(skill.casefold(),)).fetchone()[0]
                db.execute('INSERT OR IGNORE INTO tax_links VALUES(?,?,?)',(oid,sid,'skill'))
    # No private identifiers from the uploaded resume are stored in this fixture.
    text = 'OBJECTIVE: accounting, communication and customer service. SKILLS: HTML CSS basic MS Excel, bookkeeping and accounting. EDUCATION: BCA; MCA ongoing. Fresher.'
    result = rank_careers(text, db_path=path)
    titles = [job['title'] for job in result['jobs']]
    assert 'Crematory Operators' not in titles
    assert 'Taxi Drivers' not in titles
    assert 'Bookkeeping, Accounting, and Auditing Clerks' in titles
    assert 'Web Developers' in titles


def test_sparse_unrelated_catalog_abstains(tmp_path):
    path = tmp_path / 'sparse.sqlite3'
    initialize_database(path)
    with connect(path) as db:
        oid = db.execute("INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES('ONET','a','Crematory Operators','crematory operators')").lastrowid
        sid = db.execute("INSERT INTO tax_skills(source,source_id,name,normalized) VALUES('ONET','s','Communication','communication')").lastrowid
        db.execute('INSERT INTO tax_links VALUES(?,?,?)',(oid,sid,'skill'))
    result = rank_careers('Fresher. Good communication skills and basic MS Word.', db_path=path)
    assert result['jobs'] == []
    assert 'Insufficient' in result['warning']
