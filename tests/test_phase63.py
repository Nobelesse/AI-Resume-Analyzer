from app.services.occupation_ai import analyze_occupation
from app.services.career_finder import recommend_careers
from app.services.ollama_client import LocalAIError
from app.database.connection import initialize_database

def test_neurosurgeon_with_local_model():
    def fake(prompt):
        return ({'occupation':'Neurosurgeon','overview':'Specialized physician','technical_skills':['Microsurgery','Medical imaging'], 'soft_skills':['Communication'], 'responsibilities':['Evaluate patients'], 'qualifications':['Medical licensing'],'career_notes':[]}, 'llama3.2:3b')
    result=analyze_occupation('Neurosurgeon',ai_provider=fake)
    assert 'Microsurgery' in result['skills']
    assert result['source']=='ollama-llama3.2:3b'

def test_unknown_job_fallback_graceful():
    def fail(prompt): raise LocalAIError('timed out')
    result=analyze_occupation('Police Officer',ai_provider=fail)
    assert result['warning'] and result['source']=='unknown-role'

def test_career_unknown_role_no_false_perfect_match(tmp_path):
    db=tmp_path/'test.sqlite3';initialize_database(db)
    def fake(prompt):return ({'jobs':[{'title':'Neurosurgeon','reason':'AI idea','typical_skills':['Microsurgery','Medical Imaging']}]},'llama3.2:3b')
    result=recommend_careers('Python, SQL, Git, engineering',db_path=db,ai_provider=fake)
    assert result['jobs'][0]['skills_coverage']==0
    assert 'Microsurgery' in result['jobs'][0]['skills_not_detected']

def test_career_no_role_skill_claim(tmp_path):
    db=tmp_path/'test.sqlite3';initialize_database(db)
    def fake(prompt):return ({'jobs':[{'title':'Uncatalogued Role','reason':'idea'}]},'llama3.2:3b')
    result=recommend_careers('Python, SQL',db_path=db,ai_provider=fake)
    assert result['jobs'][0]['skills_coverage'] is None
