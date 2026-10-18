"""Job matching, interactive breakdown and downloadable reports."""
import streamlit as st
from app.auth.permissions import require_role,AccessDenied
from app.ui.session import session_user
from app.database.resumes import list_user_resumes
from app.database.job_matches import save_job_match,list_job_matches,get_job_match
from app.services.occupation_ai import analyze_occupation
from app.services.career_finder import recommend_careers
from app.services.resume_evidence import extract_resume_evidence, career_evidence
from app.services.career_state import _career_selection_changed, _career_current_results
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
    title_only = result.get('analysis_mode', 'role-alignment' if result.get('requirements_status') == 'title-suggestions' else 'job-description') == 'role-alignment'
    score = result.get('match_score')
    st.metric('Estimated role alignment' if title_only else 'Estimated job compatibility', f'{score} / 100' if score is not None else 'Not assessed')
    if score is not None:
        st.progress(min(100, max(0, int(score))) / 100)
    if title_only:
        st.info('No employer job description was provided. Required and preferred qualifications are not assessed; these are only typical role-skill suggestions.')
    st.caption(result['disclaimer'])
    st.caption(result.get('scoring_methodology', 'Heuristic comparison.'))
    # The screen is a concise summary. Full line-level evidence remains in the
    # downloadable PDF and HTML reports, not in user-facing expanders.
    st.subheader('Skills matched')
    matched = sorted(set(result.get('matched_required', []) + result.get('matched_preferred', [])))
    if title_only:
        matched = result.get('matched_suggested', [])
    st.write(' · '.join(matched) if matched else 'No skills detected for this comparison.')
    st.subheader('Skills to improve')
    missing = sorted(set(result.get('missing_required', []) + result.get('missing_preferred', [])))
    if title_only:
        missing = result.get('missing_suggested', [])
    st.write(' · '.join(missing) if missing else 'No additional named skills detected.')
    improvements=result.get('improvement_suggestions', [])
    if improvements:
        with st.expander('Resume improvement suggestions', expanded=True):
            for item in improvements:st.write('• '+item)

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
    st.markdown('**Matching overview**')
    if result.get('skill_match_score') is not None:
        st.caption(f"Recognized skills: {result['skill_match_score']}%")
        st.progress(max(0,min(100,result['skill_match_score']))/100)
    if not title_only and result.get('similarity_score') is not None:
        st.caption(f"Job description text similarity: {result['similarity_score']}%")
        st.progress(max(0,min(100,result['similarity_score']))/100)
    # Detailed requirement status and source explanations are available in reports.
    st.download_button('Download PDF report',render_pdf_report(result),file_name='job-match-report.pdf',mime='application/pdf',key=f"pdf_{result.get('match_id', 'new')}")
    st.download_button('Download HTML report',render_html_report(result),file_name='job-match-report.html',mime='text/html',key=f"html_{result.get('match_id', 'new')}")

def job_match():
    user=_user();page_header('OCCUPATION INTELLIGENCE', 'Job Match Studio', 'Compare resume evidence to explicit job requirements with offline, explainable matching.', '◎')
    st.caption('Offline career and job comparisons · Estimates are not hiring decisions')
    resumes=list_user_resumes(user['id'])
    if not resumes:st.warning('Upload your resume first.');return
    ids=[r['id'] for r in resumes]
    step_label('01', 'Select your resume')
    selected=st.selectbox('Select your resume',ids,format_func=lambda k:next(r['original_filename'] for r in resumes if r['id']==k))
    step_label('02', 'Describe the role you want to explore')
    with st.form('job_compare_form'):
        title=st.text_input('Job title (optional if you paste a job description)',max_chars=150,placeholder='e.g. Customer Care Executive')
        description=st.text_area('Job description (optional; up to 30,000 characters)',height=230,max_chars=30000)
        st.caption('For job-specific requirement assessment, paste an employer job description. Title-only mode provides exploratory role alignment.')
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
    if result and str(result.get('resume_id')) == str(selected): _display(result)
    elif result: st.info('Selected resume changed. Compare and save to generate new results.')

def job_history():
    user=_user();page_header('YOUR HISTORY', 'Saved Job Comparisons', 'Review comparisons and download your previous reports.', '▤')
    rows=list_job_matches(user['id'])
    if not rows:st.info('No saved job comparisons yet.');return
    st.dataframe(rows,hide_index=True,use_container_width=True)
    selection=st.selectbox('Open comparison',[r['id'] for r in rows],format_func=lambda k:next(r['job_title'] for r in rows if r['id']==k))
    result=get_job_match(user['id'],selection)
    if result:_display(result)


def career_finder():
    """Student-facing career discovery; diagnostic details remain in the result data."""
    user = _user()
    page_header('CAREER DISCOVERY', 'AI Career Finder',
                'Explore career opportunities aligned with your skills and experience.', '✧')
    resumes = list_user_resumes(user['id'])
    if not resumes:
        st.warning('Upload your resume to explore career opportunities.')
        return
    ids = [row['id'] for row in resumes]
    step_label('01', 'Choose your resume')
    selected = st.selectbox('Resume to analyze', ids,
                            format_func=lambda key: next(row['original_filename'] for row in resumes if row['id'] == key),
                            key='career_resume')
    changed = _career_selection_changed(st.session_state, user['id'], selected)
    if changed:
        st.caption('Resume changed. Find suitable careers to see updated recommendations.')
    step_label('02', 'Discover your career paths')
    if st.button('Find suitable careers', type='primary'):
        record = get_resume(user['id'], selected)
        if record is None:
            st.error('Resume not found.')
            return
        with st.spinner('Discovering career opportunities for your profile...'):
            try:
                new_results = recommend_careers(record['extracted_text'])
            except ValueError as exc:
                st.session_state.pop('career_results', None)
                st.error(str(exc))
                return
            st.session_state['career_results'] = new_results
            st.session_state['career_result_identity'] = (str(user['id']), str(selected))
    data = _career_current_results(st.session_state, user['id'], selected)
    if data is None:
        st.info('Choose your resume and select **Find suitable careers** to begin.')
        return
    if not data.get('jobs'):
        st.info('There is not enough specific information in this resume to recommend careers confidently. Consider adding relevant projects, skills or experience.')
        return
    record = get_resume(user['id'], selected)
    profile = extract_resume_evidence(record.get('extracted_text', '') if record else '')
    section_heading('Recommended Career Paths',
                    'Explore options based on the experience and skills described in your resume.')
    for job in data['jobs']:
        with st.expander(job['title'], expanded=False):
            support = career_evidence(job['title'], profile)
            relevant = support['relevant_skills']
            if relevant:
                st.markdown('**Relevant skills and knowledge from your resume**')
                st.write(', '.join(relevant))
                if support['basic_skills']:
                    st.caption('Stated as basic knowledge: ' + ', '.join(support['basic_skills']))
            else:
                st.caption('The resume offers limited directly relevant skill evidence for this career.')
            if support['career_interests']:
                st.markdown('**Career interests mentioned**')
                st.write(', '.join(support['career_interests']))
                st.caption('An interest is not proof of previous work experience.')
            if support['education']:
                st.markdown('**Education mentioned**')
                st.write(' · '.join(support['education']))
                st.caption('Education is background context, not proof of role-specific proficiency.')
            st.markdown('**Experience level**')
            st.write(support['experience_level'])
            topics = job.get('skills_not_detected', [])
            if topics:
                st.markdown('**Optional skills to explore**')
                st.write(', '.join(topics[:6]))
                st.caption('These are learning ideas, not confirmed requirements or proof that you lack these skills.')
            st.caption('Career suggestions are exploratory and do not verify job eligibility or qualifications.')
