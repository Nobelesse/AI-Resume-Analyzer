"""Ensure the stop shortcut keeps an independent icon."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_stop_shortcut_uses_dedicated_ico():
    code = (ROOT / "scripts/install_desktop_shortcut.ps1").read_text(encoding="utf-8")
    assert 'app\\assets\\stop_app_icon.ico' in code
    assert '$stop.IconLocation = "$stopIcon,0"' in code
    assert '$shortcut.IconLocation = "$icon,0"' in code
    assert (ROOT / "app/assets/stop_app_icon.ico").read_bytes()[:4] == b"\x00\x00\x01\x00"
