import pytest
from app.database.connection import connect,initialize_database
from app.services.taxonomy import ensure_tables
from app.services.hybrid_intelligence import rank_careers
from app.services.career_finder import recommend_careers
from app.services.occupation_ai import analyze_occupation

def test_offline_career_ranking(tmp_path):
    path=tmp_path/'catalog.sqlite3'
    initialize_database(path)
    with connect(path) as db:
        ensure_tables(db)
        db.execute("INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES('ONET','a','Python Developer','python developer')")
        db.execute("INSERT INTO tax_skills(source,source_id,name,normalized) VALUES('ONET','p','Python','python')")
        db.execute("INSERT INTO tax_links(occupation_id,skill_id,relation) VALUES(1,1,'essential-skill')")
    out=rank_careers('Python developer and software programmer', db_path=path)
    assert not out['jobs']
    assert 'Insufficient' in out['warning']
    assert out['source']=='curated-offline-catalog'

def test_default_finder_does_not_call_ollama(tmp_path, monkeypatch):
    import app.services.ollama_client as ollama
    monkeypatch.setattr(ollama,'query_with_fallback',lambda *a,**k: (_ for _ in ()).throw(AssertionError('Called Ollama')) )
    db=tmp_path/'career.sqlite3'
    initialize_database(db)
    result=recommend_careers('Python SQL Git',db_path=db)
    assert result['source'] in ('curated-offline-catalog','ONET/ESCO-imported-catalog')
    assert isinstance(result['jobs'],list)


def test_default_occupation_is_offline(tmp_path):
    result=analyze_occupation('Python Developer')
    assert result['source']!='ollama-llama3.2:3b'
