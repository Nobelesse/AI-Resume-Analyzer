from app.services.career_state import _career_selection_changed, _career_current_results


def test_career_switch_clears_all_private_outputs():
    state = {}
    assert _career_selection_changed(state, 42, 101)
    state['career_results'] = {'jobs': [{'title': 'Software Developers'}]}
    state['career_result_identity'] = ('42', '101')
    state['career_gemini_guidance'] = {'guidance': ['private']}
    assert _career_current_results(state, 42, 101)['jobs'][0]['title'] == 'Software Developers'
    assert _career_selection_changed(state, 42, 102)
    assert _career_current_results(state, 42, 102) is None
    assert 'career_gemini_guidance' not in state
    assert 'career_results' not in state


def test_repeated_selection_keeps_valid_result():
    state = {}
    _career_selection_changed(state, 42, 101)
    state['career_results'] = {'jobs': [{'title': 'Business Intelligence Analysts'}]}
    state['career_result_identity'] = ('42', '101')
    assert not _career_selection_changed(state, 42, 101)
    assert _career_current_results(state, 42, 101)['jobs'][0]['title'] == 'Business Intelligence Analysts'


def test_switching_accounts_hides_data():
    state = {}
    _career_selection_changed(state, 42, 101)
    state['career_results'] = {'jobs': [{'title': 'Search Marketing Strategists'}]}
    state['career_result_identity'] = ('42', '101')
    assert _career_current_results(state, 43, 101) is None
    assert _career_selection_changed(state, 43, 101)
    assert _career_current_results(state, 43, 101) is None


def test_switching_three_profiles_same_session():
    state = {}
    profiles = [(1, 'Software Developers'), (2, 'Business Intelligence Analysts'), (3, 'Search Marketing Strategists')]
    for resume_id, occupation in profiles:
        _career_selection_changed(state, 7, resume_id)
        assert _career_current_results(state, 7, resume_id) is None
        state['career_results'] = {'jobs': [{'title': occupation}]}
        state['career_result_identity'] = ('7', str(resume_id))
        assert _career_current_results(state, 7, resume_id)['jobs'][0]['title'] == occupation
