"""Streamlit server-side session state; no persistent auth cookies."""
import time
import streamlit as st
from app.auth.service import get_user, audit_logout

IDLE_LIMIT_SECONDS = 30 * 60
PRIVATE_RESULT_KEYS = ("phase6_match", "career_results")

def session_user():
    user_id = st.session_state.get("auth_user_id")
    last_seen = st.session_state.get("auth_seen_at",0)
    if user_id is None or time.monotonic() - last_seen > IDLE_LIMIT_SECONDS:
        clear_session()
        return None
    user = get_user(user_id, include_session_guard=True)
    if not user or st.session_state.get("auth_session_guard") != user.pop("_session_guard"):
        clear_session()
        return None
    st.session_state["auth_seen_at"] = time.monotonic()
    return user

def start_session(user):
    # Obtain a fresh account instance guard; IDs alone aren't session identities
    # because deleted IDs can be reused by a different person.
    record = get_user(user["id"], include_session_guard=True)
    if record is None or record["email"] != user["email"] or record["role"] != user["role"]:
        raise PermissionError("Account session could not be verified.")
    clear_session()
    st.session_state["auth_user_id"] = user["id"]
    st.session_state["auth_session_guard"] = record["_session_guard"]
    st.session_state["auth_seen_at"] = time.monotonic()

def clear_session():
    for key in PRIVATE_RESULT_KEYS:
        st.session_state.pop(key, None)
    st.session_state.pop("auth_user_id",None)
    st.session_state.pop("auth_session_guard",None)
    st.session_state.pop("auth_seen_at",None)

def logout():
    user_id=st.session_state.get("auth_user_id")
    if user_id is not None:
        # A stale browser session must not log an event against a reused ID.
        record = get_user(user_id, include_session_guard=True)
        if record and record.get("_session_guard") == st.session_state.get("auth_session_guard"):
            audit_logout(user_id)
    clear_session()
