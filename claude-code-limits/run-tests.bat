@echo off
cd /d "%~dp0"
echo Measuring real Claude Code runs inside WSL (3 repeats, about 20-30 minutes)...
wsl.exe -- bash -ic "cd \"$(wslpath '%CD%')\" && python3 -u cc_tests.py"
echo.
echo Finished. You can close this window.
pause
