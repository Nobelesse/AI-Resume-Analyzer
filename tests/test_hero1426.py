from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_version():
    assert APP_VERSION == "1.5.8"

def test_fast_closed_orbits():
    html = HTML.read_text(encoding="utf-8")
    assert 'ctx.closePath();' in html
    assert 'function drawRings(t){' in html
    assert 'drawSphere(t);\n    drawRings(t);' in html
    assert 'pointer.y*0.24' not in html
    assert 'dpr=Math.min(window.devicePixelRatio||1,1.5)' in html
    assert 'now - previousFrame < 33' in html
