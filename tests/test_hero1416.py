from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1416_version():
    assert APP_VERSION == "1.4.2"

def test_hero1416_polish_values():
    html = HTML.read_text()
    assert "width:4.9, glow:24" in html
    assert "width:3.7, glow:20" in html
    assert "Math.max(108, Math.floor((w*h)/4700))" in html
    assert "flare: hero || Math.random() > 0.965" in html
    assert "const halo = s.r * (s.hero ? (7.0 + shimmer*5.2) : s.accent ? (3.3 + shimmer*1.9) : (1.4 + shimmer*1.2));" in html
