"""Job matching, interactive breakdown and downloadable reports."""
import streamlit as st
from app.auth.permissions import require_role,AccessDenied
from app.ui.session import session_user
from app.database.resumes import list_user_resumes
from app.database.job_matches import save_job_match,list_job_matches,get_job_match
from app.services.reports import render_html_report,render_pdf_report

def _user():
    current=session_user()
    try:return require_role(current['id'] if current else None,'user')
    except AccessDenied:
        st.error('User sign-in required.');st.stop()

def _display(result):
    st.metric('Estimated job match',f"{result['match_score']} / 100")
    st.caption(result['disclaimer'])
    st.bar_chart({'Text similarity':[result['similarity_score']], 'Skills score':[result['skill_match_score'] or 0]})
    for field,title in [('matched_required','Matched required'),('missing_required','Missing required'),('matched_preferred','Matched preferred'),('missing_preferred','Missing preferred')]:
        with st.expander(f"{title} ({len(result[field])})",expanded=('missing_required'==field)):
            if result[field]:st.write(' • '.join(result[field]))
            else:st.caption('None detected')
    for explanation in result['explanations']:st.write('• '+explanation)
    st.download_button('Download PDF report',render_pdf_report(result),file_name='job-match-report.pdf',mime='application/pdf',key=f"pdf_{result.get('match_id', 'new')}")
    st.download_button('Download HTML report',render_html_report(result),file_name='job-match-report.html',mime='text/html',key=f"html_{result.get('match_id', 'new')}")

def job_match():
    user=_user();st.title('Job Match Studio')
    st.caption('Compare your uploaded resume against a job description without external AI APIs.')
    resumes=list_user_resumes(user['id'])
    if not resumes:st.warning('Upload your resume first.');return
    ids=[r['id'] for r in resumes]
    selected=st.selectbox('Select your resume',ids,format_func=lambda k:next(r['original_filename'] for r in resumes if r['id']==k))
    with st.form('job_compare_form'):
        title=st.text_input('Job title',max_chars=150)
        description=st.text_area('Job description (30–30,000 characters)',height=230,max_chars=30000)
        weight=st.slider('Required skill weight',min_value=0.50,max_value=0.95,value=0.75,step=0.05)
        submit=st.form_submit_button('Compare and save',type='primary')
    if submit:
        try:st.session_state['phase6_match']=save_job_match(user['id'],selected,title,description,required_weight=round(weight,2))
        except (ValueError,PermissionError) as exc:st.error(str(exc));return
    result=st.session_state.get('phase6_match')
    if result: _display(result)

def job_history():
    user=_user();st.title('Saved Job Comparisons')
    rows=list_job_matches(user['id'])
    if not rows:st.info('No saved job comparisons yet.');return
    st.dataframe(rows,hide_index=True,use_container_width=True)
    selection=st.selectbox('Open comparison',[r['id'] for r in rows],format_func=lambda k:next(r['job_title'] for r in rows if r['id']==k))
    result=get_job_match(user['id'],selection)
    if result:_display(result)
