"""UI-independent identity guard for user-scoped career results."""
def _career_selection_changed(state, user_id, resume_id):
    """Invalidate private analyses whenever the account or selected resume changes.

    Accepts Streamlit session state or a dict for deterministic offline tests.
    """
    identity = (str(user_id), str(resume_id))
    if state.get('career_active_identity') != identity:
        for key in ('career_results', 'career_result_identity'):
            state.pop(key, None)
        state['career_active_identity'] = identity
        return True
    return False


def _career_current_results(state, user_id, resume_id):
    """Never show previous results for a different account or resume."""
    identity = (str(user_id), str(resume_id))
    if state.get('career_active_identity') != identity or state.get('career_result_identity') != identity:
        return None
    return state.get('career_results')


