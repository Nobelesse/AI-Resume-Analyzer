"""Streamlit server-side session state; no persistent auth cookies."""
import time
import streamlit as st
from app.auth.service import get_user, audit_logout

IDLE_LIMIT_SECONDS = 30 * 60
PRIVATE_RESULT_KEYS = ("phase6_match", "career_results")

def session_user():
    user_id = st.session_state.get("auth_user_id")
    last_seen = st.session_state.get("auth_seen_at",0)
    if not user_id or time.monotonic() - last_seen > IDLE_LIMIT_SECONDS:
        clear_session()
        return None
    user = get_user(user_id)
    if not user:
        clear_session()
        return None
    st.session_state["auth_seen_at"] = time.monotonic()
    return user

def start_session(user):
    clear_session()
    st.session_state["auth_user_id"] = user["id"]
    st.session_state["auth_seen_at"] = time.monotonic()

def clear_session():
    for key in PRIVATE_RESULT_KEYS:
        st.session_state.pop(key, None)
    st.session_state.pop("auth_user_id",None)
    st.session_state.pop("auth_seen_at",None)

def logout():
    user_id=st.session_state.get("auth_user_id")
    if user_id:
        audit_logout(user_id)
    clear_session()
