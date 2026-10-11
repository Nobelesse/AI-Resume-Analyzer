"""Milestone 2 presentation regression tests; no private data needed."""
from pathlib import Path
import sys
import types
from app.ui.workspace import page_header, section_heading, step_label

ROOT = Path(__file__).resolve().parents[1]


def test_user_pages_integrate_workspace_components():
    for name in ("auth_pages", "resume_pages", "analysis_pages", "job_pages"):
        source = (ROOT / "app" / "pages" / f"{name}.py").read_text(encoding="utf-8")
        assert "page_header(" in source


def test_html_escaping_for_reusable_headers(monkeypatch):
    rendered=[]
    monkeypatch.setitem(sys.modules, "streamlit", types.SimpleNamespace(markdown=lambda text, **kwargs: rendered.append(text)))
    page_header("<script>", "<b>Title</b>", "Text & copy")
    assert "<script>" not in rendered[0]
    assert "&lt;script&gt;" in rendered[0]
    assert "&lt;b&gt;" in rendered[0]
    assert "Text &amp; copy" in rendered[0]
    step_label("01", "Upload")
    section_heading("Result")


def test_no_auth_bypass():
    for name in ("resume_pages", "analysis_pages", "job_pages"):
        source = (ROOT / "app" / "pages" / f"{name}.py").read_text(encoding="utf-8")
        assert "require_role" in source


def test_scope_of_card_css():
    source=(ROOT / 'app/assets/styles.css').read_text(encoding='utf-8')
    assert '.st-key-workspace_cards' in source
    assert '.uim2-header' in source
