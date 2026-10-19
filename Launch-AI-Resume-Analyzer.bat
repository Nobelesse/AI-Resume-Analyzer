
@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "APP_URL=http://localhost:8501"

if not exist "%PYTHON%" (
    echo ERROR: Python virtual environment not found.
    pause
    exit /b 1
)

REM Check whether port 8501 is already in use.
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"

if %errorlevel%==0 (
    REM Existing server: open its browser page only.
    start "" "%APP_URL%"
    exit /b 0
)

REM Start Streamlit without its automatic browser opening.
start "AI Resume Analyzer Server" /min "%PYTHON%" -m streamlit run app/main.py --server.port 8501 --server.headless true

REM Wait for Streamlit to become available.
set /a attempts=0

:WAIT_FOR_SERVER
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"

if %errorlevel%==0 goto OPEN_BROWSER

set /a attempts+=1

if %attempts% GEQ 30 (
    echo ERROR: Streamlit did not start within 30 seconds.
    pause
    exit /b 1
)

timeout /t 1 /nobreak >nul
goto WAIT_FOR_SERVER

:OPEN_BROWSER
start "" "%APP_URL%"
exit /b 0
