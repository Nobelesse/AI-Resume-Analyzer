from pathlib import Path
from app.config import APP_VERSION
STYLE_PATH = Path(__file__).resolve().parents[1] / "app/assets/styles.css"


def test_version_and_global_theme():
    assert APP_VERSION == "1.5.9.9.4"
    css = STYLE_PATH.read_text(encoding="utf-8")
    assert '[data-testid="stAppViewContainer"]::before' in css
    assert '[data-testid="stAppViewContainer"]::after' in css
    assert '[data-testid="stSidebar"]::before' in css
    assert "pointer-events:none!important" in css
    assert "prefers-reduced-motion:reduce" in css
    assert "ara-deep-stars" in css and "ara-near-stars" in css

def test_every_role_uses_one_theme_injection():
    main = (Path(__file__).resolve().parents[1] / "app/main.py").read_text(encoding="utf-8")
    assert main.index("inject_theme()") < main.index("current = session_user()")
    assert 'auth_pages.login("user")' in main
    assert 'auth_pages.login("admin")' in main
