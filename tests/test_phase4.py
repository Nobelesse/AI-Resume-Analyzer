import io
import re
import zipfile
import pytest
from docx import Document
from app.config import MAX_RESUME_BYTES
from app.services.resume_parser import extract_resume,ResumeValidationError
from app.database.connection import initialize_database, connect
from app.database.resumes import save_resume, list_user_resumes, list_all_resumes, get_resume
from app.auth.service import register_user,create_initial_admin
from app.auth.permissions import AccessDenied

@pytest.fixture
def actors(tmp_path):
    db=tmp_path/'private.sqlite3'; initialize_database(db)
    a=register_user('a@example.com','User A','secure-password-123',db_path=db)
    b=register_user('b@example.com','User B','secure-password-123',db_path=db)
    admin=create_initial_admin('boss@example.com','Admin','secure-password-123',db_path=db)
    return db,tmp_path/'uploads',a,b,admin

def test_txt_limit_and_validation():
    assert extract_resume('resume.TXT',b'Python developer')=='Python developer'
    assert extract_resume('resume.txt',b'x'*300_000)
    assert extract_resume("resume.txt", (b"word ") * 40000)
    for name,content in [('a.txt',b''),('a.txt',b'x'*(MAX_RESUME_BYTES+1)),('a.pdf',b'not pdf'),('a.exe',b'data'),('a.txt',b'\x00\x01bad')]:
        with pytest.raises(ResumeValidationError):extract_resume(name,content)

def test_docx():
    document=Document(); document.add_paragraph('Cloud engineering and DevOps')
    output=io.BytesIO();document.save(output)
    assert 'Cloud engineering' in extract_resume('cv.docx',output.getvalue())

def test_odt():
    content=b'<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><office:body><office:text><text:p>Python SQL skills</text:p></office:text></office:body></office:document-content>'
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        z.writestr('mimetype','application/vnd.oasis.opendocument.text')
        z.writestr('content.xml',content)
    assert 'Python SQL' in extract_resume('cv.odt',out.getvalue())

def test_rtf():
    assert 'communication' in extract_resume('cv.rtf',b'{\\rtf1\\ansi communication\\par teamwork}')

def test_ownership_and_admin(actors):
    db,uploads,a,b,admin=actors
    rid=save_resume(a,'../resume.txt',b'Python and data analytics',db_path=db,uploads_dir=uploads)
    assert len(list_user_resumes(a,db_path=db))==1
    assert list_user_resumes(b,db_path=db)==[]
    assert get_resume(a,rid,db_path=db)['extracted_text']=='Python and data analytics'
    with pytest.raises(AccessDenied): get_resume(b,rid,db_path=db)
    with pytest.raises(AccessDenied): list_all_resumes(a,db_path=db)
    with pytest.raises(AccessDenied): save_resume(admin,'c.txt',b'Admin',db_path=db,uploads_dir=uploads)
    assert len(list_all_resumes(admin,db_path=db))==1
    assert get_resume(admin,rid,db_path=db)['owner_email']=='a@example.com'
    assert len(list(uploads.iterdir()))==1
    assert (list(uploads.iterdir())[0]).name!='resume.txt'

def test_invalid_upload_does_not_persist(actors):
    db,uploads,a,b,admin=actors
    with pytest.raises(ResumeValidationError):save_resume(a,'bad.pdf',b'invalid',db_path=db,uploads_dir=uploads)
    assert list_user_resumes(a,db_path=db)==[]

def test_upgrade_preserves_accounts(actors):
    db,uploads,a,b,admin=actors
    initialize_database(db)
    with connect(db) as c:
        assert c.execute('select count(*) from users').fetchone()[0]==3
        assert c.execute('pragma user_version').fetchone()[0]==3

def test_unique_streamlit_page_urls():
    source=__import__('pathlib').Path('app/main.py').read_text(encoding='utf8')
    urls=re.findall(r'url_path="([^"]+)"',source)
    assert len(urls)>=10
    assert len(urls)==len(set(urls)),f'Duplicate page URL: {urls}'
