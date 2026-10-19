@echo off
cd /d "E:\Projects\AI-Resume-Analyzer"
if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found.
    pause
    exit /b 1
)
start "AI Resume Analyzer" ".venv\Scripts\python.exe" -m streamlit run app/main.py --server.headless true
timeout /t 5 /nobreak >nul
start "" "http://localhost:8501"
