from pathlib import Path
from app.services.local_status import ollama_status
ROOT=Path(__file__).resolve().parents[1]
def test_launcher_uses_managed_processes():
    bat=(ROOT/'Launch-AI-Resume-Analyzer.bat').read_text()
    assert 'manage_local_services.ps1' in bat
    assert 'launcher_loading.html' in bat
    manager=(ROOT/'scripts/manage_local_services.ps1').read_text()
    assert 'streamlit_pid' in manager and 'ollama_pid' in manager
    assert 'Owns' in manager and "Action -eq 'stop'" in manager
def test_ollama_offline_is_safe(monkeypatch):
    import urllib.request
    def fail(*a, **kw): raise OSError('offline')
    monkeypatch.setattr(urllib.request,'urlopen',fail)
    assert ollama_status()=={'connected':False,'models':[]}
