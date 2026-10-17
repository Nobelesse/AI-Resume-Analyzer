from app.services.ats_report import build_ats_pdf_report
from pypdf import PdfReader
from io import BytesIO
from pathlib import Path


def test_downloaded_pdf_matches_assessment_data():
    readiness={'score':42,'components':{'Resume sections':14,'Contact details':15,'Skill evidence':4,'Substance':0,'Bullet formatting':0,'Quantified impact':0},
        'disclaimer':'Not an employer ATS score.', 'checks':[{'check':'Email','status':'detected','detail':'Text present'}],
        'skills':['Python','SQL'], 'recommendations':['Add concrete experience.']}
    pdf=build_ats_pdf_report(readiness,resume_filename='Example.pdf')
    assert pdf.startswith(b'%PDF')
    text=' '.join(page.extract_text() for page in PdfReader(BytesIO(pdf)).pages)
    for expected in ['42/100','Resume sections: 14 / 35','Python','SQL','Example.pdf','Not assessed','Add concrete experience']:
        assert expected in text


def test_report_with_job_compatibility():
    readiness={'score':60,'components':{},'disclaimer':'Readiness estimate.', 'checks':[], 'skills':[], 'recommendations':[]}
    job={'score':None,'score_available':False,'disclaimer':'Not an ATS decision.','methodology':'Only verifiable evidence.',
         'matched':0,'partial':0,'not_found':0,'manual_review_count':1,
         'requirements':[{'priority':'required','status':'unverified','text':'5 years experience','matched':[],'not_found':[]}]}
    pdf=build_ats_pdf_report(readiness,job)
    text=' '.join(page.extract_text() for page in PdfReader(BytesIO(pdf)).pages)
    assert 'Not scored' in text and '5 years experience' in text and 'Manual review: 1' in text


def test_ats_page_has_no_fullscreen_chart():
    text=Path('app/pages/analysis_pages.py').read_text()
    section=text.split('def advanced_ats_intelligence():',1)[1].split('def analysis_history():',1)[0]
    assert 'st.bar_chart(' not in section
    assert 'st.download_button(' in section
