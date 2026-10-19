from pathlib import Path
from app.config import APP_VERSION

CSS = Path(__file__).resolve().parents[1] / "app" / "assets" / "styles.css"

def test_global_scroll_release():
    assert APP_VERSION == "1.5.9.9.5"
    text = CSS.read_text(encoding="utf-8")
    for token in ("ara-spatial-heading-159994", "ara-spatial-card-159994",
                  "ara-spatial-journey-left-159994", "ara-spatial-orbit-159994",
                  "animation-timeline:view(block)"):
        assert token in text

def test_accessible_scroll_and_safe_controls():
    text = CSS.read_text(encoding="utf-8")
    segment = text.split("/* v1.5.9.9.4", 1)[1]
    assert "prefers-reduced-motion: reduce" in segment
    for forbidden in ("stSidebarContent", "stDataFrame", "stForm", "stDownloadButton"):
        assert forbidden not in segment
    assert "opacity:1!important" in segment
