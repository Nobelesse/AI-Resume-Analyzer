"""Phase 7 user and admin data management views."""
import streamlit as st
from app.auth.permissions import require_role, AccessDenied, admin_list_accounts
from app.database.dashboard import (admin_resumes, admin_activity, admin_set_user_active,
                                    delete_resume, admin_delete_user, csv_export, user_overview)
from app.database.resumes import list_user_resumes
from app.ui.session import session_user
from app.ui.workspace import page_header, section_heading, step_label


def _actor(role):
    current=session_user()
    try:return require_role(current['id'] if current else None,role)
    except AccessDenied:
        st.error(f'{role.title()} access required.');st.stop()


def admin_resume_management():
    actor=_actor('admin')
    page_header('ADMINISTRATOR / DOCUMENTS', 'Applicant resume library', 'Search, filter and securely manage documents submitted to your private workspace.', '▣')
    col1,col2=st.columns([3,1])
    search=col1.text_input('Search filename or account email')
    kind=col2.selectbox('File type',['All','pdf','docx','txt','rtf','odt'])
    rows=admin_resumes(actor['id'],search=search,file_type=None if kind=='All' else kind)
    st.metric('Matching documents',len(rows))
    section_heading('Matching applicant records', 'Results are limited to the current filters')
    if rows:
        st.dataframe(rows,hide_index=True,use_container_width=True)
        fields=['id','owner_id','owner_email','original_filename','file_type','file_size','created_at']
        st.download_button('Export current records (CSV)',csv_export(rows,fields),'resume-records.csv','text/csv')
        section_heading('Delete a resume', 'Permanent deletion also removes linked analysis and job comparisons')
        selected=st.selectbox('Choose resume ID for removal',[r['id'] for r in rows],format_func=lambda rid: f'#{rid} — '+next(r['original_filename'] for r in rows if r['id']==rid))
        with st.form('admin_delete_resume'):
            confirmation=st.checkbox('I understand this permanently removes the resume and its saved analyses/job comparisons.')
            if st.form_submit_button('Permanently delete selected resume',disabled=not confirmation):
                delete_resume(actor['id'],selected);st.success('Resume removed.');st.rerun()
    else:st.info('No matching records.')


def account_management():
    actor=_actor('admin')
    page_header('ADMINISTRATOR / ACCESS', 'Account management', 'Manage user availability without exposing passwords or private documents.', '◈')
    accounts=admin_list_accounts(actor['id'])
    st.metric('Registered accounts',len(accounts))
    st.info('Permanent administrator: protected and read-only. Only standard user accounts can be activated, deactivated, or permanently deleted.')
    section_heading('Account directory', 'Administrator is permanently protected; standard users are manageable')
    st.dataframe(accounts,use_container_width=True,hide_index=True)
    st.download_button('Export account directory (CSV)',csv_export(accounts,['id','display_name','email','role','is_active','created_at']),'accounts.csv','text/csv')
    eligible=[a for a in accounts if a['role']=='user']
    if eligible:
        section_heading('Standard-user access', 'Activate, deactivate, or permanently delete a standard account')
        selected=st.selectbox('Select standard user',[a['id'] for a in eligible],format_func=lambda uid:next(a['email'] for a in eligible if a['id']==uid))
        record=next(a for a in eligible if a['id']==selected)
        st.caption('Deactivated users cannot authenticate or access records. Their information is preserved.')
        if st.button('Deactivate account' if record['is_active'] else 'Reactivate account',type='primary'):
            admin_set_user_active(actor['id'],selected,not bool(record['is_active']))
            st.success('Account status updated.');st.rerun()
        st.divider()
        st.warning('Permanent deletion cannot be undone. The selected account, resumes, saved ATS analyses and job comparisons will be removed.')
        with st.form('admin_permanent_delete_user'):
            typed=st.text_input('Type the selected user email to confirm permanent deletion', key=f'confirm_delete_{selected}')
            acknowledged=st.checkbox('I understand that this permanently removes this standard user and their saved data.')
            submitted=st.form_submit_button('Permanently delete user', type='secondary')
            if submitted:
                if not acknowledged or typed.strip() != record['email']:
                    st.error('Deletion not confirmed. Enter the exact user email and check the confirmation box.')
                else:
                    admin_delete_user(actor['id'], selected)
                    st.success('Standard user account permanently deleted.')
                    st.rerun()



def audit_page():
    actor=_actor('admin')
    page_header('ADMINISTRATOR / SECURITY', 'Activity log', 'Review auditable account and document events in your local workspace.', '◎')
    events=admin_activity(actor['id'],limit=500)
    kinds=sorted(set(r['event'] for r in events))
    selected=st.selectbox('Filter event',['All']+kinds)
    rows=[r for r in events if selected=='All' or r['event']==selected]
    st.metric('Events in view',len(rows))
    section_heading('Recorded events', 'Up to 500 recent events, metadata only')
    st.dataframe(rows,hide_index=True,use_container_width=True)
    st.download_button('Export activity log (CSV)',csv_export(rows,['id','actor_id','actor_email','event','created_at']),'audit-events.csv','text/csv')
    st.caption('Event log contains metadata only; no passwords or extracted resume text.')


def my_record_management():
    actor=_actor('user')
    page_header('MY WORKSPACE / PRIVACY', 'Manage my records', 'Inspect and remove resumes you own, with linked results removed as well.', '▣')
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


def taxonomy_management():
    _actor('admin')
    from app.services.taxonomy import catalog_details
    page_header('ADMINISTRATOR / INTELLIGENCE', 'Occupation and skills catalog', 'Inspect imported publisher data and actual database counts. No resume content is displayed.', '◈')
    info=catalog_details()
    a,b,c=st.columns(3)
    a.metric('Occupations',info['counts']['occupations'])
    b.metric('Unique catalog skills',info['counts']['skills'])
    c.metric('Occupation–skill links',info['counts']['links'])
    section_heading('Source attribution','Datasets imported from official publisher CSVs')
    st.dataframe(info['imports'],use_container_width=True,hide_index=True)
    section_heading('Relationships','Relationship counts grouped by publisher and type')
    st.dataframe(info['relations'],use_container_width=True,hide_index=True)
    section_heading('Occupation aliases','Searchable alternate job titles')
    st.dataframe(info['aliases'],use_container_width=True,hide_index=True)
    st.caption('Catalog counts describe imported records, not verified candidate skills. Official files remain outside the application ZIP.')
