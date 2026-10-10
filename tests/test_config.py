"""Foundation tests run without launching Streamlit."""
import ast
from pathlib import Path

from app.config import APP_NAME, MAX_RESUME_BYTES, SUPPORTED_EXTENSIONS


def test_foundation_settings():
    assert APP_NAME == "AI Resume Analyzer"
    assert MAX_RESUME_BYTES == 2_000_000
    assert {"pdf", "docx", "txt", "rtf", "odt"}.issubset(SUPPORTED_EXTENSIONS)


def test_eight_milestones():
    roadmap = Path(__file__).resolve().parents[1] / "app" / "pages" / "roadmap.py"
    module = ast.parse(roadmap.read_text(encoding="utf-8"))
    phases = next(
        ast.literal_eval(node.value)
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "PHASES" for target in node.targets)
    )
    assert len(phases) == 8
