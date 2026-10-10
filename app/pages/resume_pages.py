"""Protected resume upload, personal library and admin-only global library."""
import streamlit as st
from app.auth.permissions import require_role, AccessDenied
from app.database.resumes import save_resume,list_user_resumes,list_all_resumes,get_resume
from app.services.resume_parser import ResumeValidationError
from app.ui.session import session_user
from app.config import MAX_RESUME_BYTES

def _actor(role):
    current=session_user()
    try:
        return require_role(current['id'] if current else None,role)
    except AccessDenied:
        st.error(f'{role.capitalize()} sign-in required.')
        st.stop()

def upload_resume():
    user=_actor('user')
    st.title('Upload your resume')
    st.caption('PDF · DOCX · TXT · RTF · ODT | Strict 2 MB (2,000,000 bytes) per upload')
    with st.form('resume_upload',clear_on_submit=True):
        document=st.file_uploader('Choose your resume',type=['pdf','docx','txt','rtf','odt'],accept_multiple_files=False)
        submitted=st.form_submit_button('Validate & save resume',type='primary')
    if submitted:
        if document is None:
            st.warning('Select a resume file first.')
        elif document.size>MAX_RESUME_BYTES:
            st.error('File exceeds 2 MB. Please upload a smaller document.')
        else:
            try:
                record_id=save_resume(user['id'],document.name,document.getvalue())
                st.success(f'Validated and saved resume #{record_id} to your private library.')
            except (ResumeValidationError,ValueError) as exc:
                st.error(str(exc))
    st.info('Files are stored locally, not sent to any cloud AI service. OCR for image-only PDFs is planned for a later phase.')

def user_library():
    user=_actor('user')
    st.title('My resume library')
    records=list_user_resumes(user['id'])
    if not records:
        st.info('You have not uploaded any resumes yet.')
        return
    st.dataframe(records,hide_index=True,use_container_width=True)
    selected=st.selectbox('View extracted text',options=[r['id'] for r in records],format_func=lambda x:next(f"#{r['id']} · {r['original_filename']}" for r in records if r['id']==x))
    record=get_resume(user['id'],selected)
    if record:
        st.text_area('Extracted text',record['extracted_text'],height=340,disabled=True)

def admin_library():
    admin=_actor('admin')
    st.title('Resume records · Administrator')
    st.caption('Restricted: stored applicant data is available only to authorized administrators.')
    records=list_all_resumes(admin['id'])
    st.metric('Total resumes',len(records))
    if not records:
        st.info('No resume records have been submitted.')
        return
    st.dataframe(records,hide_index=True,use_container_width=True)
    selected=st.selectbox('Inspect resume',options=[r['id'] for r in records],format_func=lambda x:next(f"#{r['id']} · {r['original_filename']}" for r in records if r['id']==x))
    record=get_resume(admin['id'],selected)
    if record:
        st.write('Owner:',record['owner_email'])
        st.text_area('Stored extracted text',record['extracted_text'],height=340,disabled=True)
