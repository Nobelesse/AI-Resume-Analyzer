from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")


def test_hero1424_version():
    assert APP_VERSION == "1.5.8"


def test_hero1424_uses_continuous_orbit_sampling_and_smoothing():
    html = HTML.read_text()
    assert "for(let i=0;i<=360;i++)" in html
    assert "function drawRings(t){" in html
    assert "ctx.closePath();" in html
    assert "function drawRings(t){" in html


def test_hero1424_release_notes_present():
    notes = Path("docs/VERSION_1_4_2_4_ORBIT_PROFESSIONAL_FIX.md").read_text()
    assert "Orbit Continuity Professional Fix" in notes
