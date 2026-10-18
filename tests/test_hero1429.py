from pathlib import Path
from app.config import APP_VERSION

HTML = Path("app/ui/web/intelligence_hero.html")

def test_version_1429():
    assert APP_VERSION == "1.5.9.6"

def test_new_scale_preserves_radial_gap_at_eight_percent_grow():
    html=HTML.read_text()
    assert "cx = w * (mobile ? 0.56 : 0.755);" in html
    assert "const orbitBound = mobile ? 2.08 : 1.90;" in html
    assert "h * (mobile ? 0.270 : 0.430)" in html
    assert "{r:1.278" in html
    assert "{r:1.398" in html
    # New scale targets about 8% larger globe and ring geometry.
    for old,new in ((1.30,1.278),(1.43,1.398)):
        assert abs((new-1)*1.08-(old-1)) < 0.001

def test_optimized_orbit_and_abyss_preserved():
    html=HTML.read_text()
    assert "ctx.closePath();" in html
    assert "drawRings(t);" in html
    assert "rgba(220,190,122,.84)" in html
