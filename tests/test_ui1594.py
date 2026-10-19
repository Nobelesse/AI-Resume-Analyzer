from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_borderless_global_style():
    css = (ROOT / "app/assets/styles.css").read_text(encoding="utf-8")
    tail = css.split("/* Version 1.5.9.4")[1]
    for selector in (".st-key-auth_shell", ".feature-card", ".uim2-header", ".v10-hero", '[data-testid="stMetric"]'):
        assert selector in tail
    assert 'background:transparent!important' in tail
    assert 'focus-visible' in tail
    assert 'prefers-reduced-motion' in tail

def test_hero_scene_is_translucent():
    source = (ROOT / "app/ui/web/intelligence_hero.html").read_text(encoding="utf-8")
    assert '.scene::after{content:none!important}' in source

def test_version():
    from app.config import APP_VERSION
    assert APP_VERSION == "1.5.9.9.5"

def test_scroll_depth_is_native_and_accessible():
    css = (ROOT / "app/assets/styles.css").read_text(encoding="utf-8")
    assert '@keyframes ara-scroll-depth' in css
    assert 'animation-timeline:view(block)' in css
    assert '@supports (animation-timeline:view())' in css
    assert 'prefers-reduced-motion:reduce' in css
    scroll_section = css.split('/* Scroll-linked depth:')[1]
    assert '[data-testid="stTextInput"]' not in scroll_section
    assert '[data-testid="stDataFrame"]' not in scroll_section
