from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1416_version():
    assert APP_VERSION == "1.4.1.6"

def test_hero1416_polish_values():
    html = HTML.read_text()
    assert "width:3.25" in html
    assert "width:2.55" in html
    assert "Math.max(72, Math.floor((w*h)/6200))" in html
    assert "cross: Math.random() > 0.56" in html
    assert "glow = s.r * (3.0 + shimmer*3.6)" in html
