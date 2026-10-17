from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1416_version():
    assert APP_VERSION == "1.5.7.4"

def test_hero1416_polish_values():
    html = HTML.read_text()
    assert "width:6.3, glow:24" in html
    assert "width:5.0, glow:22" in html
    assert "function drawRings(t){" in html
    assert "flare: hero || Math.random() > 0.965" in html
    assert "const halo = s.r * (s.hero ? (7.0 + shimmer*5.2) : s.accent ? (3.3 + shimmer*1.9) : (1.4 + shimmer*1.2));" in html
