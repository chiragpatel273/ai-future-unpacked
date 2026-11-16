# run-demo.ps1 - our tiny agent with and without subagents. The same investigation task, twice,
# each time in a fresh copy of the demo project:
#   1) no subagents           -> the main agent reads everything itself
#   2) with the explorer      -> the explorer reads, the main agent only gets its report
# Watch "context: N tokens" on each turn. Saves run-1-no-subagent.txt and run-2-with-subagent.txt.
# Your API key is typed here and not saved.
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$agent = Join-Path $PSScriptRoot "subagents_agent.py"
$task = "Customers reported three problems. 1) Coupon SAVE10 gives no discount at all when the cart has a sale item. 2) A US order of exactly 50.00 dollars still pays shipping, but we promise free shipping from 50 dollars. 3) The order email for 3 mugs shows 12.00 on the mug line, but 3 mugs cost 36.00. For each problem, find the cause: the file, the function and the line. If you have helper agents, use one per problem. Do not change any code yet. Reply with a short report."

python -c "import openai" 2>$null
if ($LASTEXITCODE -ne 0) { python -m pip install --upgrade openai }

# A fresh copy of the demo project (the shop, its tests, .agent/agents/explorer.md)
function New-DemoRepo($withSubagent) {
    Set-Location $PSScriptRoot
    if (Test-Path demo-repo) { Remove-Item demo-repo -Recurse -Force }
    Copy-Item demo demo-repo -Recurse -Force
    Set-Location demo-repo
    if (-not $withSubagent) { Remove-Item .agent -Recurse -Force }
}

function Save-Run($lines, $file) {
    @($lines) | Set-Content -Encoding utf8 "..\$file"
}

# Key (hidden while you paste)
$sec = Read-Host "Paste your Groq API key and press Enter" -AsSecureString
$env:API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
$m = Read-Host "Model (press Enter for openai/gpt-oss-120b)"
if ($m) { $env:MODEL = $m }
try {
    New-DemoRepo $false
    Write-Host "`n=== Run 1: no subagents ===`n" -ForegroundColor Cyan
    python -u $agent $task 2>&1 | ForEach-Object { "$_" } | Tee-Object -Variable lines1
    Save-Run $lines1 "run-1-no-subagent.txt"

    New-DemoRepo $true                            # run 2 starts from the same fresh project
    Write-Host "`n=== Run 2: with the explorer subagent ===`n" -ForegroundColor Cyan
    python -u $agent $task 2>&1 | ForEach-Object { "$_" } | Tee-Object -Variable lines2
    Save-Run $lines2 "run-2-with-subagent.txt"
} finally {
    Remove-Item Env:API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:MODEL -ErrorAction SilentlyContinue
    Set-Location $PSScriptRoot
}
Write-Host "`nDone. Logs saved: run-1-no-subagent.txt, run-2-with-subagent.txt" -ForegroundColor Green
