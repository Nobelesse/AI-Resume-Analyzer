"""Private user and administrator landing pages."""
import streamlit as st
from app.auth.permissions import require_role, AccessDenied, admin_list_accounts
from app.ui.session import session_user

def user_dashboard():
    current=session_user()
    try:
        account=require_role(current["id"] if current else None,"user")
    except AccessDenied:
        st.error("User sign-in is required.")
        st.stop()
    st.markdown('<div class="eyebrow">MEMBER WORKSPACE</div>',unsafe_allow_html=True)
    st.title(f"Welcome, {account['display_name']}")
    st.info("Upload documents from Upload Resume, then view stored text in My Resumes. AI scoring arrives in Phase 5.")
    st.write("Account:", account["email"])

def admin_dashboard():
    current=session_user()
    try:
        account=require_role(current["id"] if current else None,"admin")
        users=admin_list_accounts(account["id"])
    except AccessDenied:
        st.error("Administrator access is required.")
        st.stop()
    st.markdown('<div class="eyebrow">RESTRICTED ADMINISTRATION</div>',unsafe_allow_html=True)
    st.title("Admin control center")
    st.metric("Registered accounts",len(users))
    st.caption("Admin-only directory. Password hashes are never shown.")
    st.dataframe(users,use_container_width=True,hide_index=True)
    st.info("Use All Resumes for protected applicant records; AI analytics arrive in later phases.")
