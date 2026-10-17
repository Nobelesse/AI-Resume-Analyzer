"""UI 1.3 smoke tests: performance, accessibility and stable navigation."""
from pathlib import Path
from app.config import APP_VERSION, MAX_RESUME_BYTES

ROOT = Path(__file__).resolve().parents[1]


def test_version_and_upload_limit():
    assert APP_VERSION == "1.5.7.2"
    assert MAX_RESUME_BYTES == 2_000_000


def test_animation_pauses_on_hidden_tabs():
    for file in ("intelligence_hero.html", "intelligence_sphere.html"):
        html = (ROOT / "app" / "ui" / "web" / file).read_text(encoding="utf-8")
        assert "visibilitychange" in html
        assert "cancelAnimationFrame" in html
        assert "pointermove" in html


def test_css_accessibility_and_responsive():
    css = (ROOT / "app" / "assets" / "styles.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion:reduce" in css
    assert "focus-visible" in css
    assert "@media(max-width:800px)" in css


def test_existing_navigation_routes_preserved():
    navigation = (ROOT / "app/ui/navigation.py").read_text(encoding="utf-8")
    for route in ("resume-analysis", "career-finder", "job-match", "admin-dashboard", "audit-log"):
        assert f'"{route}"' in navigation
