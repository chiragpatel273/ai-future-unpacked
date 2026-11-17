#!/usr/bin/env bash
# run-demo.sh - Linux / WSL / macOS version of run-demo.bat.
# Our tiny agent with Code Mode off, then on. The same task, twice, in a fresh copy of the demo docs:
#   1) Code Mode off  -> the model asks for one tool call at a time and reads every result
#   2) Code Mode on   -> the model writes one Python script that calls the tools and prints the answer
# Watch "context: N tokens" on each turn. Saves run-1-normal.txt and run-2-code-mode.txt.
# Your API key is typed here and not saved.
set -u
cd "$(dirname "$0")"
HERE="$PWD"
AGENT="$HERE/code_mode_agent.py"
TASK="Read every Markdown file in this project and list the links that point to local files that do not exist. For each one, give the file it is in and the link. Do not change any files."

if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv || { echo "Install venv first:  sudo apt install python3-venv"; exit 1; }
fi
source .venv/bin/activate
python -c "import openai" 2>/dev/null || pip install -q --upgrade openai

new_demo_repo() { cd "$HERE" && rm -rf demo-repo && cp -r demo demo-repo && cd demo-repo; }

read -rsp "Paste your Groq API key and press Enter: " API_KEY; echo
export API_KEY
read -rp "Model (press Enter for openai/gpt-oss-120b): " M
[ -n "$M" ] && export MODEL="$M"
export PYTHONUNBUFFERED=1

new_demo_repo
echo; echo "=== Run 1: Code Mode off ==="; echo
CODE_MODE=0 python "$AGENT" "$TASK" 2>&1 | tee ../run-1-normal.txt

new_demo_repo
echo; echo "=== Run 2: Code Mode on ==="; echo
CODE_MODE=1 python "$AGENT" "$TASK" 2>&1 | tee ../run-2-code-mode.txt

unset API_KEY
cd "$HERE"
echo; echo "Done. Logs saved: run-1-normal.txt, run-2-code-mode.txt"
