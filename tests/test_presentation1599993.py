from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def test_professional_sidebar_and_workflow():
    main = (BASE / "app/main.py").read_text(encoding="utf-8")
    guide = (BASE / "app/pages/design_lab.py").read_text(encoding="utf-8")
    assert 'title="Getting Started"' in main
    assert 'url_path="interaction-studio"' in main  # old links remain valid
    assert "Experience Center" not in main
    assert "intelligence_sphere" not in guide
    assert "Job Match Studio" in guide and "AI Career Finder" in guide


def test_overview_workspace_has_real_heading():
    home = (BASE / "app/pages/home.py").read_text(encoding="utf-8")
    assert home.count('"Your Workspace"') == 2
    assert 'section_heading("YOUR WORKSPACE"' not in home
