from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")


def test_hero1425_version():
    assert APP_VERSION == "1.5.1"


def test_hero1425_continuous_orbit_fix_present():
    html = HTML.read_text()
    assert "function drawRings(t){" in html
    assert "ctx.closePath();" in html
    assert "function drawRings(t){" in html
    assert "function drawRings(t){" in html


def test_hero1425_release_notes_present():
    notes = Path("docs/VERSION_1_4_2_5_TRUE_CONTINUOUS_ORBIT.md").read_text()
    assert "True Continuous Orbit Fix" in notes
