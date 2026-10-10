"""Role-protected, database-backed dashboard overview pages."""
import streamlit as st
from app.auth.permissions import require_role, AccessDenied
from app.database.dashboard import admin_overview, user_overview
from app.ui.session import session_user


def _get(role):
    current=session_user()
    try:return require_role(current['id'] if current else None,role)
    except AccessDenied:
        st.error('This dashboard requires the corresponding authenticated account.');st.stop()


def user_dashboard():
    actor=_get('user');overview=user_overview(actor['id'])
    st.markdown('<div class="eyebrow">CAREER INTELLIGENCE WORKSPACE</div>',unsafe_allow_html=True)
    st.title(f"Welcome, {actor['display_name']}")
    cols=st.columns(4)
    for col,key,title in zip(cols[:3],('resumes','analyses','job_matches'),('Uploaded Resumes','ATS Analyses','Job Comparisons')):
        col.metric(title,overview['counts'][key])
    cols[3].metric('Average ATS Readiness',f"{overview['average_ats_score']} / 100" if overview['average_ats_score'] is not None else '—')
    st.subheader('Recent uploaded resumes')
    if overview['recent_resumes']:st.dataframe(overview['recent_resumes'],use_container_width=True,hide_index=True)
    else:st.info('Upload a resume to get started.')
    st.caption('Use AI Resume Analysis, Job Match Studio, and AI Career Finder from the navigation. Use Manage My Records to delete uploaded resumes.')


def admin_dashboard():
    actor=_get('admin');overview=admin_overview(actor['id'])
    st.markdown('<div class="eyebrow">RESTRICTED ADMINISTRATION</div>',unsafe_allow_html=True)
    st.title('Admin control center')
    counts=overview['counts']
    c1,c2,c3,c4=st.columns(4)
    for col,name,label in zip((c1,c2,c3,c4),('users','resumes','analyses','job_matches'),('Accounts','Resumes','ATS Analyses','Job Matches')):
        col.metric(label,counts[name])
    st.caption(f"Active standard users: {counts['active_users']} | Indexed skills: {counts['skills']}")
    left,right=st.columns(2)
    with left:
        st.subheader('Resume uploads by day')
        if overview['daily_uploads']:
            st.bar_chart({r['day']:r['count'] for r in overview['daily_uploads']})
        else:st.info('No uploaded resumes yet.')
    with right:
        st.subheader('Document types')
        if overview['file_types']:
            st.bar_chart({r['type']:r['count'] for r in overview['file_types']})
        else:st.info('No document data yet.')
    st.caption('Use Resume Management, Account Management and Activity Log to inspect and manage saved records.')
