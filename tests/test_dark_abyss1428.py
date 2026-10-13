from pathlib import Path
from app.config import APP_VERSION

def test_release_and_global_theme():
    assert APP_VERSION == "1.4.2.8"
    css = Path("app/assets/styles.css").read_text()
    assert "Dark Abyss system" in css
    assert "--abyss-gold:#dec28a" in css
    assert '[data-testid="stSidebar"]' in css

def test_hero_orbit_clearance_and_continuity():
    html = Path("app/ui/web/intelligence_hero.html").read_text()
    assert "{r:1.30" in html
    assert "{r:1.43" in html
    assert "const orbitBound = 2.04" in html
    assert "ctx.closePath();" in html
    assert "const sys = rotate" in html
