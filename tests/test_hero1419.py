from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1419_version():
    assert APP_VERSION == "1.5.9.4"

def test_hero1419_planet_and_abyss_values():
    html = HTML.read_text()
    assert "linear-gradient(118deg,rgba(2,5,13,.46) 0%,rgba(5,11,24,.40) 35%,rgba(8,19,38,.35) 64%,rgba(3,7,17,.42) 100%)" in html
    assert "cx = w * (mobile ? 0.56 : 0.755);" in html
    assert "width:6.3, glow:24" in html
    assert "width:5.0, glow:22" in html
    assert "function drawRings(t){" in html
    assert "const atmosphere = ctx.createRadialGradient" in html
