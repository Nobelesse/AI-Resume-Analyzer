"""Job matching, interactive breakdown and downloadable reports."""
import streamlit as st
from app.auth.permissions import require_role,AccessDenied
from app.ui.session import session_user
from app.database.resumes import list_user_resumes
from app.database.job_matches import save_job_match,list_job_matches,get_job_match
from app.services.occupation_ai import analyze_occupation
from app.services.career_finder import recommend_careers
from app.services.career_state import _career_selection_changed, _career_current_results
from app.services.hybrid_intelligence import explain_career_recommendations, GeminiUnavailable, gemini_connection_status
from app.database.resumes import get_resume
from app.services.reports import render_html_report,render_pdf_report
from app.ui.workspace import page_header, step_label, section_heading

def _user():
    current=session_user()
    try:return require_role(current['id'] if current else None,'user')
    except AccessDenied:
        st.error('User sign-in required.');st.stop()

def _display(result):
    section_heading('Your match overview', 'Evidence-based comparison against the selected role')
    st.metric('Estimated job match',f"{result['match_score']} / 100")
    st.progress(min(100, max(0, int(result['match_score']))) / 100)
    st.caption(result['disclaimer'])
    if result.get('requirements_status') == 'title-suggestions':
        st.info('These are typical skills suggested for this role, NOT confirmed requirements from an employer.')
    elif result.get('requirements_status') == 'unrecognized-role':
        st.warning('Role not found in the offline catalog. Paste a detailed job description for better matching.')
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
    user=_user();page_header('OCCUPATION INTELLIGENCE', 'Job Match Studio', 'Compare resume evidence to explicit job requirements with offline, explainable matching.', '◎')
    st.caption('Zero-cost offline matching · Imported O*NET/ESCO skills when available · Not a certified ATS score')
    resumes=list_user_resumes(user['id'])
    if not resumes:st.warning('Upload your resume first.');return
    ids=[r['id'] for r in resumes]
    step_label('01', 'Select your resume')
    selected=st.selectbox('Select your resume',ids,format_func=lambda k:next(r['original_filename'] for r in resumes if r['id']==k))
    step_label('02', 'Describe the role you want to explore')
    with st.form('job_compare_form'):
        title=st.text_input('Job title (optional if you paste a job description)',max_chars=150,placeholder='e.g. Customer Care Executive')
        description=st.text_area('Job description (optional; up to 30,000 characters)',height=230,max_chars=30000)
        st.caption('No paid API and no local language model required.')
        weight=st.slider('Required skill weight',min_value=0.50,max_value=0.95,value=0.75,step=0.05)
        submit=st.form_submit_button('Compare and save',type='primary')
    if submit:
        try:
            with st.spinner('Comparing resume evidence against the role requirements...'):
                profile=analyze_occupation(title,description)
                st.session_state['phase6_match']=save_job_match(user['id'],selected,title,description,
                    required_weight=round(weight,2),occupation_profile=profile)
        except (ValueError,PermissionError) as exc:st.error(str(exc));return
    result=st.session_state.get('phase6_match')
    if result: _display(result)

def job_history():
    user=_user();page_header('YOUR HISTORY', 'Saved Job Comparisons', 'Review comparisons and download your previous reports.', '▤')
    rows=list_job_matches(user['id'])
    if not rows:st.info('No saved job comparisons yet.');return
    st.dataframe(rows,hide_index=True,use_container_width=True)
    selection=st.selectbox('Open comparison',[r['id'] for r in rows],format_func=lambda k:next(r['job_title'] for r in rows if r['id']==k))
    result=get_job_match(user['id'],selection)
    if result:_display(result)


def career_finder():
    user = _user()
    page_header('CAREER DISCOVERY', 'AI Career Finder',
                'Find career paths aligned with the skills and experience evidenced by your resume.', '✧')
    st.caption('Evidence-ranked O*NET/ESCO careers · Works fully offline · Optional Gemini guidance with consent')
    st.caption(gemini_connection_status()['message'])
    ai_opt_in = st.checkbox(
        'Enable optional Gemini career guidance (sends matched skills and proposed roles to Google; free quota limits apply)',
        value=False)
    resumes = list_user_resumes(user['id'])
    if not resumes:
        st.warning('Upload your resume first.')
        return
    ids = [row['id'] for row in resumes]
    step_label('01', 'Choose a resume for career discovery')
    selected = st.selectbox('Resume to analyze', ids,
                            format_func=lambda key: next(row['original_filename'] for row in resumes if row['id'] == key),
                            key='career_resume')
    changed = _career_selection_changed(st.session_state, user['id'], selected)
    if changed:
        st.caption('Resume changed. Click **Find suitable careers** to generate new recommendations.')
    step_label('02', 'Discover relevant career paths')
    if st.button('Find suitable careers', type='primary'):
        record = get_resume(user['id'], selected)
        if record is None:
            st.error('Resume not found.')
            return
        with st.spinner('Ranking careers from your local occupation catalog...'):
            try:
                new_results = recommend_careers(record['extracted_text'])
            except ValueError as exc:
                st.session_state.pop('career_results', None)
                st.error(str(exc))
                return
            st.session_state['career_results'] = new_results
            st.session_state['career_result_identity'] = (str(user['id']), str(selected))
            st.session_state.pop('career_gemini_guidance', None)
    data = _career_current_results(st.session_state, user['id'], selected)
    if data is None:
        st.info('Choose your resume and click **Find suitable careers**. Previous resume results are cleared automatically.')
        return
    if data.get('warning'):
        st.warning(data['warning'])
    if ai_opt_in and st.button('Generate optional Gemini learning guidance'):
        try:
            st.session_state['career_gemini_guidance'] = explain_career_recommendations(data, consent=True)
        except GeminiUnavailable as error:
            st.warning(str(error))
    if ai_opt_in and st.session_state.get('career_gemini_guidance'):
        st.subheader('Optional Gemini guidance — verify independently')
        st.json(st.session_state['career_gemini_guidance'])
    st.caption('Source: ' + data['source'] + ' • ' + data['disclaimer'])
    section_heading('Suggested career paths', 'Domain-aware rankings; catalog skill coverage is not a suitability probability')
    for job in data['jobs']:
        title = job['title']
        strength = job.get('match_strength')
        label = title + (' — evidence ranking '+str(round(strength, 1))+'/100' if strength is not None else '')
        with st.expander(label, expanded=False):
            st.write(job['reason'])
            parts = job.get('score_breakdown') or {}
            if parts:
                st.caption('Ranking contributions (points): ' + ', '.join(f'{name.replace("_", " ")}: {value}' for name, value in parts.items()))
            matched = job.get('skills_detected', [])
            st.write('**Matched catalog terms (' + str(len(matched)) + '):** ' + (', '.join(matched) or 'None'))
            st.caption('Higher-signal technical/domain evidence: ' + (', '.join(job.get('high_signal_skills', [])) or 'Not identified'))
            st.write('**Potential learning topics (not verified job requirements):** ' + (', '.join(job.get('skills_not_detected', [])) or 'None'))
            coverage = job.get('skills_coverage')
            count = job.get('catalog_skill_count')
            if coverage is not None:
                st.caption(f'Raw catalog coverage: {coverage}% ({len(matched)} of {count or "unknown"} catalog skills). '
                           'Catalog coverage is distinct from the evidence-ranking score and may be small for broad occupations.')
            if job.get('domain_alignment'):
                st.caption('Career-family alignment: ' + job['domain_alignment'])
            st.caption(job['eligibility'])
