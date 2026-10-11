from pathlib import Path

def test_moving_orb_and_reduced_motion():
    css = (Path(__file__).resolve().parents[1]/"app/assets/styles.css").read_text(encoding="utf-8")
    for term in ("orb-bob-111", "orb-sheen-111", "orb-star-breathe-111", "prefers-reduced-motion:reduce"):
        assert term in css
