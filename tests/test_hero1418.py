from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1418_version():
    assert APP_VERSION == "1.4.2.2"

def test_hero1418_spacing_and_stars():
    html = HTML.read_text()
    assert "cx = w * (mobile ? 0.545 : 0.792);" in html
    assert "Math.max(108, Math.floor((w*h)/4700))" in html
    assert "flare: hero || Math.random() > 0.965" in html
    assert "const core = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, halo);" in html
    assert "pointer.x += (pointer.tx - pointer.x) * 0.135;" in html
