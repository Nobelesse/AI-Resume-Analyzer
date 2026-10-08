"""Isolated first-party animation rendered within a Streamlit HTML component iframe."""
from pathlib import Path
import streamlit.components.v1 as components
SCENE_PATH = Path(__file__).resolve().parent / "web" / "motion.html"

def render_motion_scene(height: int = 360) -> None:
    if not 200 <= height <= 1000:
        raise ValueError("Invalid component height")
    components.html(SCENE_PATH.read_text(encoding="utf-8"), height=height, scrolling=False)
