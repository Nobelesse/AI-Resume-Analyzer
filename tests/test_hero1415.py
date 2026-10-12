from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1415_orbits_and_stars():
    assert APP_VERSION == "1.4.2.2"
    html = HTML.read_text()
    assert "width:6.2, glow:30" in html
    assert "twinkle:" in html
    assert "if(s.flare)" in html
    assert "strokeOrbitSection(points, isFront, ring.core || ring.color" in html
    assert "Math.max(108, Math.floor((w*h)/4700))" in html
