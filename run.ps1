$ErrorActionPreference = "Stop"
$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  Write-Error "Python virtual environment not found. Run: py -3.11 -m venv .venv"
  exit 1
}
Set-Location $PSScriptRoot
& $Python -m streamlit run app/main.py
