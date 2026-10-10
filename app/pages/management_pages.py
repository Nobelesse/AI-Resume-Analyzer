"""Phase 7 user and admin data management views."""
import streamlit as st
from app.auth.permissions import require_role, AccessDenied, admin_list_accounts
from app.database.dashboard import (admin_resumes, admin_activity, admin_set_user_active,
                                    delete_resume, csv_export, user_overview)
from app.database.resumes import list_user_resumes
from app.ui.session import session_user


def _actor(role):
    current=session_user()
    try:return require_role(current['id'] if current else None,role)
    except AccessDenied:
        st.error(f'{role.title()} access required.');st.stop()


def admin_resume_management():
    actor=_actor('admin')
    st.title('Resume Management')
    st.caption('Search and manage applicant records. Extracted resume text is restricted to authenticated administrators.')
    col1,col2=st.columns([3,1])
    search=col1.text_input('Search filename or account email')
    kind=col2.selectbox('File type',['All','pdf','docx','txt','rtf','odt'])
    rows=admin_resumes(actor['id'],search=search,file_type=None if kind=='All' else kind)
    st.metric('Matching resumes',len(rows))
    if rows:
        st.dataframe(rows,hide_index=True,use_container_width=True)
        fields=['id','owner_id','owner_email','original_filename','file_type','file_size','created_at']
        st.download_button('Export current records (CSV)',csv_export(rows,fields),'resume-records.csv','text/csv')
        selected=st.selectbox('Choose resume ID for removal',[r['id'] for r in rows],format_func=lambda rid: f'#{rid} — '+next(r['original_filename'] for r in rows if r['id']==rid))
        with st.form('admin_delete_resume'):
            confirmation=st.checkbox('I understand this permanently removes the resume and its saved analyses/job comparisons.')
            if st.form_submit_button('Permanently delete selected resume',disabled=not confirmation):
                delete_resume(actor['id'],selected);st.success('Resume removed.');st.rerun()
    else:st.info('No matching records.')


def account_management():
    actor=_actor('admin');st.title('Account Management')
    accounts=admin_list_accounts(actor['id'])
    st.dataframe(accounts,use_container_width=True,hide_index=True)
    st.download_button('Export account directory (CSV)',csv_export(accounts,['id','display_name','email','role','is_active','created_at']),'accounts.csv','text/csv')
    eligible=[a for a in accounts if a['role']=='user']
    if eligible:
        selected=st.selectbox('Select standard user',[a['id'] for a in eligible],format_func=lambda uid:next(a['email'] for a in eligible if a['id']==uid))
        record=next(a for a in eligible if a['id']==selected)
        st.caption('Deactivated users cannot authenticate or access records. Their information is preserved.')
        if st.button('Deactivate account' if record['is_active'] else 'Reactivate account',type='primary'):
            admin_set_user_active(actor['id'],selected,not bool(record['is_active']))
            st.success('Account status updated.');st.rerun()


def audit_page():
    actor=_actor('admin');st.title('Activity Log')
    events=admin_activity(actor['id'],limit=500)
    kinds=sorted(set(r['event'] for r in events))
    selected=st.selectbox('Filter event',['All']+kinds)
    rows=[r for r in events if selected=='All' or r['event']==selected]
    st.dataframe(rows,hide_index=True,use_container_width=True)
    st.download_button('Export activity log (CSV)',csv_export(rows,['id','actor_id','actor_email','event','created_at']),'audit-events.csv','text/csv')
    st.caption('Event log contains metadata only; no passwords or extracted resume text.')


def my_record_management():
    actor=_actor('user');st.title('Manage My Records')
    overview=user_overview(actor['id'])
    cols=st.columns(3)
    for col,key,label in zip(cols,('resumes','analyses','job_matches'),('Resumes','ATS Analyses','Job Matches')):
        col.metric(label,overview['counts'][key])
    rows=list_user_resumes(actor['id'])
    st.dataframe(rows,hide_index=True,use_container_width=True)
    if rows:
        target=st.selectbox('Delete one of your resumes',[r['id'] for r in rows],format_func=lambda rid:next(r['original_filename'] for r in rows if r['id']==rid))
        with st.form('user_delete_resume'):
            confirmed=st.checkbox('Permanently delete this resume and its associated analyses and job comparisons')
            if st.form_submit_button('Delete my resume',disabled=not confirmed):
                delete_resume(actor['id'],target);st.success('Resume deleted.');st.rerun()
