from pathlib import Path
from app.config import APP_VERSION
from app.ui.sphere import HERO_PATH

def test_hero_overlay_and_network():
    assert APP_VERSION == "1.5.9.9.6"
    html=HERO_PATH.read_text(encoding="utf-8")
    assert 'class="hero-copy"' in html
    assert 'function drawSphere(t)' in html
    assert 'edges = []' in html
    assert 'for(const [i,j,dist] of edges)' in html
    assert 'prefers-reduced-motion' in html

def test_home_uses_single_hero_component():
    src=(Path(__file__).resolve().parents[1]/"app/pages/home.py").read_text(encoding="utf-8")
    assert 'render_intelligence_hero(650)' in src
    assert 'st.columns([1.1, 0.9]' not in src
