"""Streamlit UI: authorized resume scoring and historical results."""
import streamlit as st
from app.auth.permissions import require_role,AccessDenied
from app.ui.session import session_user
from app.database.resumes import list_user_resumes
from app.database.analyses import analyze_resume,list_analyses,get_analysis
from app.services.skills import skill_count
from app.services.ats_intelligence import resume_readiness, job_compatibility
from app.database.resumes import get_resume
from app.ui.workspace import page_header, section_heading, step_label

def _user():
    current=session_user()
    try:return require_role(current['id'] if current else None,'user')
    except AccessDenied:
        st.error('User sign-in required.');st.stop()

def _show(result):
    section_heading('Your ATS readiness', 'An explainable estimate, not an employer hiring decision')
    st.metric('Estimated ATS-readiness',f"{result['score']}/100")
    st.progress(min(100, max(0, int(result['score']))) / 100)
    st.caption(result['disclaimer'])
    section_heading('Evaluation breakdown', 'See how the score is distributed across categories')
    st.bar_chart(result['components'])
    section_heading(f"Recognized skills ({len(result['skills'])})")
    if result['skills']:st.write(' · '.join(result['skills']))
    else:st.info('No matching entries in the current local skill catalog.')
    section_heading('Section detection')
    st.dataframe([{'section':name.title(),'Detected':status} for name,status in result['sections'].items()],hide_index=True,use_container_width=True)
    section_heading('Your next improvements')
    if result['recommendations']:
        for item in result['recommendations']:st.write('• '+item)
    else:st.success('No recommendations triggered by the current rules.')

def resume_analysis():
    user=_user();page_header('ATS ANALYSIS', 'Resume Intelligence', 'Understand your resume structure, recognized skills and improvement opportunities.', '✧')
    st.caption(f'Local skills catalog · {skill_count():,} entries · Explainable scoring')
    step_label('01', 'Select a saved resume')
    resumes=list_user_resumes(user['id'])
    if not resumes:
        st.warning('Upload a resume in Upload Resume first.');return
    selected=st.selectbox('Choose one of your resumes',[r['id'] for r in resumes],format_func=lambda key:next(f"#{r['id']} · {r['original_filename']}" for r in resumes if r['id']==key))
    step_label('02', 'Run secure local analysis')
    if st.button('Analyze and save results',type='primary'):
        try:st.session_state['phase5_current_result']=analyze_resume(user['id'],selected)
        except (ValueError,PermissionError) as error:st.error(str(error));return
    result=st.session_state.get('phase5_current_result')
    if result: _show(result)

def advanced_ats_intelligence():
    user=_user()
    page_header('ATS INTELLIGENCE', 'Advanced ATS Intelligence',
                'Understand resume readiness and how your experience aligns with a specific job.', '✧')
    st.caption('Two independent, evidence-based assessments. No score can guarantee employer ATS outcomes.')
    resumes=list_user_resumes(user['id'])
    if not resumes:
        st.warning('Upload a resume first.');return
    selected=st.selectbox('Choose your resume',[r['id'] for r in resumes],
            format_func=lambda ident:next(r['original_filename'] for r in resumes if r['id']==ident),
            key='ats158_resume')
    resume=get_resume(user['id'],selected)
    text=resume['extracted_text']
    description=st.text_area('Paste a job description (optional)',height=160,
                              placeholder='Paste required and preferred skills, experience, and qualifications from a real job posting.',
                              key='ats158_description')
    analysis_key=(user['id'],selected,description)
    if st.button('Analyze resume',type='primary',key='ats158_analyze'):
        try:
            readiness=resume_readiness(text)
            compatibility=job_compatibility(text,description) if description.strip() else None
            st.session_state['ats158_result']=(analysis_key,readiness,compatibility)
        except ValueError as error:
            st.error(str(error));return
    result=st.session_state.get('ats158_result')
    if not result or result[0]!=analysis_key:
        st.info('Run the analysis to view results for this resume and job description.');return
    _,readiness,compatibility=result
    left,right=st.columns(2)
    left.metric('Resume readiness',f"{readiness['score']}/100")
    right.metric('Job compatibility',
       f"{compatibility['score']}/100" if compatibility and compatibility['score_available'] else 'Not assessed')
    st.caption(readiness['disclaimer'])
    if compatibility:st.caption(compatibility['disclaimer'])
    section_heading('Resume quality', 'Understand what the resume parser can detect')
    st.dataframe(readiness['checks'],hide_index=True,use_container_width=True)
    with st.expander('Readiness scoring breakdown'):
        st.bar_chart(readiness['components'])
    if readiness['recommendations']:
        st.subheader('Resume improvement opportunities')
        for item in readiness['recommendations'][:8]:st.write('• '+item)
    if compatibility:
        section_heading('Job requirements', 'Separate documented matches from items needing human review')
        if not compatibility['score_available']:
            st.warning('Insufficient recognized job-specific evidence to calculate a meaningful compatibility score.')
        st.caption(f"{compatibility['matched']} evidenced · {compatibility['partial']} partially evidenced · "
                   f"{compatibility['not_found']} not found · {compatibility['manual_review_count']} need manual review")
        for requirement in compatibility['requirements']:
            with st.expander(f"{requirement['priority'].title()} · {requirement['status'].replace('-', ' ')} · {requirement['text'][:110]}"):
                st.write('Evidence found: '+(', '.join(requirement['matched']) or 'None detected'))
                st.write('Not found in resume: '+(', '.join(requirement['not_found']) or 'None'))
        with st.expander('Job compatibility methodology'):
            st.write(compatibility['methodology'])

def analysis_history():
    user=_user();page_header('SAVED INTELLIGENCE', 'Analysis History', 'Revisit earlier ATS reports without losing your progress.', '◷')
    rows=list_analyses(user['id'])
    if not rows:st.info('You have no saved analyses yet.');return
    st.dataframe(rows,hide_index=True,use_container_width=True)
    chosen=st.selectbox('Open previous result',[r['id'] for r in rows],format_func=lambda ident:f'Analysis #{ident}')
    result=get_analysis(user['id'],chosen)
    if result:_show(result)
