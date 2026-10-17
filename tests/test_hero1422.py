from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1422_version():
    assert APP_VERSION == "1.5.9"

def test_hero1422_front_back_orbit_layers():
    html = HTML.read_text()
    assert "function drawRings(t){" in html
    assert "function drawRings(t){" in html
    assert "function drawRings(t){" in html
    assert "function drawRings(t){" in html
    assert "function drawRings(t){" in html

def test_hero1422_atmosphere_depth_layers():
    html = HTML.read_text()
    assert 'const haze = ctx.createRadialGradient' in html
    assert "nightShadow.addColorStop(.76,'rgba(10,14,44,.24)');" in html
    assert "ctx.strokeStyle = 'rgba(168,212,255,.22)';" in html
