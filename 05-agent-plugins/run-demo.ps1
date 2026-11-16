# run-demo.ps1 - loads the dev-helper Agent Plugin into our tiny agent and runs two tasks:
#   1) commit a staged change (uses the plugin's SKILL)   2) ask what was committed (uses the plugin's MCP server)
# Saves run-1-commit.txt and run-2-notes.txt. Your API key is typed here and not saved.
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
$agent = Join-Path $PSScriptRoot "plugin_agent.py"
$plugin = Join-Path $PSScriptRoot "dev-helper"

python -c "import openai, mcp" 2>$null
if ($LASTEXITCODE -ne 0) { python -m pip install --upgrade openai "mcp>=2.3" }

# 0. Start clean: no notes from earlier runs
$data = Join-Path $HOME ".tiny-agent\plugin-data\dev-helper"
if (Test-Path $data) { Remove-Item $data -Recurse -Force }

# 1. A small demo repo with one staged change on a ticket branch (no skills inside it!)
if (Test-Path demo-repo) { Remove-Item demo-repo -Recurse -Force }
New-Item -ItemType Directory demo-repo | Out-Null
Set-Location demo-repo
git init -q -b main
git config user.name "Demo"; git config user.email "demo@example.com"
@'
def cart_total(items, discount=0.0):
    """Total of (price, qty) items after a discount (0.10 = 10%)."""
    subtotal = sum(price * qty for price, qty in items)
    return round(subtotal * (1 - discount), 2)
'@ | Set-Content -Encoding ascii cart.py
git add . ; git commit -q -m "Initial cart"
git checkout -q -b feature/PAY-142-discount-cap
(Get-Content cart.py) -replace '^    subtotal = sum', "    discount = min(discount, 0.5)  # never more than 50% off`n    subtotal = sum" | Set-Content -Encoding ascii cart.py
git add cart.py

# 2. Key (hidden while you paste)
$sec = Read-Host "Paste your Groq API key and press Enter" -AsSecureString
$env:API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
try {
    Write-Host "`n=== Run 1: commit (type y when it asks to run a command) ===`n" -ForegroundColor Cyan
    python -u $agent $plugin "Commit my staged changes, then save a note about what you committed." 2>&1 | ForEach-Object { "$_" } | Tee-Object -Variable lines1
    $msg = git log -1 --format=%B
    ($lines1 + "", "=== resulting commit message ===") + $msg | Set-Content -Encoding utf8 ..\run-1-commit.txt

    Write-Host "`n=== Run 2: a NEW session asks the notes server ===`n" -ForegroundColor Cyan
    python -u $agent $plugin "What did I commit for PAY-142? Check my notes." 2>&1 | ForEach-Object { "$_" } | Tee-Object -Variable lines2
    $lines2 | Set-Content -Encoding utf8 ..\run-2-notes.txt
} finally {
    Remove-Item Env:API_KEY -ErrorAction SilentlyContinue
    Set-Location $PSScriptRoot
}
Write-Host "`nCommit message:" -ForegroundColor Green; $msg
Write-Host "`nNotes file (in PLUGIN_DATA): $data\notes.md" -ForegroundColor Green
if (Test-Path "$data\notes.md") { Get-Content "$data\notes.md" | Tee-Object -FilePath notes-after-run.txt }
Write-Host "`nDone. Logs saved - tell Claude 'done'." -ForegroundColor Green
