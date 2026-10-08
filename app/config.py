"""Central project configuration for the foundation phase."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "AI Resume Analyzer"
APP_VERSION = "0.1.0"
MAX_RESUME_BYTES = 2 * 1024 * 1024
SUPPORTED_EXTENSIONS = ("pdf", "docx", "txt", "rtf", "odt")
GITHUB_URL = "https://github.com/Nobelesse/AI-Resume-Analyzer"
