"""Regression checks: plain UI, detailed reports, and JD heading parsing."""
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from app.database.connection import initialize_database
from app.services.job_matcher import compare_resume_to_job, requirement_evidence, split_requirements
from app.services.reports import render_pdf_report, render_html_report


def test_singular_required_skill_heading_is_not_requirement(tmp_path):
    db = tmp_path/'isolated.sqlite3'
    initialize_database(db)
    jd = 'Required Skill:\n- Python\n- SQL\n- FastAPI\nPreferred Skills:\n- Docker'
    rows = requirement_evidence(jd, {'Python', 'SQL'}, db_path=db)
    assert len(rows) == 4, rows
    assert [row['priority'] for row in rows] == ['required']*3+['preferred']
    assert all('Required Skill:' not in row['text'] for row in rows)
    required, preferred = split_requirements(jd)
    assert 'Required Skill:' not in required
    assert 'Docker' in preferred
    result = compare_resume_to_job('Python and SQL',jd,job_title='Backend Developer',db_path=db)
    assert not any('Required Skill:' in s for s in result['improvement_suggestions'])


def test_job_studio_screen_does_not_render_line_evidence_sections():
    page = Path(__file__).resolve().parents[1]/'app/pages/job_pages.py'
    src=page.read_text(encoding='utf-8')
    assert "with st.expander(f'{category} requirements" not in src
    assert "st.caption('Status: '" not in src
    assert 'Skills matched' in src and 'Skills to improve' in src


def test_pdf_html_retains_actual_detailed_findings(tmp_path):
    db=tmp_path/'isolated.sqlite3'
    initialize_database(db)
    jd='Required Skill:\n- Python\n- SQL\n- FastAPI'
    result=compare_resume_to_job('Python and SQL experience', jd, job_title='Backend Developer',db_path=db)
    result['job_title']='Backend Developer'
    html=render_html_report(result).decode('utf-8')
    assert 'Line-by-line job description assessment' in html
    assert 'FastAPI' in html
    assert 'Not detected' in html
    assert 'Required Skill:' not in html
    pdf=render_pdf_report(result)
    text=' '.join(page.extract_text() for page in PdfReader(BytesIO(pdf)).pages)
    assert 'Line-by-line job description assessment' in text
    assert 'FastAPI' in text
    assert 'Not detected' in text
    assert 'Required Skill:' not in text
