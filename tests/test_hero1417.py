from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1417_version():
    assert APP_VERSION == "1.4.2"

def test_hero1417_motion_and_realism_values():
    html = HTML.read_text()
    assert "cx = w * (mobile ? 0.545 : 0.785);" in html
    assert "Math.max(108, Math.floor((w*h)/4700))" in html
    assert "flare: hero || Math.random() > 0.965" in html
    assert "const ay = pointer.x * 0.50 + t * (reduce ? 0 : 0.36);" in html
    assert "pointer.x += (pointer.tx - pointer.x) * 0.135;" in html
