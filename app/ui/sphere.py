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


HERO_PATH = Path(__file__).resolve().parent / "web" / "intelligence_hero.html"

def render_intelligence_hero(height: int = 510) -> None:
    """Render text directly over a canvas-powered full-width hero background."""
    if not 320 <= height <= 900:
        raise ValueError("Invalid hero height")
    from app.ui.native_hero import render_native_hero
    render_native_hero(height=height)
