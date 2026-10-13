from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")


def test_hero1423_version():
    assert APP_VERSION == "1.5.5"


def test_hero1423_orbit_continuity_helpers():
    html = HTML.read_text()
    assert "function drawRings(t){" in html
    assert "function drawRings(t){" in html
    assert "function drawRings(t){" in html
    assert "ctx.lineJoin = 'round';" in html


def test_hero1423_continuity_release_notes_present():
    notes = Path("docs/VERSION_1_4_2_3_ORBIT_CONTINUITY.md").read_text()
    assert "Orbit Continuity & Smooth 3D Fix" in notes
