from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_guest_info_has_separate_spacing_element():
    source = (ROOT / "app/pages/home.py").read_text(encoding="utf-8")
    gap = 'guest-card-info-gap'
    banner = 'st.info("Open User Login or Admin Login in the sidebar to get started.")'
    assert source.index(gap) < source.index(banner)
    assert source.count(gap) == 1

def test_guest_info_gap_style_exists():
    css = (ROOT / "app/assets/styles.css").read_text(encoding="utf-8")
    assert '.guest-card-info-gap { height: 20px; }' in css
