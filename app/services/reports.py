"""Portable offline HTML and PDF reports. Escape all user-controlled content."""
from html import escape
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def render_html_report(result):
    title=escape(result['job_title'])
    title_only = result.get('analysis_mode', 'role-alignment' if result.get('requirements_status') == 'title-suggestions' else 'job-description') == 'role-alignment'
    label = 'Estimated role alignment' if title_only else 'Estimated job compatibility'
    score = f"{result['match_score']}/100" if result.get('match_score') is not None else 'Not assessed'
    lines=[f'<h1>{"Role Alignment" if title_only else "Job Compatibility"} — {title}</h1>',f'<p>{label}: {score}</p>']
    if title_only:
        lines.append('<p>No employer job description provided. Required and preferred qualifications were not assessed.</p>')
    elif result.get('similarity_score') is not None:
        lines.append(f"<p>Job description text similarity: {result['similarity_score']}/100</p>")
    if result.get('suggested_role_skills'):
        lines.append('<h2>Suggested occupation skills (not verified employer requirements)</h2><ul>')
        lines.extend(f'<li>{escape(str(item))}</li>' for item in result['suggested_role_skills'])
        lines.append('</ul>')
    for key,label in ([] if title_only else [('matched_required','Matched required skills'),('missing_required','Missing required skills'),('matched_preferred','Matched preferred skills'),('missing_preferred','Missing preferred skills')]):
        lines.append(f'<h2>{label}</h2><ul>')
        lines.extend(f'<li>{escape(str(s))}</li>' for s in result[key])
        lines.append('</ul>')
    if not title_only:
        lines.append('<h2>Line-by-line job description assessment</h2>')
        for row in result.get('requirement_evidence', []):
            lines.append('<p><strong>'+escape(row['priority'].title())+' — '+escape(row['status'].replace('-', ' '))+'</strong>: '+escape(row['text'])+'</p>')
            lines.append('<p>Named skills detected in resume: '+escape(', '.join(row['matched']) or 'None')+'; not detected: '+escape(', '.join(row['not_found']) or 'None')+'</p>')
        lines.append('<h2>Improvement suggestions</h2><ul>')
        lines.extend('<li>'+escape(s)+'</li>' for s in result.get('improvement_suggestions', []))
        lines.append('</ul>')
    lines.append('<p>Evidence indicates text recognized in the uploaded resume, not verified proficiency. Not detected does not mean not possessed. Experience and credentials require manual review.</p>')
    lines.append(f"<p>{escape(result['disclaimer'])}</p>")
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Job match report</title>'
       '<style>body{font-family:Arial;max-width:800px;margin:40px auto;color:#20263b}h1{color:#484baf}</style>'
       '</head><body>'+''.join(lines)+'</body></html>').encode('utf8')

def render_pdf_report(result):
    stream=BytesIO();pdf=canvas.Canvas(stream,pagesize=A4)
    width,height=A4;y=height-45
    def line(value,bold=False):
        nonlocal y
        if y<55:pdf.showPage();y=height-45
        pdf.setFont('Helvetica-Bold' if bold else 'Helvetica',11 if bold else 9)
        # Built-in PDF font supports latin-1; replace unrepresentable glyphs safely.
        clean=value.encode('latin-1','replace').decode('latin-1')
        while clean:
            pdf.drawString(45,y,clean[:100]);clean=clean[100:];y-=15
    line('AI Resume Analyzer | Job Match Report',True)
    line('Job: '+result['job_title'])
    title_only = result.get('analysis_mode', 'role-alignment' if result.get('requirements_status') == 'title-suggestions' else 'job-description') == 'role-alignment'
    label='Estimated role alignment' if title_only else 'Estimated job compatibility'
    score=str(result['match_score'])+'/100' if result.get('match_score') is not None else 'Not assessed'
    line(label+': '+score)
    if title_only:
        line('No employer description: required and preferred skills not assessed.')
    elif result.get('similarity_score') is not None:
        line('JD text similarity: '+str(result['similarity_score'])+'/100')
    if result.get('suggested_role_skills'):
        y-=7;line('Typical role skills (not employer-confirmed)',True)
        for skill in result['suggested_role_skills']:line(' - '+skill)
    for key,label in ([] if title_only else [('matched_required','Matched required skills'),('missing_required','Missing required skills'),('matched_preferred','Matched preferred skills'),('missing_preferred','Missing preferred skills')]):
        y-=7;line(label,True)
        for skill in result[key]:line(' - '+skill)
    if not title_only:
        y-=7;line('Line-by-line job description assessment',True)
        for row in result.get('requirement_evidence', []):
            line(f"[{row['priority']}; {row['status']}] {row['text']}")
            line('  Detected: '+(', '.join(row['matched']) or 'None'))
            line('  Not detected: '+(', '.join(row['not_found']) or 'None'))
        y-=7;line('Improvement suggestions',True)
        for item in result.get('improvement_suggestions', []):line(' - '+item)
    y-=7;line('Matching recognizes resume text, not verified competence, education or experience.')
    line('Not detected in a resume does not mean the candidate lacks a skill.')
    line('Method: '+result.get('scoring_methodology','Heuristic matching.'))
    y-=8;line(result['disclaimer'])
    pdf.save();return stream.getvalue()
