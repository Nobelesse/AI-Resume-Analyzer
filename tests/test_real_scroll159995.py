"""Regression checks for the main-document scroll engine and safe UI targets."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_main_document_integration():
    source = (ROOT / 'app/main.py').read_text(encoding='utf8')
    hook = (ROOT / 'app/ui/scroll_engine.py').read_text(encoding='utf8')
    assert 'inject_scroll_engine()' in source
    assert 'st.html(' in hook and 'unsafe_allow_javascript=True' in hook
    assert 'components.html' not in hook


def test_scroll_engine_tracks_actual_scroll_and_skips_interactive_controls():
    js = (ROOT / 'app/ui/web/scroll_engine.js').read_text(encoding='utf8')
    assert "addEventListener('scroll', schedule" in js
    assert 'getBoundingClientRect()' in js
    assert 'requestAnimationFrame(render)' in js
    assert 'MutationObserver' in js
    assert 'prefers-reduced-motion: reduce' in js
    assert '[data-testid="stSidebar"]' in js
    assert 'button, [role="button"], form' in js
    assert 'fetch(' not in js and 'XMLHttpRequest' not in js


def test_current_version_and_css_override():
    from app.config import APP_VERSION
    assert APP_VERSION == '1.5.9.9.5'
    css = (ROOT / 'app/assets/styles.css').read_text(encoding='utf8')
    assert 'v1.5.9.9.5 — Real Spatial Scroll Engine' in css
    assert 'transform: var(--ara-scroll-transform, none) !important;' in css
    assert '(prefers-reduced-motion: reduce)' in css
