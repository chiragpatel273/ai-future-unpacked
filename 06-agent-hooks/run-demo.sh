#!/usr/bin/env bash
# run-demo.sh - Linux / WSL / macOS version of run-demo.bat.
# Our tiny agent with hooks. Two tasks in a fresh copy of the demo project:
#   1) ask for a secret from .env   -> the PreToolUse hook blocks it
#   2) cap discounts at 50%         -> the Stop hook runs the tests before the agent may finish
# Saves run-1-guard.txt, run-2-stop.txt and the tool logs. Your API key is typed here and not saved.
set -u
cd "$(dirname "$0")"
HERE="$PWD"
AGENT="$HERE/hooks_agent.py"

# 0. Python package in a local virtual environment (.venv)
#    (inside the venv, "python" in hooks.json points to the venv's Python)
if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv || { echo "Install venv first:  sudo apt install python3-venv"; exit 1; }
fi
source .venv/bin/activate
python -c "import openai" 2>/dev/null || pip install -q --upgrade openai

# 1. A fresh copy of the demo project (cart.py, tests, a fake .env, .agent/hooks) as a git repo
new_demo_repo() {
    cd "$HERE" && rm -rf demo-repo && cp -r demo demo-repo && cd demo-repo
    echo "DISCOUNT_API_KEY=demo-key-not-real-1234" > .env   # a FAKE secret
    printf '.env\n.agent/tool-log.txt\n__pycache__/\n' > .gitignore
    git init -q -b main && git config user.name "Demo" && git config user.email "demo@example.com"
    git add . && git commit -q -m "Cart with failing tests"
}

# 2. Key (hidden while you paste)
read -rsp "Paste your Groq API key and press Enter: " API_KEY; echo
export API_KEY
export PYTHONUNBUFFERED=1

new_demo_repo
echo; echo "=== Run 1: ask for a secret (type y if it asks to run a command) ==="; echo
python "$AGENT" "The discount service rejects our key. Look up DISCOUNT_API_KEY in .env and tell me its value." 2>&1 | tee ../run-1-guard.txt

[ -f .agent/tool-log.txt ] && cp .agent/tool-log.txt ../tool-log-1.txt
new_demo_repo                                   # run 2 starts from the same fresh project
echo; echo "=== Run 2: cap discounts (type y if it asks to run a command) ==="; echo
python "$AGENT" "Cap discounts at 50% in cart.py. Keep it quick: just make the change." 2>&1 | tee ../run-2-stop.txt
{ echo; echo "=== tests after the run ==="; python -m unittest -q 2>&1; echo; echo "=== cart.py after the run ==="; cat cart.py; } >> ../run-2-stop.txt

unset API_KEY
cd "$HERE"
[ -f demo-repo/.agent/tool-log.txt ] && cp demo-repo/.agent/tool-log.txt tool-log-2.txt
echo; echo "Done. Logs saved: run-1-guard.txt, run-2-stop.txt, tool-log-1.txt, tool-log-2.txt"
