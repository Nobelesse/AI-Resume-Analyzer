from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_subtle_motion_and_theme():
    js=(ROOT/'app/ui/web/scroll_engine.js').read_text()
    css=(ROOT/'app/assets/styles.css').read_text()
    assert 'entering * 7' in js
    assert 'ara-spotlight-progress' in js
    assert 'ara-polished-visible' in css
    assert 'translate3d(' in js
    assert 'scale(' not in js
    assert 'rotateY(' not in js
    assert 'stSidebarContent' in css
