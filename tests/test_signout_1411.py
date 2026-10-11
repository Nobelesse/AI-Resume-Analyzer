from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_signout_full_sidebar_area_not_narrow_columns():
    source = (ROOT / "app/main.py").read_text(encoding="utf-8")
    assert 'with st.container(key="sidebar_signout_area"):' in source
    assert 'st.button("Sign out", key="sidebar_signout", use_container_width=False)' in source
    assert '_, signout_col, _ = st.columns([1, 1, 1])' not in source
    assert 'logout()' in source

def test_signout_style_avoids_label_truncation():
    css = (ROOT / "app/assets/styles.css").read_text(encoding="utf-8")
    assert '.st-key-sidebar_signout_area' in css
    assert 'min-width: 6.6rem !important' in css
    assert 'text-overflow: clip !important' in css
    assert 'justify-content: center !important' in css
