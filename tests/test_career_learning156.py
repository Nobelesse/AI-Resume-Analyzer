from app.services.career_intelligence155 import occupation_learning_topics, canonical_skill
from app.config import APP_VERSION

def test_release():
    assert APP_VERSION == '1.5.9.9.5'

def test_backend_learning_avoids_marketing():
    options={'Python','REST API','Django','Docker','Google Ads','Tableau','Git','MySQL'}
    actual=occupation_learning_topics('Software Developers', options, {'Python','Git'}, 'Backend Developer Python Git')
    assert 'REST API' in actual or 'Django' in actual
    assert 'Google Ads' not in actual and 'Tableau' not in actual

def test_analyst_priority_is_data():
    options={'Power BI','SQL','GitHub','Kubernetes','DAX','JavaScript','Google Ads'}
    actual=occupation_learning_topics('Business Intelligence Analysts',options, {'SQL'}, 'Data Analyst SQL')
    assert 'Power BI' in actual and 'DAX' in actual
    assert 'Kubernetes' not in actual and 'Google Ads' not in actual

def test_marketing_avoids_engineering():
    options={'Google Analytics','SEO','Content Marketing','Docker','Kubernetes','MySQL'}
    actual=occupation_learning_topics('Market Research Analysts and Marketing Specialists',options,set(), 'Marketing Coordinator')
    assert 'Google Analytics' in actual and 'SEO' in actual
    assert 'Docker' not in actual and 'MySQL' not in actual

def test_known_aliases_are_normalized():
    assert canonical_skill('Microsoft Power BI') == canonical_skill('Power BI')
    actual=occupation_learning_topics('Business Intelligence Analysts',{'Microsoft Power BI','DAX'}, {'Power BI'}, 'Power BI reports')
    assert 'Microsoft Power BI' not in actual and 'DAX' in actual

def test_unknown_job_has_no_arbitrary_recommendations():
    assert occupation_learning_topics('Unrelated Specialist', {'Docker','Google Ads'},set()) == []
