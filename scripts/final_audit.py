"""Local Phase 8 project audit. Safe to run without using any user data."""
from pathlib import Path
import ast
import re
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.config import APP_VERSION, SUPPORTED_EXTENSIONS, MAX_RESUME_BYTES

def audit():
    assert MAX_RESUME_BYTES == 2_000_000
    assert set(SUPPORTED_EXTENSIONS) == {'pdf','docx','txt','rtf','odt'}
    code = (ROOT/'app/main.py').read_text(encoding='utf8')
    page_paths = re.findall(r'url_path=["\']([^"\']+)', code)
    assert len(page_paths) >= 15 and len(page_paths) == len(set(page_paths)), 'Duplicate navigation pathname'
    for filename in ROOT.rglob('*.py'):
        if any(x in filename.parts for x in ('.venv','venv')): continue
        ast.parse(filename.read_text(encoding='utf8'), filename=str(filename))
    private = list((ROOT/'data').glob('*.sqlite3')) if (ROOT/'data').exists() else []
    print('PASS: Version', APP_VERSION)
    print('PASS: Upload size and extensions')
    print('PASS: Unique Streamlit URL paths:', len(page_paths))
    print('PASS: Python source parsing')
    print('INFO: Existing SQLite files (private, excluded from Git):',len(private))
    return 0

if __name__ == '__main__':
    raise SystemExit(audit())
