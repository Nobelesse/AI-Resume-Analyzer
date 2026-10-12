from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_hero1421_version():
    assert APP_VERSION == "1.4.2.4"

def test_hero1421_scale_and_orbit_values():
    html = HTML.read_text()
    assert "cx = w * (mobile ? 0.545 : 0.792);" in html
    assert "h * (mobile ? 0.242 : 0.348)" in html
    assert "width:6.8, glow:32" in html
    assert "width:5.4, glow:28" in html
    assert "strokeOrbitSection(points, isFront, ring.color, ring.width || (idx===0 ? 6.8 : 5.4)" in html
