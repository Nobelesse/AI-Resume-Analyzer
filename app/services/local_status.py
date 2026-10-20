"""Quick, read-only local runtime checks (no network beyond localhost)."""
import json
import sqlite3
import urllib.request
from app.config import DATABASE_PATH

def ollama_status(timeout=0.35):
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=timeout) as response:
            payload = json.load(response)
        return {"connected": True, "models": [x.get("name", "") for x in payload.get("models", [])]}
    except (OSError, ValueError, TypeError):
        return {"connected": False, "models": []}

def catalog_status():
    if not DATABASE_PATH.is_file():
        return {"ready": False, "occupations": 0, "skills": 0}
    try:
        with sqlite3.connect(f"file:{DATABASE_PATH.as_posix()}?mode=ro", uri=True, timeout=0.25) as db:
            occupations = db.execute("SELECT COUNT(*) FROM tax_occupations").fetchone()[0]
            skills = db.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
        return {"ready": occupations > 0 and skills > 0, "occupations": occupations, "skills": skills}
    except sqlite3.Error:
        return {"ready": False, "occupations": 0, "skills": 0}
