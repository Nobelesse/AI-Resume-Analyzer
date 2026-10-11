from pathlib import Path
from app.config import APP_VERSION
from app.ui.sphere import HERO_PATH

def test_cinematic_hero_source():
    html = HERO_PATH.read_text(encoding="utf-8")
    assert APP_VERSION == "1.4.1.3"
    assert 'class="hero-copy"' in html
    assert "linear-gradient(90deg" in html
    assert "edges = []" in html
    assert "visibilitychange" in html
    assert "prefers-reduced-motion" in html

def test_taller_home_hero():
    home = (Path(__file__).resolve().parents[1]/"app/pages/home.py").read_text(encoding="utf-8")
    assert "render_intelligence_hero(650)" in home
    assert "guest-card-info-gap" in home
