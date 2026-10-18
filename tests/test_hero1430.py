from pathlib import Path
from app.config import APP_VERSION

def test_1430_scale_and_clearance():
    hero = Path('app/ui/web/intelligence_hero.html').read_text()
    assert APP_VERSION == '1.5.9.9.1'
    assert 'cx = w * (mobile ? 0.56 : 0.755);' in hero
    assert 'const orbitBound = mobile ? 2.08 : 1.90;' in hero
    assert 'h * (mobile ? 0.270 : 0.430)' in hero
    assert '{r:1.278' in hero and '{r:1.398' in hero
    assert 'ctx.closePath();' in hero
