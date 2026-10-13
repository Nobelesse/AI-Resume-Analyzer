from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1419_version():
    assert APP_VERSION == "1.4.2.6"

def test_hero1419_planet_and_abyss_values():
    html = HTML.read_text()
    assert "linear-gradient(118deg,#030816 0%,#071124 35%,#08132a 64%,#030915 100%)" in html
    assert "cx = w * (mobile ? 0.545 : 0.792);" in html
    assert "width:6.8, glow:32" in html
    assert "width:5.4, glow:28" in html
    assert "function drawRings(t){" in html
    assert "const atmosphere = ctx.createRadialGradient" in html
