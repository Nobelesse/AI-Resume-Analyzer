"""UI 1.0 foundation regression tests."""
from pathlib import Path
from app.config import APP_VERSION, MAX_RESUME_BYTES
ROOT = Path(__file__).resolve().parents[1]

def test_ui10_version_and_limit():
    assert APP_VERSION == "1.5.9.4"
    assert MAX_RESUME_BYTES == 2_000_000

def test_home_has_real_navigation_and_no_stale_copy():
    home = (ROOT / "app/pages/home.py").read_text(encoding="utf-8")
    assert "navigation_card(*card)" in home
    assert 'Your potential.' not in home or 'v10-headline' in home
    assert "Engineered for the next phases" not in home
    assert "Phase 3 active" not in home

def test_scoped_cards_and_reduced_motion():
    css = (ROOT / "app/assets/styles.css").read_text(encoding="utf-8")
    assert '.st-key-workspace_cards' in css
    assert '@media(prefers-reduced-motion:reduce)' in css
    assert '.v10-orb' in css

def test_navigation_remains_role_restricted():
    main = (ROOT / "app/main.py").read_text(encoding="utf-8")
    assert 'st.session_state["_ara_registered_pages"]' in main
    assert 'elif current["role"] == "admin"' in main
    assert 'elif current["role"] == "user"' in main
