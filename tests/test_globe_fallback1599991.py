from pathlib import Path
from app.config import APP_VERSION
from app.ui.native_hero import render_native_hero, ORB_SVG

def test_globe_has_visible_svg_fallback(monkeypatch):
    import sys, types
    fake = types.ModuleType('streamlit')
    captured=[]
    fake.markdown=lambda value, **kwargs: captured.append(value)
    monkeypatch.setitem(sys.modules,'streamlit',fake)
    render_native_hero()
    assert 'ara-orb-fallback' in captured[0]
    assert '<svg' in captured[0]
    assert 'ara-premium-artwork' in captured[0]

def test_canvas_only_hides_fallback_after_draw():
    root=Path(__file__).resolve().parents[1]
    script=(root/'app/ui/web/premium_globe.js').read_text()
    style=(root/'app/assets/styles.css').read_text()
    assert "classList.add('ara-canvas-ready')" in script
    assert "classList.remove('ara-canvas-ready')" in script
    assert '.ara-native-orb-shell.ara-canvas-ready .ara-orb-fallback' in style

def test_patch_version():
    assert APP_VERSION == '1.5.9.9.12'
