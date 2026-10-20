"""Protected resume upload, personal library and admin-only global library."""
import streamlit as st
from app.auth.permissions import require_role, AccessDenied
from app.database.resumes import save_resume,list_user_resumes,list_all_resumes,get_resume
from app.services.resume_parser import ResumeValidationError
from app.ui.session import session_user
from app.config import MAX_RESUME_BYTES, MAX_CV_BYTES
from app.ui.workspace import page_header, step_label, section_heading

def _actor(role):
    current=session_user()
    try:
        return require_role(current['id'] if current else None,role)
    except AccessDenied:
        st.error(f'{role.capitalize()} sign-in required.')
        st.stop()

def upload_resume():
    user = _actor('user')
    page_header('DOCUMENT INTELLIGENCE', 'Upload Resume / CV',
                'Import a resume or academic CV for ATS insights, job matching and career discovery.', '↥')
    with st.form('resume_upload', clear_on_submit=True):
        document_type = st.radio('Document type', ['Resume', 'CV'], horizontal=True,
                                 help='Resume: maximum 2 MB. CV: maximum 10 MB.')
        document = st.file_uploader('Choose your Resume / CV',
                                    type=['pdf', 'docx', 'txt', 'rtf', 'odt'],
                                    accept_multiple_files=False)
        submitted = st.form_submit_button('Validate & save document', type='primary')
    kind = document_type.lower()
    limit = MAX_CV_BYTES if kind == 'cv' else MAX_RESUME_BYTES
    if submitted:
        if document is None:
            st.warning('Select a document first.')
        elif document.size > limit:
            st.error(f'{document_type} exceeds {limit // 1_000_000} MB. Please upload a smaller document.')
        else:
            try:
                record_id = save_resume(user['id'], document.name, document.getvalue(), document_type=kind)
                st.success(f'Validated and saved {document_type} #{record_id} to your private library.')
            except (ResumeValidationError, ValueError) as exc:
                st.error(str(exc))
    st.info('Resume: 2 MB · CV: 10 MB · PDF, DOCX, TXT, RTF, ODT. Scanned images require OCR.')

def user_library():
    user=_actor('user')
    page_header('YOUR DOCUMENTS', 'Resume & CV library', 'Access your uploaded documents and review the extracted text.', '▤')
    records=list_user_resumes(user['id'])
    if not records:
        st.info('You have not uploaded a resume or CV yet.')
        return
    st.dataframe(records,hide_index=True,use_container_width=True)
    selected=st.selectbox('View extracted text',options=[r['id'] for r in records],format_func=lambda x:next(f"#{r['id']} · {r['original_filename']}" for r in records if r['id']==x))
    record=get_resume(user['id'],selected)
    if record:
        st.text_area('Extracted text',record['extracted_text'],height=340,disabled=True)

def admin_library():
    admin=_actor('admin')
    page_header('ADMIN · PRIVATE RECORDS', 'Resume & CV records', 'Inspect and manage all stored applicant documents with admin authorization.', '◆')
    st.caption('Restricted: stored applicant data is available only to authorized administrators.')
    records=list_all_resumes(admin['id'])
    st.metric('Total documents',len(records))
    if not records:
        st.info('No resume records have been submitted.')
        return
    st.dataframe(records,hide_index=True,use_container_width=True)
    selected=st.selectbox('Inspect resume',options=[r['id'] for r in records],format_func=lambda x:next(f"#{r['id']} · {r['original_filename']}" for r in records if r['id']==x))
    record=get_resume(admin['id'],selected)
    if record:
        st.write('Owner:',record['owner_email'])
        st.text_area('Stored extracted text',record['extracted_text'],height=340,disabled=True)
