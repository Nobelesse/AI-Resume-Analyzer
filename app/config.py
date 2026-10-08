"""Central application settings (Python 3.11)."""
import os
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "AI Resume Analyzer"
APP_VERSION = "0.4.0"
MAX_RESUME_BYTES = 2 * 1024 * 1024
SUPPORTED_EXTENSIONS = ("pdf", "docx", "txt", "rtf", "odt")
GITHUB_URL = "https://github.com/Nobelesse/AI-Resume-Analyzer"
DATABASE_PATH = Path(os.environ.get("ARA_DATABASE_PATH", str(PROJECT_ROOT / "data" / "resume_analyzer.sqlite3"))).resolve()
