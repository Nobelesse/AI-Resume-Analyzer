"""Generate a factual, text-first PDF from the exact results shown in ATS Intelligence."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether


def build_ats_pdf_report(readiness: dict, compatibility: dict | None = None, *, resume_filename: str = 'Resume') -> bytes:
    """Produce a downloadable, bounded report without inventing scoring evidence."""
    data = BytesIO()
    pdf = SimpleDocTemplate(data, pagesize=A4, leftMargin=19*mm,
                            rightMargin=19*mm, topMargin=18*mm, bottomMargin=18*mm,
                            title='Resume Assessment', author='AI Resume Analyzer')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitleCustom', parent=styles['Heading1'], fontSize=17,
                              textColor=colors.HexColor('#17243B'), spaceAfter=11))
    styles.add(ParagraphStyle(name='ReportSmallCustom', parent=styles['BodyText'], fontSize=8.7,
                              leading=12, spaceAfter=6, wordWrap='CJK'))
    story = []
    def para(value):
        return Paragraph(escape(str(value)), styles['ReportSmallCustom'])
    def heading(text):
        story.append(Paragraph(escape(text), styles['Heading2']))
    story.append(Paragraph('Resume Intelligence — Assessment Report', styles['ReportTitleCustom']))
    story.append(para('Resume: '+str(resume_filename)[:160]))
    story.append(para('Resume Readiness: '+str(readiness['score'])+'/100 (rule-based estimate)'))
    if compatibility is None:
        story.append(para('Job Compatibility: Not assessed — no job description provided.'))
    elif compatibility.get('score_available'):
        story.append(para('Job Compatibility: '+str(compatibility['score'])+'/100 (job-description evidence estimate)'))
    else:
        story.append(para('Job Compatibility: Not scored — insufficient recognized requirements.'))
    story.append(para(readiness.get('disclaimer','')))
    if compatibility:
        story.append(para(compatibility.get('disclaimer','')))
    heading('Readiness scoring breakdown')
    maxima = {'Resume sections':35,'Contact details':15,'Skill evidence':20,
              'Substance':15,'Bullet formatting':10,'Quantified impact':5}
    for name, maximum in maxima.items():
        awarded=readiness['components'].get(name,0)
        story.append(para(f'{name}: {awarded} / {maximum} points'))
    heading('Resume quality checks')
    for check in readiness.get('checks',[])[:40]:
        story.append(para(f"{check['check']}: {check['status']} — {check['detail']}"))
    heading('Detected skills')
    skills=readiness.get('skills',[])
    story.append(para(', '.join(skills) if skills else 'No supported skill names detected.'))
    heading('Suggested resume improvements')
    advice=readiness.get('recommendations',[])
    for item in advice[:20]:story.append(para('• '+item))
    if not advice:story.append(para('No improvements triggered by the current heuristic checks.'))
    if compatibility:
        heading('Job description compatibility')
        story.append(para(compatibility.get('methodology','')))
        story.append(para(f"Evidenced: {compatibility['matched']}; Partially evidenced: {compatibility['partial']}; Not detected: {compatibility['not_found']}; Manual review: {compatibility['manual_review_count']}"))
        for item in compatibility.get('requirements',[])[:60]:
            story.append(para(f"[{item['priority']}; {item['status']}] {item['text']}"))
            if item.get('matched'):story.append(para('Evidence: '+', '.join(item['matched'])))
            if item.get('not_found'):story.append(para('Not detected: '+', '.join(item['not_found'])))
    heading('Interpretation and limitations')
    story.append(para('Scores reflect only this application’s text-based rules. They do not validate the original PDF layout, reading order, skills proficiency, credentials, employment eligibility, or any employer ATS outcome. Missing resume evidence does not mean a candidate lacks a skill.'))
    pdf.build(story)
    return data.getvalue()
