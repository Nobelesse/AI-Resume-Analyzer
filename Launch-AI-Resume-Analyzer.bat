@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo ERROR: Virtual environment missing.
 pause
 exit /b 1
)
set "SPLASH=%~dp0app\assets\launcher_loading.html"
start "" "%SPLASH%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\manage_local_services.ps1" -Action start
if errorlevel 1 (echo Startup failed. & pause)
