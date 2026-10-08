"""Verify that the Phase 2 UX remains honest and self-contained."""
from pathlib import Path
from app.config import APP_VERSION, MAX_RESUME_BYTES, SUPPORTED_EXTENSIONS
import ast
ROOT = Path(__file__).resolve().parents[1]
SCENE_PATH = ROOT / "app" / "ui" / "web" / "motion.html"

def get_phases():
    tree = ast.parse((ROOT / "app" / "pages" / "roadmap.py").read_text(encoding="utf-8"))
    return ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PHASES" for t in n.targets)))

def test_version_and_contract():
    assert APP_VERSION == "0.4.0"
    assert MAX_RESUME_BYTES == 2 * 1024 * 1024
    assert len(SUPPORTED_EXTENSIONS) == 5

def test_roadmap_has_eight_milestones():
    assert len(get_phases()) == 8
    assert [x[0] for x in get_phases()] == [f"{i:02}" for i in range(1, 9)]

def test_scene_is_local_and_accessible():
    html = SCENE_PATH.read_text(encoding="utf-8")
    assert "prefers-reduced-motion" in html
    assert "pointermove" in html
    assert "https://" not in html
    assert "aria-label" in html

def test_assets_exist():
    assert (Path(__file__).resolve().parents[1] / "app" / "assets" / "styles.css").is_file()
