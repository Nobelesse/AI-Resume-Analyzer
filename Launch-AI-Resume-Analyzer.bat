
@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "URL=http://localhost:8501"

if not exist "%PYTHON%" (
    echo ERROR: Python environment not found.
    pause
    exit /b 1
)

REM Check whether Streamlit is already running.
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"

if not errorlevel 1 (
    start "" "%URL%"
    exit /b 0
)

REM Start Streamlit without automatic browser opening.
start "AI Resume Analyzer Server" /min "%PYTHON%" -m streamlit run app/main.py --server.port 8501 --server.headless true

REM Wait until the server is ready.
set /a attempts=0

:WAIT
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"

if not errorlevel 1 goto OPEN_BROWSER

set /a attempts+=1

if %attempts% GEQ 30 (
    echo ERROR: Streamlit did not start within 30 seconds.
    pause
    exit /b 1
)

timeout /t 1 /nobreak >nul
goto WAIT

:OPEN_BROWSER
start "" "%URL%"
exit /b 0
