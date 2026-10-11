"""Separate sign-in screens for users and administrators."""
import streamlit as st
from app.auth.service import register_user, authenticate, AuthError
from app.ui.session import start_session, session_user
from app.ui.workspace import page_header, step_label

def login(role):
    if session_user():
        st.info("You are already signed in. Sign out before switching accounts.")
        return
    title = "Admin access" if role == "admin" else "User sign in"
    page_header("SECURE ACCESS · ADMIN" if role == "admin" else "SECURE ACCESS · USER", title, "Administrator credentials are provisioned privately." if role == "admin" else "Sign in to access your private career intelligence workspace.", "◆")
    with st.container(key="auth_shell"):
      with st.form(f"login_{role}",clear_on_submit=True):
          email=st.text_input("Email address",max_chars=254)
          password=st.text_input("Password",type="password")
          _, button_center, _ = st.columns([1, 1, 1])
          with button_center:
              submitted=st.form_submit_button("Sign in",use_container_width=False)
    if submitted:
        try:
            user=authenticate(email,password,role)
        except (AuthError,ValueError) as error:
            st.error(str(error))
        else:
            start_session(user)
            st.success("Signed in successfully.")
            st.rerun()

def register():
    if session_user():
        st.info("Sign out to register another account.")
        return
    page_header("JOIN THE WORKSPACE", "Create your account", "Create a secure account to analyze resumes and discover careers.", "✦")
    with st.container(key="auth_shell"):
      with st.form("register",clear_on_submit=True):
          name=st.text_input("Full name",max_chars=80)
          email=st.text_input("Email",max_chars=254)
          password=st.text_input("Password (12+ characters, letters and numbers)",type="password")
          confirm=st.text_input("Confirm password",type="password")
          submitted=st.form_submit_button("Create account",use_container_width=False)
    if submitted:
        if password != confirm:
            st.error("Passwords do not match.")
        else:
            try:
                register_user(email,name,password)
            except ValueError as error:
                st.error(str(error))
            else:
                st.success("Account created. Please sign in through User Login.")
