"""Custom first-party interactive intelligence sphere component."""
from pathlib import Path

SCENE_PATH = Path(__file__).resolve().parent / "web" / "intelligence_sphere.html"


def render_intelligence_sphere(height: int = 360) -> None:
    """Render a lightweight interactive sphere scene in an isolated iframe."""
    if not 220 <= height <= 900:
        raise ValueError("Invalid sphere height")
    import streamlit.components.v1 as components
    html = SCENE_PATH.read_text(encoding="utf-8")
    components.html(html, height=height, scrolling=False)
