from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_compact_centered_auth():
    auth=(ROOT/'app/pages/auth_pages.py').read_text(encoding='utf-8')
    main=(ROOT/'app/main.py').read_text(encoding='utf-8')
    style=(ROOT/'app/assets/styles.css').read_text(encoding='utf-8')
    assert 'button_center' in auth
    assert 'with st.container(key="sidebar_signout_area"):' in main
    assert 'UI 1.3.1' in style
