from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1415_orbits_and_stars():
    assert APP_VERSION == "1.4.1.6"
    html = HTML.read_text()
    assert "width:3.25" in html
    assert "twinkle:" in html
    assert "if(s.cross || s.r > 1.05)" in html
    assert "ctx.strokeStyle = ring.core || ring.color;" in html
    assert "Math.max(72, Math.floor((w*h)/6200))" in html
