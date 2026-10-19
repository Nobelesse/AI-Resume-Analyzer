from pathlib import Path
from app.config import APP_VERSION

CSS = (Path(__file__).resolve().parents[1] / "app/assets/styles.css").read_text(encoding="utf-8")

def test_spatial_animations_are_geometric_not_fade():
    assert APP_VERSION == "1.5.9.9.9.3"
    part = CSS.split("/* v1.5.9.9.4", 1)[1]
    assert "rotateY(" in part and "rotateX(" in part
    assert "translate3d(" in part and "scale(" in part
    for animation in ("ara-spatial-heading-159994", "ara-spatial-card-159994",
                      "ara-spatial-journey-left-159994", "ara-spatial-journey-right-159994"):
        body = part.split("@keyframes " + animation, 1)[1].split("}", 1)[0]
        assert "opacity:" not in body and "filter:blur" not in body

def test_controls_excluded_from_motion_targets():
    part = CSS.split("/* v1.5.9.9.4", 1)[1]
    assert ".roadmap-row" in part and ".feature-card" in part
    assert "prefers-reduced-motion: reduce" in part
    assert "stSidebarContent" not in part and "stButton" not in part
