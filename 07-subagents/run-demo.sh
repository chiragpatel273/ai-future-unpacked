#!/usr/bin/env bash
# run-demo.sh - Linux / WSL / macOS version of run-demo.bat.
# Our tiny agent with and without a subagent. The same investigation task, twice, in a fresh copy of the demo:
#   1) no subagents           -> the main agent reads everything itself
#   2) with the explorer      -> the explorer reads, the main agent only gets its report
# Watch "context: N tokens" on each turn. Saves run-1-no-subagent.txt and run-2-with-subagent.txt.
# Your API key is typed here and not saved.
set -u
cd "$(dirname "$0")"
HERE="$PWD"
AGENT="$HERE/subagents_agent.py"
TASK="Customers reported three problems. 1) Coupon SAVE10 gives no discount at all when the cart has a sale item. 2) A US order of exactly 50.00 dollars still pays shipping, but we promise free shipping from 50 dollars. 3) The order email for 3 mugs shows 12.00 on the mug line, but 3 mugs cost 36.00. For each problem, find the cause: the file, the function and the line. If you have helper agents, use one per problem. Do not change any code yet. Reply with a short report."

if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv || { echo "Install venv first:  sudo apt install python3-venv"; exit 1; }
fi
source .venv/bin/activate
python -c "import openai" 2>/dev/null || pip install -q --upgrade openai

new_demo_repo() {   # $1 = 1 to keep the explorer subagent
    cd "$HERE" && rm -rf demo-repo && cp -r demo demo-repo && cd demo-repo
    [ "$1" = 1 ] || rm -rf .agent
}

read -rsp "Paste your Groq API key and press Enter: " API_KEY; echo
export API_KEY
read -rp "Model (press Enter for openai/gpt-oss-120b): " M
[ -n "$M" ] && export MODEL="$M"
export PYTHONUNBUFFERED=1

new_demo_repo 0
echo; echo "=== Run 1: no subagents ==="; echo
python "$AGENT" "$TASK" 2>&1 | tee ../run-1-no-subagent.txt

new_demo_repo 1
echo; echo "=== Run 2: with the explorer subagent ==="; echo
python "$AGENT" "$TASK" 2>&1 | tee ../run-2-with-subagent.txt

unset API_KEY
cd "$HERE"
echo; echo "Done. Logs saved: run-1-no-subagent.txt, run-2-with-subagent.txt"
