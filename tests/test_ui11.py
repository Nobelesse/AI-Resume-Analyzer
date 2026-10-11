"""Regression tests for immersive UI 1.1 design changes."""
from pathlib import Path
from app.config import APP_VERSION
ROOT=Path(__file__).resolve().parents[1]
def read(path):return (ROOT/path).read_text(encoding="utf-8")
def test_ui11_version_and_animated_orb():
    assert APP_VERSION == "1.1.0"
    hero=read("app/pages/home.py")
    styles=read("app/assets/styles.css")
    assert "v11-starfield" in hero and "v11-orbit-c" in hero
    assert "v11-twinkle" in styles and "v11-system-drift" in styles
def test_accessible_motion():
    assert "prefers-reduced-motion:reduce" in read("app/assets/styles.css")
    assert "prefers-reduced-motion" in read("app/ui/web/motion.html")
def test_experience_is_real_navigation():
    body=read("app/pages/design_lab.py")
    assert "navigation_card(" in body and "session_user()" in body
    assert "Experience Center" in read("app/main.py")
