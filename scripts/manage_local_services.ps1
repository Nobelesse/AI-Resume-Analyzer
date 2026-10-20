param([ValidateSet('start','stop')][string]$Action='start')
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$stateDir = Join-Path $env:LOCALAPPDATA 'AI-Resume-Analyzer'
$stateFile = Join-Path $stateDir 'launcher-processes.json'
$python = Join-Path $project '.venv\Scripts\python.exe'
$health = 'http://127.0.0.1:8501/_stcore/health'
$ollamaUrl = 'http://127.0.0.1:11434/api/tags'
New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
function Ready([string]$url) { try { $null=Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2; return $true } catch { return $false } }
function Owns([int]$processId, [string]$expected) {
  if ($processId -le 0) { return $false }
  $p = Get-CimInstance Win32_Process -Filter "ProcessId=$processId" -ErrorAction SilentlyContinue
  return [bool]($p -and $p.CommandLine -and $p.CommandLine.Contains($expected))
}
function ReadState { if(Test-Path $stateFile) {try{return Get-Content $stateFile -Raw | ConvertFrom-Json}catch{}}; return $null }
if($Action -eq 'stop') {
  $saved=ReadState
  if($saved) {
    if($saved.streamlit_pid -and (Owns ([int]$saved.streamlit_pid) 'streamlit')) {Stop-Process -Id ([int]$saved.streamlit_pid) -Force -ErrorAction SilentlyContinue}
    if($saved.ollama_pid -and (Owns ([int]$saved.ollama_pid) 'ollama')) {Stop-Process -Id ([int]$saved.ollama_pid) -Force -ErrorAction SilentlyContinue}
    Remove-Item $stateFile -Force -ErrorAction SilentlyContinue
  }
  Write-Host 'Stopped launcher-managed application services. Externally running Ollama was not touched.'
  exit 0
}
if(!(Test-Path $python)) {throw 'Virtual environment not found. Install the project before launching.'}
$saved=ReadState
$streamPid=0
$ollamaPid=0
if($saved) {
  if($saved.streamlit_pid -and (Owns ([int]$saved.streamlit_pid) 'streamlit')) {$streamPid=[int]$saved.streamlit_pid}
  if($saved.ollama_pid -and (Owns ([int]$saved.ollama_pid) 'ollama')) {$ollamaPid=[int]$saved.ollama_pid}
}
if(!(Ready $ollamaUrl)) {
  $ollamaCmd=Get-Command 'ollama.exe' -ErrorAction SilentlyContinue
  if($ollamaCmd) {
    try { $p=Start-Process -FilePath $ollamaCmd.Source -ArgumentList 'serve' -PassThru -WindowStyle Hidden; $ollamaPid=$p.Id }
    catch {Write-Warning "Ollama could not be started: $_"}
  } else {Write-Warning 'Ollama is not on PATH; catalog-based matching still works.'}
}
if(!(Ready $health)) {
  $portInUse=Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
  if($portInUse) {Write-Warning 'Port 8501 is in use by another process; not starting a second server.'}
  else {
    $arguments='-m streamlit run app/main.py --server.port 8501 --server.headless true'
    $p=Start-Process -FilePath $python -ArgumentList $arguments -WorkingDirectory $project -PassThru -WindowStyle Minimized
    $streamPid=$p.Id
  }
}
@{streamlit_pid=$streamPid;ollama_pid=$ollamaPid;project=$project} | ConvertTo-Json | Set-Content -Path $stateFile -Encoding UTF8
