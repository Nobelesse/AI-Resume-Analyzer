from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1417_version():
    assert APP_VERSION == "1.5.5"

def test_hero1417_motion_and_realism_values():
    html = HTML.read_text()
    assert "cx = w * (mobile ? 0.56 : 0.755);" in html
    assert "function drawRings(t){" in html
    assert "flare: hero || Math.random() > 0.965" in html
    assert "const ay = pointer.x * 0.50 + t * (reduce ? 0 : 0.36);" in html
    assert "pointer.x += (pointer.tx - pointer.x) * 0.115;" in html
