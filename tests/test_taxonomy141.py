"""Official O*NET supplemental CSV shapes: idempotence, aliases and safe counts."""
import csv
from app.database.connection import initialize_database
from app.services.taxonomy import import_onet_expanded,lookup_occupation,role_skills,counts,catalog_details


def csvfile(folder,filename,head,rows):
    with (folder/filename).open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f);writer.writerow(head);writer.writerows(rows)


def test_essential_knowledge_and_titles(tmp_path):
    db=tmp_path/'app.sqlite3';initialize_database(db)
    csvfile(tmp_path,'occupation_data.csv',['O*NET-SOC Code','Title'],[['11-1011.00','Chief Executives']])
    csvfile(tmp_path,'job_titles.csv',['O*NET-SOC Code','Title'],[['11-1011.00','CEO']])
    csvfile(tmp_path,'content_model_reference.csv',['Element ID','Element Name'],[['2.A.1.a','Reading Comprehension'],['2.C.1.a','Administration and Management']])
    csvfile(tmp_path,'essential_skills.csv',['O*NET-SOC Code','Element ID','Scale ID','Data Value'],[['11-1011.00','2.A.1.a','IM',3]])
    csvfile(tmp_path,'knowledge.csv',['O*NET-SOC Code','Element ID','Scale ID','Data Value'],[['11-1011.00','2.C.1.a','IM',3]])
    report=import_onet_expanded(tmp_path,db_path=db)
    assert report['title_aliases']==1
    assert lookup_occupation('CEO',db_path=db)[0]['name']=='Chief Executives'
    assert set(role_skills('Chief Executives',db_path=db)['skills'])=={'Reading Comprehension','Administration and Management'}
    before=counts(db)
    import_onet_expanded(tmp_path,db_path=db)
    assert counts(db)==before
    assert len(catalog_details(db_path=db)['relations'])==2


def test_without_reference_skip_unknown_elements(tmp_path):
    db=tmp_path/'app.sqlite3';initialize_database(db)
    csvfile(tmp_path,'occupation_data.csv',['O*NET-SOC Code','Title'],[['11-1011.00','Chief Executives']])
    csvfile(tmp_path,'essential_skills.csv',['O*NET-SOC Code','Element ID','Data Value'],[['11-1011.00','unknown',4]])
    assert import_onet_expanded(tmp_path,db_path=db)['skipped']==1
    assert counts(db)['skills']==0
