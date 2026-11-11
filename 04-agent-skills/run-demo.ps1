# run-demo.ps1 - runs skills_agent twice on the same staged change: first WITHOUT skills, then WITH.
# Saves run-without-skills.txt and run-with-skills.txt. Your API key is typed here and not saved.
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
$agent = Join-Path $PSScriptRoot "skills_agent.py"

python -c "import openai" 2>$null
if ($LASTEXITCODE -ne 0) { python -m pip install --upgrade openai }

# 1. A small demo repo with one staged change on a ticket branch
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
New-Item -ItemType Directory .agents | Out-Null
Copy-Item -Recurse ..\skills .agents\skills
git add . ; git commit -q -m "Initial cart and team skills"
git checkout -q -b feature/PAY-142-discount-cap
(Get-Content cart.py) -replace '^    subtotal = sum', "    discount = min(discount, 0.5)  # never more than 50% off`n    subtotal = sum" | Set-Content -Encoding ascii cart.py
git add cart.py

# 2. Key (hidden while you paste)
$sec = Read-Host "Paste your Groq API key and press Enter" -AsSecureString
$env:API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
$task = "Commit my staged changes."
try {
    Write-Host "`n=== Run 1: WITHOUT skills (type y when it asks to run a command) ===`n" -ForegroundColor Cyan
    $env:NO_SKILLS = "1"
    python -u $agent $task 2>&1 | ForEach-Object { "$_" } | Tee-Object -Variable lines1
    Remove-Item Env:NO_SKILLS
    $msg1 = git log -1 --format=%B
    ($lines1 + "", "=== resulting commit message ===") + $msg1 | Set-Content -Encoding utf8 ..\run-without-skills.txt
    git reset -q --soft HEAD~1   # undo that commit, keep the change staged

    Write-Host "`n=== Run 2: WITH the commit-message skill ===`n" -ForegroundColor Cyan
    python -u $agent $task 2>&1 | ForEach-Object { "$_" } | Tee-Object -Variable lines2
    $msg2 = git log -1 --format=%B
    ($lines2 + "", "=== resulting commit message ===") + $msg2 | Set-Content -Encoding utf8 ..\run-with-skills.txt
} finally {
    Remove-Item Env:API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:NO_SKILLS -ErrorAction SilentlyContinue
    Set-Location $PSScriptRoot
}
Write-Host "`nWithout skills:" -ForegroundColor Yellow; $msg1
Write-Host "`nWith skills:" -ForegroundColor Green; $msg2
Write-Host "`nDone. Logs saved - tell Claude 'done'." -ForegroundColor Green
