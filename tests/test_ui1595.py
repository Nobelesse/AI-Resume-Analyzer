from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_platform_navigation_preserves_routes():
    source=(ROOT/'app/main.py').read_text(encoding='utf-8')
    assert '"PLATFORM": project_pages' in source
    assert '"PROJECT": project_pages' not in source
    assert 'url_path="build-roadmap"' in source
    assert 'url_path="architecture"' in source
    assert 'title="Platform Capabilities"' in source
    assert 'title="Privacy & Technology"' in source

def test_hero_feathered_and_background_translucent():
    source=(ROOT/'app/ui/web/intelligence_hero.html').read_text()
    assert 'background:none!important' in source
    assert '.scene::after{content:none!important}' in source
    assert 'rgba(2,5,13,.46)' not in source

def test_scroll_reveal_is_accessible_and_noninteractive():
    css=(ROOT/'app/assets/styles.css').read_text().split('/* Version 1.5.9.6')[1]
    assert 'animation-timeline:view(block)' in css
    assert 'prefers-reduced-motion:reduce' in css
    assert 'stButton' not in css
    assert 'stTextInput' not in css

def test_architecture_no_longer_claims_app_unbuilt():
    page=(ROOT/'app/pages/architecture.py').read_text()
    assert 'There is no live upload' not in page
    assert 'Offline-first tools' in page
