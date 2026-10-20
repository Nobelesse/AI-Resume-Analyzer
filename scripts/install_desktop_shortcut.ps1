# Create or update the current user's one-click presentation shortcut.
$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $project "Launch-AI-Resume-Analyzer.bat"
$icon = Join-Path $project "app\assets\app_icon.ico"
if (-not (Test-Path $launcher) -or -not (Test-Path $icon)) { throw "Launcher or icon missing." }
$desktop = [Environment]::GetFolderPath("Desktop")
$path = Join-Path $desktop "AI Resume Analyzer.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($path)
$shortcut.TargetPath = $launcher
$shortcut.WorkingDirectory = $project
$shortcut.IconLocation = "$icon,0"
$shortcut.Description = "Open AI Resume Analyzer"
$shortcut.Save()
Write-Host "Desktop shortcut updated: $path" -ForegroundColor Green

# Separate stop shortcut; closing a Streamlit browser tab does not stop its server.
$stop = $shell.CreateShortcut((Join-Path $desktop "Stop AI Resume Analyzer.lnk"))
$stop.TargetPath = (Join-Path $project "Stop-AI-Resume-Analyzer.bat")
$stop.WorkingDirectory = $project
$stopIcon = Join-Path $project "app\assets\stop_app_icon.ico"
if (-not (Test-Path $stopIcon)) { throw "Stop shortcut icon missing." }
$stop.IconLocation = "$stopIcon,0"
$stop.Description = "Stop this project's server and launcher-managed Ollama"
$stop.Save()
