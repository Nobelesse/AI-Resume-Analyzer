from pathlib import Path
from app.config import APP_VERSION

def test_version_142():
    assert APP_VERSION == "1.5.9.9.9.5"

def test_hero_visual_polish():
    html = Path("app/ui/web/intelligence_hero.html").read_text(encoding="utf-8")
    assert "cx = w * (mobile ? 0.56 : 0.755);" in html
    assert "ctx.closePath();" in html
    assert "prefers-reduced-motion:reduce" in html
    assert 'background:none!important' in html
