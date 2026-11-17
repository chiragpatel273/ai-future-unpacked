# run-demo.ps1 - our tiny agent with Code Mode off, then on. The same task, twice,
# each time in a fresh copy of the demo docs:
#   1) Code Mode off  -> the model asks for one tool call at a time and reads every result
#   2) Code Mode on   -> the model writes one Python script that calls the tools and prints the answer
# Watch "context: N tokens" on each turn. Saves run-1-normal.txt and run-2-code-mode.txt.
# Your API key is typed here and not saved.
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$agent = Join-Path $PSScriptRoot "code_mode_agent.py"
$task = "Read every Markdown file in this project and list the links that point to local files that do not exist. For each one, give the file it is in and the link. Do not change any files."

python -c "import openai" 2>$null
if ($LASTEXITCODE -ne 0) { python -m pip install --upgrade openai }

function New-DemoRepo {                       # a fresh copy of the demo docs
    Set-Location $PSScriptRoot
    if (Test-Path demo-repo) { Remove-Item demo-repo -Recurse -Force }
    Copy-Item demo demo-repo -Recurse -Force
    Set-Location demo-repo
}

function Save-Run($lines, $file) {
    @($lines) | Set-Content -Encoding utf8 "..\$file"
}

$sec = Read-Host "Paste your Groq API key and press Enter" -AsSecureString
$env:API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
$m = Read-Host "Model (press Enter for openai/gpt-oss-120b)"
if ($m) { $env:MODEL = $m }
try {
    New-DemoRepo
    $env:CODE_MODE = "0"
    Write-Host "`n=== Run 1: Code Mode off ===`n" -ForegroundColor Cyan
    python -u $agent $task 2>&1 | ForEach-Object { "$_" } | Tee-Object -Variable lines1
    Save-Run $lines1 "run-1-normal.txt"

    New-DemoRepo                                # run 2 starts from the same fresh docs
    $env:CODE_MODE = "1"
    Write-Host "`n=== Run 2: Code Mode on ===`n" -ForegroundColor Cyan
    python -u $agent $task 2>&1 | ForEach-Object { "$_" } | Tee-Object -Variable lines2
    Save-Run $lines2 "run-2-code-mode.txt"
} finally {
    Remove-Item Env:API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:MODEL -ErrorAction SilentlyContinue
    Remove-Item Env:CODE_MODE -ErrorAction SilentlyContinue
    Set-Location $PSScriptRoot
}
Write-Host "`nDone. Logs saved: run-1-normal.txt, run-2-code-mode.txt" -ForegroundColor Green
