import csv
import sqlite3
from pathlib import Path
from app.services.taxonomy import import_esco, import_onet_supplements
from scripts.import_unified_datasets import main


def write_csv(path, fields, rows):
    with path.open('w',encoding='utf-8',newline='') as out:
        w=csv.DictWriter(out,fieldnames=fields);w.writeheader();w.writerows(rows)

def test_official_source_ids_aliases_idempotency(tmp_path):
    esco=tmp_path/'ESCO';onet=tmp_path/'ONET';esco.mkdir();onet.mkdir()
    write_csv(esco/'occupations_en.csv',['conceptUri','preferredLabel'],[{'conceptUri':'urn:occupation:data','preferredLabel':'Data Analyst'}])
    write_csv(esco/'skills_en.csv',['conceptUri','preferredLabel','altLabels','hiddenLabels'],[{'conceptUri':'urn:skill:excel','preferredLabel':'Microsoft Excel','altLabels':'MS Excel','hiddenLabels':'Excel spreadsheet'}])
    write_csv(esco/'occupationSkillRelations_en.csv',['occupationUri','skillUri','relationType'],[{'occupationUri':'urn:occupation:data','skillUri':'urn:skill:excel','relationType':'essential'}])
    write_csv(onet/'software_skills.csv',['O*NET-SOC Code','Workplace Example'],[{'O*NET-SOC Code':'15-2051.00','Workplace Example':'Power BI'}])
    write_csv(onet/'essential_skills.csv',['O*NET-SOC Code','Element ID','Element Name','Scale ID'],[{'O*NET-SOC Code':'15-2051.00','Element ID':'2.A.1','Element Name':'Critical Thinking','Scale ID':'IM'},{'O*NET-SOC Code':'15-2051.00','Element ID':'2.A.1','Element Name':'Critical Thinking','Scale ID':'LV'}])
    from app.services.taxonomy import ensure_tables
    db=tmp_path/'private.sqlite3'
    with sqlite3.connect(db) as connection:
        ensure_tables(connection)
        connection.execute("INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES('ONET','15-2051.00','Data Scientists','data scientists')")
    assert main(['--esco-dir',str(esco),'--onet-dir',str(onet),'--db',str(db)])==0
    with sqlite3.connect(db) as connection:
        assert connection.execute('SELECT COUNT(*) FROM tax_skills').fetchone()[0]==0
    assert main(['--esco-dir',str(esco),'--onet-dir',str(onet),'--db',str(db),'--apply'])==0
    assert main(['--esco-dir',str(esco),'--onet-dir',str(onet),'--db',str(db),'--apply'])==0
    with sqlite3.connect(db) as connection:
        assert connection.execute('SELECT COUNT(*) FROM tax_skills').fetchone()[0]==3
        assert connection.execute('SELECT COUNT(*) FROM tax_links').fetchone()[0]==3
        assert connection.execute("SELECT COUNT(*) FROM tax_skill_aliases WHERE alias='ms excel'").fetchone()[0]==1
        assert connection.execute("SELECT COUNT(*) FROM tax_skill_aliases WHERE alias='excel spreadsheet'").fetchone()[0]==1
    assert list(tmp_path.glob('*before-1599-*.sqlite3'))
