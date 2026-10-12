from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1419_version():
    assert APP_VERSION == "1.4.1.9"

def test_hero1419_planet_and_abyss_values():
    html = HTML.read_text()
    assert "linear-gradient(118deg,#030816 0%,#071124 35%,#08132a 64%,#030915 100%)" in html
    assert "cx = w * (mobile ? 0.545 : 0.826);" in html
    assert "width:4.9, glow:24" in html
    assert "width:3.7, glow:20" in html
    assert "Math.max(108, Math.floor((w*h)/4700))" in html
    assert "const atmosphere = ctx.createRadialGradient" in html
