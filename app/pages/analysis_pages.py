"""Streamlit UI: authorized resume scoring and historical results."""
import streamlit as st
from app.auth.permissions import require_role,AccessDenied
from app.ui.session import session_user
from app.database.resumes import list_user_resumes
from app.database.analyses import analyze_resume,list_analyses,get_analysis
from app.services.skills import skill_count

def _user():
    current=session_user()
    try:return require_role(current['id'] if current else None,'user')
    except AccessDenied:
        st.error('User sign-in required.');st.stop()

def _show(result):
    st.metric('Estimated ATS-readiness',f"{result['score']}/100")
    st.caption(result['disclaimer'])
    st.subheader('Evaluation breakdown')
    st.bar_chart(result['components'])
    st.subheader(f"Recognized skills ({len(result['skills'])})")
    if result['skills']:st.write(' · '.join(result['skills']))
    else:st.info('No matching entries in the current local skill catalog.')
    st.subheader('Section detection')
    st.dataframe([{'section':name.title(),'Detected':status} for name,status in result['sections'].items()],hide_index=True,use_container_width=True)
    st.subheader('Actionable recommendations')
    if result['recommendations']:
        for item in result['recommendations']:st.write('• '+item)
    else:st.success('No recommendations triggered by the current rules.')

def resume_analysis():
    user=_user();st.title('Resume Intelligence');st.caption('Local explainable analysis — no paid AI key required')
    st.info(f'Current skills catalog: {skill_count():,} curated entries. Expand using the CSV importer for 10,000+ skills.')
    resumes=list_user_resumes(user['id'])
    if not resumes:
        st.warning('Upload a resume in Upload Resume first.');return
    selected=st.selectbox('Choose one of your resumes',[r['id'] for r in resumes],format_func=lambda key:next(f"#{r['id']} · {r['original_filename']}" for r in resumes if r['id']==key))
    if st.button('Analyze and save results',type='primary'):
        try:st.session_state['phase5_current_result']=analyze_resume(user['id'],selected)
        except (ValueError,PermissionError) as error:st.error(str(error));return
    result=st.session_state.get('phase5_current_result')
    if result: _show(result)

def analysis_history():
    user=_user();st.title('My Analysis History')
    rows=list_analyses(user['id'])
    if not rows:st.info('You have no saved analyses yet.');return
    st.dataframe(rows,hide_index=True,use_container_width=True)
    chosen=st.selectbox('Open previous result',[r['id'] for r in rows],format_func=lambda ident:f'Analysis #{ident}')
    result=get_analysis(user['id'],chosen)
    if result:_show(result)
