from pathlib import Path
from app.ui import native_hero
from app.config import APP_VERSION

def test_reference_globe_artwork():
    path=Path(native_hero.__file__).resolve().parents[1]/'assets'/'premium_globe_art.webp'
    assert path.is_file() and path.stat().st_size>10000
    assert APP_VERSION=='1.5.9.9.9.2'

def test_native_render_no_iframe():
    import inspect
    src=inspect.getsource(native_hero.render_native_hero)
    assert 'ara-premium-artwork' in src
    assert 'data:image/webp;base64,' in src
    assert 'components.html' not in src
