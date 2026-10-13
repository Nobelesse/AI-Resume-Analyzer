from pathlib import Path
from app.config import APP_VERSION
from app.ui.sphere import HERO_PATH

def test_full_orb_camera_framing():
    html=HERO_PATH.read_text(encoding="utf-8")
    assert APP_VERSION == "1.5.2"
    assert "const FRAME_PADDING = 24" in html
    assert "const orbitBound = mobile ? 2.08 : 1.90" in html
    assert "(w - cx - FRAME_PADDING) / orbitBound" in html
    assert "(h - cy - FRAME_PADDING) / orbitBound" in html
    assert "const depth = 4.25" in html

def test_depth_and_motion():
    html=HERO_PATH.read_text(encoding="utf-8")
    for feature in ("const aura", "const beam", "pointer.x", "pointer.y", "visibilitychange", "prefers-reduced-motion", "requestAnimationFrame"):
        assert feature in html
    assert 'class="hero-copy"' in html
    assert "const n = 270" in html
