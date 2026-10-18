from pathlib import Path
from app.config import APP_VERSION

CSS = Path(__file__).resolve().parents[1] / "app" / "assets" / "styles.css"

def test_global_scroll_release():
    assert APP_VERSION == "1.5.9.9.3"
    text = CSS.read_text(encoding="utf-8")
    assert "ara-celestial-heading" in text
    assert "ara-celestial-card" in text
    assert "ara-celestial-orbit-depth" in text
    assert "animation-timeline: view(block)" in text

def test_accessible_scroll_and_safe_controls():
    text = CSS.read_text(encoding="utf-8")
    segment = text.split("/* v1.5.9.9.3", 1)[1]
    assert "prefers-reduced-motion: reduce" in segment
    assert 'stSidebarContent' not in segment
    assert 'stDataFrame' not in segment
    assert 'stForm' not in segment
    assert 'stDownloadButton' not in segment
    assert 'opacity:1!important' in segment
