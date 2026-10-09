"""Job matching, interactive breakdown and downloadable reports."""
import streamlit as st
from app.auth.permissions import require_role,AccessDenied
from app.ui.session import session_user
from app.database.resumes import list_user_resumes
from app.database.job_matches import save_job_match,list_job_matches,get_job_match
from app.services.occupation_ai import analyze_occupation
from app.services.career_finder import recommend_careers
from app.database.resumes import get_resume
from app.services.reports import render_html_report,render_pdf_report

def _user():
    current=session_user()
    try:return require_role(current['id'] if current else None,'user')
    except AccessDenied:
        st.error('User sign-in required.');st.stop()

def _display(result):
    st.metric('Estimated job match',f"{result['match_score']} / 100")
    st.caption(result['disclaimer'])
    if result.get('requirements_status') == 'title-suggestions':
        st.info('These are typical skills suggested for this role, NOT confirmed requirements from an employer.')
    elif result.get('requirements_status') == 'unrecognized-role':
        st.warning('Role not found in the offline role library. Paste a job description or enable local Ollama for broader role suggestions.')
    with st.expander('Suggested role skills ('+str(len(result.get('suggested_role_skills',[])))+')', expanded=True):
        st.write(', '.join(result.get('suggested_role_skills',[])) or 'No occupation suggestions available')
        st.caption('Matched in your resume: '+(', '.join(result.get('matched_suggested',[])) or 'None'))
        st.caption('Not detected in your resume: '+(', '.join(result.get('missing_suggested',[])) or 'None'))
    profile=result.get('occupation_profile') or {}
    if profile:
        st.subheader('AI Occupation Intelligence')
        st.caption('Source: '+profile.get('source','unknown'))
        if profile.get('warning'): st.warning('Local AI fallback: '+profile['warning'])
        st.write(profile.get('overview',''))
        for name,label in [('responsibilities','Typical responsibilities'),('technical_skills','Technical skills'),('soft_skills','Soft skills'),('qualifications','Typical qualifications'),('career_notes','Career notes')]:
            if profile.get(name):
                with st.expander(label,expanded=(name=='responsibilities')):
                    for item in profile[name]:st.write('• '+item)
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
    st.caption('Enter any job title or job description. Ollama runs automatically; the offline library is a fallback.')
    resumes=list_user_resumes(user['id'])
    if not resumes:st.warning('Upload your resume first.');return
    ids=[r['id'] for r in resumes]
    selected=st.selectbox('Select your resume',ids,format_func=lambda k:next(r['original_filename'] for r in resumes if r['id']==k))
    with st.form('job_compare_form'):
        title=st.text_input('Job title (optional if you paste a job description)',max_chars=150,placeholder='e.g. Customer Care Executive')
        description=st.text_area('Job description (optional; up to 30,000 characters)',height=230,max_chars=30000)
        st.caption('Automatic Ollama: llama3.2:3b, then llama3.2:1b on failure. No checkbox needed.')
        weight=st.slider('Required skill weight',min_value=0.50,max_value=0.95,value=0.75,step=0.05)
        submit=st.form_submit_button('Compare and save',type='primary')
    if submit:
        try:
            with st.spinner('Analyzing occupation with local Ollama (first response can take a few minutes)...'):
                profile=analyze_occupation(title,description)
                st.session_state['phase6_match']=save_job_match(user['id'],selected,title,description,
                    required_weight=round(weight,2),occupation_profile=profile)
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


def career_finder():
    user=_user();st.title('AI Career Finder')
    st.caption('Get possible jobs based on your existing resume skills. Ollama runs automatically with offline fallback.')
    resumes=list_user_resumes(user['id'])
    if not resumes:st.warning('Upload your resume first.');return
    ids=[r['id'] for r in resumes]
    selected=st.selectbox('Resume to analyze',ids,format_func=lambda k:next(r['original_filename'] for r in resumes if r['id']==k),key='career_resume')
    if st.button('Find suitable careers',type='primary'):
        record=get_resume(user['id'],selected)
        if record is None:st.error('Resume not found.');return
        with st.spinner('Finding career options with Ollama...'):
            try:st.session_state['career_results']=recommend_careers(record['extracted_text'])
            except ValueError as exc:st.error(str(exc));return
    data=st.session_state.get('career_results')
    if not data:return
    if data.get('warning'):st.warning('Offline fallback used: '+data['warning'])
    st.caption('Source: '+data['source']+' • '+data['disclaimer'])
    for job in data['jobs']:
        with st.expander(job['title']+' — '+(str(job['skills_coverage'])+'% skill coverage' if job['skills_coverage'] is not None else 'skill coverage unavailable'),expanded=False):
            st.write(job['reason'])
            st.write('**Detected:** '+(', '.join(job['skills_detected']) or 'None'))
            st.write('**Not detected:** '+(', '.join(job['skills_not_detected']) or 'None'))
            st.caption(job['eligibility'])
