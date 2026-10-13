"""Regression tests for immersive UI design changes."""
from pathlib import Path
from app.config import APP_VERSION
ROOT=Path(__file__).resolve().parents[1]
def read(path):return (ROOT/path).read_text(encoding="utf-8")

def test_ui12_version_and_interactive_sphere():
    assert APP_VERSION == "1.5.4"
    hero = read("app/pages/home.py")
    sphere = read("app/ui/web/intelligence_sphere.html")
    assert "render_intelligence_hero(" in hero
    assert "Interactive Intelligence Core" in sphere
    assert "requestAnimationFrame(frame)" in sphere

def test_accessible_motion():
    assert "prefers-reduced-motion:reduce" in read("app/assets/styles.css")
    assert "prefers-reduced-motion" in read("app/ui/web/intelligence_sphere.html")

def test_experience_is_real_navigation():
    body = read("app/pages/design_lab.py")
    assert "navigation_card(" in body and "session_user()" in body
    assert "Experience Center" in read("app/main.py")
