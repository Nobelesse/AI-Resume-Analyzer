from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_launcher_opens_splash_without_fixed_wait():
    s=(ROOT/'Launch-AI-Resume-Analyzer.bat').read_text(encoding='ascii').lower()
    assert 'launcher_loading.html' in s and 'start "" "%splash%"' in s
    assert 'timeout /t 5' not in s and '--server.headless true' in s

def test_launcher_uses_brand_icon_and_safe_shortcut():
    s=(ROOT/'scripts/install_desktop_shortcut.ps1').read_text(encoding='utf-8')
    assert 'app_icon.ico' in s and 'getfolderpath("desktop")' in s.lower()
    assert (ROOT/'app/assets/app_icon.ico').read_bytes()[:4]==b'\x00\x00\x01\x00'

def test_splash_checks_server_and_redirects():
    s=(ROOT/'app/assets/launcher_loading.html').read_text(encoding='utf-8')
    assert '_stcore/health' in s and 'window.location.replace(url)' in s
