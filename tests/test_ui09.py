
"""Regression tests for AI-Resume-Analyzer UI Upgrade 0.9.0."""

from pathlib import Path
import ast

from app.config import APP_VERSION, MAX_RESUME_BYTES


ROOT = Path(__file__).resolve().parents[1]


def constants(file, names):
    source = (ROOT / file).read_text(encoding="utf-8")
    tree = ast.parse(source)

    return {
        target.id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id in names
    }


def test_release_and_upload_limit():
    assert APP_VERSION == "0.9.0"
    assert MAX_RESUME_BYTES == 2_000_000


def test_all_roadmap_milestones_delivered():
    phases = constants(
        "app/pages/roadmap.py",
        {"PHASES"},
    )["PHASES"]

    assert len(phases) == 8
    assert all(len(phase) == 3 for phase in phases)


def test_functional_workspace_routes():
    cards = constants(
        "app/pages/home.py",
        {"USER_CARDS", "ADMIN_CARDS"},
    )

    routes = constants(
        "app/ui/navigation.py",
        {"ROUTE_LABELS"},
    )["ROUTE_LABELS"]

    assert len(cards["USER_CARDS"]) >= 6
    assert len(cards["ADMIN_CARDS"]) >= 3

    assert all(
        card[2] in routes
        for card in cards["USER_CARDS"] + cards["ADMIN_CARDS"]
    )


def test_no_stale_home_copy():
    text = (ROOT / "app/pages/home.py").read_text(
        encoding="utf-8"
    )

    assert "Phase 3 active" not in text
    assert "Engineered for the next phases" not in text
