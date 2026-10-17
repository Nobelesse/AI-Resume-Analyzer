"""Run controlled ATS validation without accessing user resumes or a private DB."""
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.database.connection import initialize_database
from app.services.ats_validation import run_benchmark

with tempfile.TemporaryDirectory(prefix='ara_ats_validation_') as tmp:
    db=Path(tmp)/'benchmark.sqlite3'
    initialize_database(db)
    result=run_benchmark(db_path=db)
print(json.dumps(result, indent=2))
raise SystemExit(0 if result['passed']==result['total'] else 1)
