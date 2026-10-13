# Version 1.4.2.5 — Windows VS Code and GitHub Commands

## Extract and replace project
```powershell
$zip = "$HOME\Downloads\AI-Resume-Analyzer-Version-1.4.2.5-True-Continuous-Orbit.zip"
$extract = "C:\Projects\Version-1.4.2.5-New"
$source = "$extract\AI-Resume-Analyzer-1.4.2.5"
$destination = "C:\Projects\AI-Resume-Analyzer"
$backup = "C:\Projects\AI-Resume-Analyzer-Backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

Expand-Archive -LiteralPath $zip -DestinationPath $extract
Copy-Item $destination $backup -Recurse
robocopy $source $destination /E /R:2 /W:1 /XD .git .venv data __pycache__ .pytest_cache /XF .env *.db *.sqlite *.sqlite3
```

## Run in VS Code terminal
```powershell
cd "C:\Projects\AI-Resume-Analyzer"
.\.venv\Scripts\activate
python -m pytest -q
streamlit run app\main.py
```

## GitHub
```powershell
cd "C:\Projects\AI-Resume-Analyzer"
git status
git add .
git commit -m "Version 1.4.2.5 true continuous orbit fix"
git push origin main
```
