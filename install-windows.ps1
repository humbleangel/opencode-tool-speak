# Speak tool - automatic Windows installer.
# Run this line in PowerShell and follow what it says:
# powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/humbleangel/opencode-tool-speak/main/install-windows.ps1 | iex"
$ErrorActionPreference = "Stop"
$Repo = "humbleangel/opencode-tool-speak"
$Files = @("speak.py", "speak.ts", "speak.json")
$ToolsDir = Join-Path $HOME ".config\opencode\tools"

Write-Host ""
Write-Host "=== Speak tool installer ==="
Write-Host "This will check Python, install the voice library and a sound player,"
Write-Host "then copy the 3 tool files into your OpenCode tools folder."
Write-Host ""

function Refresh-Path {
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "Python not found. Trying to install it automatically..."
  try {
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    Refresh-Path
  } catch {
    Write-Host "Automatic install did not work."
    Write-Host "Please install Python from https://www.python.org/downloads/ (tick 'Add python.exe to PATH'),"
    Write-Host "then run this installer again."
    exit 1
  }
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "Python was installed, but this window cannot see it yet."
  Write-Host "Close this window, open a new one, and run the installer again."
  exit 1
}
python --version

Write-Host "Installing the voice library (one time)..."
python -m pip install --upgrade edge-tts

if (-not (Get-Command ffplay -ErrorAction SilentlyContinue)) {
  Write-Host "No sound player found. Trying to install ffmpeg (it includes ffplay)..."
  try {
    winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    Refresh-Path
  } catch {
    Write-Host "Automatic install did not work."
    Write-Host "Please install ffmpeg from https://ffmpeg.org/download.html or VLC from https://www.videolan.org/vlc/,"
    Write-Host "then run this installer again."
    exit 1
  }
}

Write-Host "Copying the tool files..."
New-Item -ItemType Directory -Path $ToolsDir -Force | Out-Null
foreach ($f in $Files) {
  Invoke-WebRequest -Uri "https://raw.githubusercontent.com/$Repo/main/$f" -OutFile (Join-Path $ToolsDir $f)
  Write-Host "  installed $f"
}

Write-Host ""
Write-Host "Done! Now restart OpenCode."
Write-Host "On its very first message, the agent will speak to you out loud."
