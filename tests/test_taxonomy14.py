"""End-to-end imported taxonomies and resume matching, using representative CSV fixtures."""
import csv
from app.database.connection import initialize_database
from app.services.taxonomy import import_esco,import_onet,counts,role_skills,lookup_occupation
from app.services.skills import extract_skills
from app.services.job_matcher import compare_resume_to_job


def csvfile(tmp_path, name, header, records):
    path=tmp_path/name
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(records)
    return path


def test_esco_import_alias_matching_and_repeat(tmp_path):
    db=tmp_path/'test.sqlite3';initialize_database(db)
    occupations=csvfile(tmp_path,'occupations_en.csv',['conceptUri','preferredLabel','altLabels'],[
        ['occ:a','Quantum Technician','Quantum Lab Specialist|Q-Tech']])
    skills=csvfile(tmp_path,'skills_en.csv',['conceptUri','preferredLabel','altLabels'],[
        ['skill:a','Quantum Calibration','QC tuning'],['skill:b','Photon Analysis','Optical analysis']])
    relations=csvfile(tmp_path,'occupationSkillRelations_en.csv',['occupationUri','skillUri','relationType'],[
        ['occ:a','skill:a','essential'],['occ:a','skill:b','optional']])
    res=import_esco(occupations,skills,relations,db_path=db,version='test-ESCO')
    assert res == {'occupations':1,'skills':2,'links':2}
    import_esco(occupations,skills,relations,db_path=db,version='test-ESCO')
    assert counts(db)=={'occupations':1,'skills':2,'links':2}
    assert lookup_occupation('Q-Tech',db_path=db)[0]['name']=='Quantum Technician'
    assert 'Quantum Calibration' in extract_skills('Experienced in QC tuning',db_path=db)
    suggested=role_skills('Quantum Technician',db_path=db)
    assert 'Photon Analysis' in suggested['skills']
    matched=compare_resume_to_job('Quantum Calibration and Photon Analysis', '', job_title='Quantum Technician',db_path=db)
    assert matched['matched_suggested']
    assert matched['inference_source']=='ESCO-imported'


def test_onet_import_mapping(tmp_path):
    db=tmp_path/'test.sqlite3';initialize_database(db)
    occupations=csvfile(tmp_path,'occupation_data.csv',['O*NET-SOC Code','Title'],[
        ['00-0001.00','Laser Engineer']])
    software=csvfile(tmp_path,'software_skills.csv',['O*NET-SOC Code','Title','Workplace Example'],[
        ['00-0001.00','Laser Engineer','Photon Modeling Software'],
        ['00-0001.00','Laser Engineer','Signal Analysis Toolkit']])
    assert import_onet(occupations,software,db_path=db)=={'occupations':1,'skills':2,'links':2}
    assert role_skills('Laser Engineer',db_path=db)['source']=='ONET-imported'


def test_invalid_esco_rolls_back(tmp_path):
    db=tmp_path/'test.sqlite3';initialize_database(db)
    occupations=csvfile(tmp_path,'occupations.csv',['bad'],[['x']])
    skills=csvfile(tmp_path,'skills.csv',['conceptUri','preferredLabel'],[['s','Tool']])
    relations=csvfile(tmp_path,'relations.csv',['occupationUri','skillUri'],[['x','s']])
    import pytest
    with pytest.raises(ValueError):import_esco(occupations,skills,relations,db_path=db)
    assert counts(db)['occupations']==0


def test_catalog_preferred_over_ai_suggestion(tmp_path):
    db=tmp_path/'test.sqlite3'; initialize_database(db)
    occupations=csvfile(tmp_path,'o.csv',['conceptUri','preferredLabel'],[['occ:z','Laser Engineer']])
    skills=csvfile(tmp_path,'s.csv',['conceptUri','preferredLabel'],[['skill:z','Laser Alignment']])
    links=csvfile(tmp_path,'l.csv',['occupationUri','skillUri','relationType'],[['occ:z','skill:z','essential']])
    import_esco(occupations,skills,links,db_path=db)
    result=compare_resume_to_job('Laser Alignment', '',job_title='Laser Engineer',db_path=db,
        occupation_profile={'skills':['Unverified Model Skill'],'source':'ollama-fake'})
    assert result['suggested_role_skills']==['Laser Alignment']
    assert result['inference_source']=='ESCO-imported'
