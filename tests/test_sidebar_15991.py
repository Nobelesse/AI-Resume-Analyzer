from pathlib import Path


def test_sidebar_is_scrollable():
    css = (Path(__file__).resolve().parents[1] / "app/assets/styles.css").read_text()
    assert '[data-testid="stSidebarContent"]' in css
    assert 'overflow-y: auto !important' in css
    assert 'overscroll-behavior-y: contain' in css
    assert 'overflow:hidden;}\n[data-testid="stSidebar"]::before' not in css


def test_sidebar_routes_preserved():
    nav = (Path(__file__).resolve().parents[1] / "app/ui/navigation.py").read_text()
    assert '"job-match": "Job Match Studio"' in nav
    assert '"career-finder": "AI Career Finder"' in nav
