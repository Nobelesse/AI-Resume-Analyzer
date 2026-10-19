from pathlib import Path
from app.config import APP_VERSION
ROOT=Path(__file__).resolve().parents[1]

def test_true_seamless_hero_has_one_global_sky():
    html=(ROOT/'app/ui/web/intelligence_hero.html').read_text()
    assert 'background:none!important' in html
    assert '.scene::after{content:none!important}' in html
    frame=html.split('function frame(')[1].split('scene.addEventListener')[0]
    assert 'drawBackgroundGlow(t);' not in frame
    assert 'drawStars(t);' not in frame
    assert 'drawSphere(t);' in frame and 'drawRings(t);' in frame

def test_scroll_reveal_is_read_only_and_accessible():
    css=(ROOT/'app/assets/styles.css').read_text().split('/* Version 1.5.9.6')[1]
    assert 'animation-timeline:view(block)' in css
    assert 'prefers-reduced-motion:reduce' in css
    assert 'stTextInput' not in css and 'stButton' not in css
    assert 'background-image:none!important' in css
    assert APP_VERSION == '1.5.9.9.8'
