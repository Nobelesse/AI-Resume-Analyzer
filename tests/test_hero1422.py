from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1422_version():
    assert APP_VERSION == "1.4.2.2"

def test_hero1422_front_back_orbit_layers():
    html = HTML.read_text()
    assert "function drawRings(t, layer='all')" in html
    assert 'drawRings(t, "back")' in html
    assert 'drawRings(t, "front")' in html
    assert 'const isBack = pt => pt.z < -0.04;' in html
    assert 'const isFront = pt => pt.z >= -0.04;' in html

def test_hero1422_atmosphere_depth_layers():
    html = HTML.read_text()
    assert 'const haze = ctx.createRadialGradient' in html
    assert "nightShadow.addColorStop(.76,'rgba(10,14,44,.24)');" in html
    assert "ctx.strokeStyle = 'rgba(168,212,255,.22)';" in html
