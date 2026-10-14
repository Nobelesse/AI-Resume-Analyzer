"""Regression tests for UI 1.2 intelligence sphere."""
from pathlib import Path

from app.config import APP_VERSION
from app.ui.sphere import SCENE_PATH

ROOT = Path(__file__).resolve().parents[1]


def test_release_version_ui12():
    assert APP_VERSION == "1.5.7"


def test_sphere_component_asset_exists():
    assert SCENE_PATH.exists()
    html = SCENE_PATH.read_text(encoding="utf-8")
    assert "Interactive Intelligence Core" in html
    assert "requestAnimationFrame(frame)" in html


def test_home_and_experience_center_use_sphere():
    home = (ROOT / "app/pages/home.py").read_text(encoding="utf-8")
    design = (ROOT / "app/pages/design_lab.py").read_text(encoding="utf-8")
    assert "render_intelligence_hero(" in home
    assert "intelligence_sphere(" in design
    assert "v10-orb" not in home
