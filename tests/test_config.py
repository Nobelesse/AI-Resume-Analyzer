"""Foundation tests run without launching Streamlit."""
import ast
from pathlib import Path

from app.config import APP_NAME, MAX_RESUME_BYTES, SUPPORTED_EXTENSIONS


def test_foundation_settings():
    assert APP_NAME == "AI Resume Analyzer"
    assert MAX_RESUME_BYTES == 2_000_000
    assert {"pdf", "docx", "txt", "rtf", "odt"}.issubset(SUPPORTED_EXTENSIONS)


def test_system_workflow_has_six_real_user_steps():
    import ast
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / "app" / "pages" / "roadmap.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    render = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "render")
    steps = next(ast.literal_eval(n.value) for n in ast.walk(render)
                 if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "stages" for t in n.targets))
    assert len(steps) == 6
    assert [step[0] for step in steps] == ["01", "02", "03", "04", "05", "06"]
    labels = " ".join(step[1] for step in steps).lower()
    for keyword in ("upload", "extract", "skills", "job", "career", "results"):
        assert keyword in labels
