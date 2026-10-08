"""Resource-limited extraction of readable text from supported CV formats."""
from __future__ import annotations
import io
import re
import zipfile
from xml.etree import ElementTree as ET
from html import unescape
from pypdf import PdfReader
from docx import Document
from app.config import MAX_RESUME_BYTES, SUPPORTED_EXTENSIONS

class ResumeValidationError(ValueError):
    """Invalid, unsupported, or unsafe document."""

MAX_TEXT_LENGTH = 350_000
MAX_ARCHIVE_TOTAL_BYTES = 12 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 150

def _check_archive(data: bytes, required: str) -> None:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            infos=z.infolist()
            if len(infos)>MAX_ARCHIVE_ENTRIES or sum(x.file_size for x in infos)>MAX_ARCHIVE_TOTAL_BYTES:
                raise ResumeValidationError('Document archive exceeds processing limits.')
            if any(x.flag_bits & 1 for x in infos):
                raise ResumeValidationError('Encrypted document archives are not supported.')
            if required not in z.namelist():
                raise ResumeValidationError('Invalid document structure.')
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        raise ResumeValidationError('Unreadable document archive.') from exc

def _plain_text(data: bytes) -> str:
    for encoding in ('utf-8-sig','utf-16'):
        try: return data.decode(encoding)
        except UnicodeError: pass
    raise ResumeValidationError('TXT must be UTF-8 or UTF-16 encoded.')

def _rtf_text(data: bytes) -> str:
    # Simple, conservative RTF text conversion; formatting, embedded images are ignored.
    try: source=data.decode('latin-1')
    except UnicodeError as exc: raise ResumeValidationError('Invalid RTF.') from exc
    if not source.lstrip().startswith(r'{\rtf'):
        raise ResumeValidationError('Invalid RTF header.')
    source=re.sub(r'\\[\'"][0-9a-fA-F]{2}',lambda m: bytes([int(m.group()[2:],16)]).decode('cp1252',errors='replace'),source)
    source=re.sub(r'\\u(-?\d+)\??',lambda m: chr(int(m.group(1))%65536),source)
    source=re.sub(r'\\(par|line)\b ?', '\n',source)
    source=re.sub(r'\\[a-zA-Z]+-?\d* ?', '',source)
    source=re.sub(r'\\[^a-zA-Z\n]', '',source)
    return source.replace('{','').replace('}','')

def _odt_text(data: bytes) -> str:
    _check_archive(data,'content.xml')
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            mimetype=z.read('mimetype')
            if mimetype.strip()!=b'application/vnd.oasis.opendocument.text':
                raise ResumeValidationError('Invalid ODT content type.')
            xml=z.read('content.xml')
        root=ET.fromstring(xml)
    except (KeyError, ET.ParseError, ValueError, RuntimeError) as exc:
        raise ResumeValidationError('Unreadable ODT content.') from exc
    uri='{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'
    return '\n'.join(''.join(node.itertext()) for node in root.iter() if node.tag in (uri+'p',uri+'h'))

def extract_resume(filename: str, data: bytes) -> str:
    if not isinstance(data,bytes) or not data or len(data)>MAX_RESUME_BYTES:
        raise ResumeValidationError('Resume must be non-empty and at most 2 MiB (2,097,152 bytes).')
    if not isinstance(filename,str) or not filename.strip() or len(filename)>255:
        raise ResumeValidationError('Invalid filename.')
    ext=filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
    if ext not in SUPPORTED_EXTENSIONS:
        raise ResumeValidationError('Unsupported file type. Use PDF, DOCX, TXT, RTF, or ODT.')
    try:
        if ext=='pdf':
            if not data.startswith(b'%PDF-'):
                raise ResumeValidationError('Invalid PDF signature.')
            reader=PdfReader(io.BytesIO(data),strict=True)
            if reader.is_encrypted:
                raise ResumeValidationError('Password-protected PDFs are not supported.')
            if len(reader.pages)>100:
                raise ResumeValidationError('PDF has too many pages (maximum 100).')
            text='\n'.join(page.extract_text() or '' for page in reader.pages)
        elif ext=='docx':
            _check_archive(data,'word/document.xml')
            document=Document(io.BytesIO(data))
            text='\n'.join([p.text for p in document.paragraphs]+[cell.text for table in document.tables for row in table.rows for cell in row.cells])
        elif ext=='txt':
            if b'\x00' in data and not (data.startswith(b'\xff\xfe') or data.startswith(b'\xfe\xff')):
                raise ResumeValidationError('Binary content is not a text document.')
            text=_plain_text(data)
        elif ext=='rtf':
            text=_rtf_text(data)
        else:
            text=_odt_text(data)
    except ResumeValidationError:
        raise
    except Exception as exc:
        raise ResumeValidationError('The document could not be parsed. Check the format and try again.') from exc
    text=unescape(text).replace('\x00','').strip()
    if not text:
        raise ResumeValidationError('No extractable text found. Scanned images/OCR are not supported yet.')
    if len(text)>MAX_TEXT_LENGTH:
        raise ResumeValidationError('Extracted text is longer than the allowed processing limit.')
    return text
