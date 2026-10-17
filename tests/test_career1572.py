from app.services.hybrid_intelligence import _onet_query_keys, rank_careers
from app.services.taxonomy import ensure_tables
from app.database.connection import connect, initialize_database


def test_explicit_aliases_without_false_product_inference():
    terms = _onet_query_keys('HTML, CSS, MS Word, customer service and bookkeeping', {'html', 'css', 'customer service'})
    assert 'hypertext markup language html' in terms
    assert 'cascading style sheets css' in terms
    assert 'microsoft word' in terms
    assert 'customer service and support software' not in terms
    assert 'bookkeeping software' not in terms


def test_aliases_retrieve_real_catalog_names(tmp_path):
    dbpath = tmp_path / 'catalog.sqlite3'
    initialize_database(dbpath)
    with connect(dbpath) as db:
        ensure_tables(db)
        db.execute("INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES('ONET','a','Web Developers','web developers')")
        oid=db.execute('SELECT id FROM tax_occupations').fetchone()[0]
        for index, name in enumerate(('Hypertext markup language HTML', 'Cascading style sheets CSS'),1):
            db.execute('INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)',('ONET',str(index),name,name.casefold()))
            sid=db.execute('SELECT id FROM tax_skills WHERE source_id=?',(str(index),)).fetchone()[0]
            db.execute('INSERT INTO tax_links VALUES(?,?,?)',(oid,sid,'software-example'))
    result = rank_careers('HTML CSS web development',db_path=dbpath)
    assert result['diagnostics']['catalog_skill_matches'] >= 2
    assert result['diagnostics']['occupations_retrieved'] >= 1
    assert result['jobs'][0]['title'] == 'Web Developers'
    assert result['source'] == 'ONET/ESCO-imported-catalog'


def test_fallback_explains_missing_catalog(tmp_path):
    dbpath=tmp_path/'empty.sqlite3'
    initialize_database(dbpath)
    result = rank_careers('Accounting, bookkeeping, customer service, communication', db_path=dbpath)
    assert result['source'] == 'curated-offline-catalog'
    assert result['diagnostics']['fallback_reason']
