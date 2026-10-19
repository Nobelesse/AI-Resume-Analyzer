from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def test_depth_motion_visible_and_upright():
    js=(ROOT/'app/ui/web/scroll_engine.js').read_text()
    css=(ROOT/'app/assets/styles.css').read_text()
    assert 'entering * 34' in js
    assert 'entering * 75' in js
    assert 'scale(' in js
    assert 'rotateY(' not in js and 'rotateX(' not in js
    assert 'transition: none !important;' in css
    assert 'prefers-reduced-motion: reduce' in js
