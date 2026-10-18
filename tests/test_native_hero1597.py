from pathlib import Path
from app.config import APP_VERSION
from app.ui.native_hero import ORB_SVG
from app.ui import sphere

def test_no_iframe_for_overview_hero():
    assert APP_VERSION == "1.5.9.9.3"
    assert "render_native_hero(height=height)" in Path(sphere.__file__).read_text()
    assert "<svg" in ORB_SVG and "ara-native-orb" in ORB_SVG

def test_global_starfield_is_unobstructed():
    css=Path("app/assets/styles.css").read_text().split("/* 1.5.9.7")[1]
    assert "background:transparent!important" in css
    assert "animation-timeline:view(block)" in css
    assert "prefers-reduced-motion:reduce" in css
