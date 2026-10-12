from pathlib import Path
from app.config import APP_VERSION

def test_version_142():
    assert APP_VERSION == "1.4.2.2"

def test_hero_visual_polish():
    html = Path("app/ui/web/intelligence_hero.html").read_text(encoding="utf-8")
    assert "cx = w * (mobile ? 0.545 : 0.792);" in html
    assert "accentAngle" in html
    assert "prefers-reduced-motion:reduce" in html
    assert "radial-gradient(ellipse 36% 38%" in html
