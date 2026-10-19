from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_cinematic_transforms_and_safety():
    js = (ROOT/'app/ui/web/scroll_engine.js').read_text(encoding='utf8')
    assert 'state.direction' in js
    assert 'translate3d(' in js and 'scale(' in js
    assert 'rotateX(' not in js and 'rotateY(' not in js
    assert 'prefers-reduced-motion: reduce' in js
    assert '[data-testid="stSidebar"]' in js
    assert 'MutationObserver' in js

def test_version():
    from app.config import APP_VERSION
    assert APP_VERSION == '1.5.9.9.6'
