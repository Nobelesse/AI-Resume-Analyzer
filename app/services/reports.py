"""Portable offline HTML and PDF reports. Escape all user-controlled content."""
from html import escape
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def render_html_report(result):
    title=escape(result['job_title'])
    lines=[f'<h1>Job Match — {title}</h1>',f"<p>Estimated match: {result['match_score']}/100</p>",
      f"<p>Text similarity: {result['similarity_score']}/100</p>"]
    for key,label in [('matched_required','Matched required skills'),('missing_required','Missing required skills'),('matched_preferred','Matched preferred skills'),('missing_preferred','Missing preferred skills')]:
        lines.append(f'<h2>{label}</h2><ul>')
        lines.extend(f'<li>{escape(str(s))}</li>' for s in result[key])
        lines.append('</ul>')
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
    line('Estimated match: '+str(result['match_score'])+'/100')
    line('Text similarity: '+str(result['similarity_score'])+'/100')
    for key,label in [('matched_required','Matched required skills'),('missing_required','Missing required skills'),('matched_preferred','Matched preferred skills'),('missing_preferred','Missing preferred skills')]:
        y-=7;line(label,True)
        for skill in result[key]:line(' - '+skill)
    y-=8;line(result['disclaimer'])
    pdf.save();return stream.getvalue()
