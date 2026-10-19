from pathlib import Path
from app.config import APP_VERSION
from app.ui.native_hero import render_native_hero
ROOT = Path(__file__).resolve().parents[1]
GLOBE_SCRIPT_PATH = ROOT / "app/ui/web/premium_globe.js"
SCRIPT_PATH = ROOT / "app/ui/web/scroll_engine.js"


def test_premium_globe_renderer_is_local_and_transparent():
    assert APP_VERSION == '1.5.9.9.9.2'
    js = GLOBE_SCRIPT_PATH.read_text(encoding='utf-8')
    assert "clearRect" in js and "getContext('2d',{alpha:true})" in js
    assert "requestAnimationFrame" in js
    assert "prefers-reduced-motion" in js
    assert "IntersectionObserver" in js
    assert "fetch(" not in js and "XMLHttpRequest" not in js
    assert 'window.open(' not in js


def test_native_globe_has_no_iframe():
    import inspect
    source = inspect.getsource(render_native_hero)
    assert 'ara-premium-artwork' in source
    assert 'components.html' not in source
    assert 'iframe' not in source.split('st.markdown(')[-1]


def test_scroll_layers_stay_upright():
    js = SCRIPT_PATH.read_text(encoding='utf-8')
    assert 'hero-title' in js and 'hero-description' in js
    assert 'hero-kicker' in js and 'hero-pills' in js
    assert 'entering * 56' in js and 'entering * 105' in js
    assert 'rotateX(' not in js and 'rotateY(' not in js
