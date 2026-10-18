from app.services.hybrid_intelligence import _ranking_score

def test_occupation_specific_scores_vary():
    strengths={'software':5,'data':0,'marketing':0}
    s1, _, _, part1 = _ranking_score('Software Developers', {'Python','SQL','Docker','Git'}, ['Python','SQL','Docker'], strengths)
    s2, _, _, part2 = _ranking_score('Software Quality Assurance Analysts and Testers', {'Python','Testing','Selenium','Jira','Git'}, ['Python','Git'], strengths)
    assert s1 != s2
    assert part1['catalog_coverage'] != part2['catalog_coverage']

def test_alignment_not_dominant():
    strengths={'software':5,'data':0,'marketing':0}
    low,_,_,_ = _ranking_score('Software Developers', set(map(str,range(100))), ['0'], strengths)
    high,_,_,_ = _ranking_score('Software Developers', {'Python','SQL','Docker'}, ['Python','SQL','Docker'], strengths)
    assert high > low

