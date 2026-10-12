from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1415_orbits_and_stars():
    assert APP_VERSION == "1.4.2"
    html = HTML.read_text()
    assert "width:4.9, glow:24" in html
    assert "twinkle:" in html
    assert "if(s.flare)" in html
    assert "ctx.strokeStyle = ring.core || ring.color;" in html
    assert "Math.max(108, Math.floor((w*h)/4700))" in html
