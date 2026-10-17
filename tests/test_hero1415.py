from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1415_orbits_and_stars():
    assert APP_VERSION == "1.5.9"
    html = HTML.read_text()
    assert "width:6.3, glow:24" in html
    assert "twinkle:" in html
    assert "if(s.flare)" in html
    assert "function drawRings(t){" in html
    assert "function drawRings(t){" in html
