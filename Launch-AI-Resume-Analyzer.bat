@echo off
setlocal
cd /d "%~dp0"
set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "SPLASH=%~dp0app\assets\launcher_loading.html"
if not exist "%PYTHON%" (
  echo ERROR: Python environment not found in project folder.
  pause
  exit /b 1
)
if not exist "%SPLASH%" (
  echo ERROR: launcher page is missing.
  pause
  exit /b 1
)
REM Windows socket check: do not start a second server if the port is already in use.
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 (
  start "AI Resume Analyzer Server" /min "%PYTHON%" -m streamlit run app/main.py --server.port 8501 --server.headless true
)
REM Immediately open a single loading page. It redirects when Streamlit is ready.
start "" "%SPLASH%"
exit /b 0
