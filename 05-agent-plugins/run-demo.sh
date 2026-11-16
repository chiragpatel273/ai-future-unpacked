#!/usr/bin/env bash
# run-demo.sh - Linux / WSL / macOS version of run-demo.bat.
# Loads the dev-helper Agent Plugin into our tiny agent and runs two tasks:
#   1) commit a staged change (uses the plugin's SKILL)
#   2) ask what was committed (uses the plugin's MCP server)
# Saves run-1-commit.txt and run-2-notes.txt. Your API key is typed here and not saved.
set -u
cd "$(dirname "$0")"
HERE="$PWD"
AGENT="$HERE/plugin_agent.py"
PLUGIN="$HERE/dev-helper"

# 0. Python packages in a local virtual environment (.venv)
#    (inside the venv, "python" in mcp.json and SKILL.md points to the venv's Python)
if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv || { echo "Install venv first:  sudo apt install python3-venv git"; exit 1; }
fi
source .venv/bin/activate
python -c "import openai, mcp" 2>/dev/null || pip install -q --upgrade openai "mcp>=2.3"

# Start clean: no notes from earlier runs
DATA="$HOME/.tiny-agent/plugin-data/dev-helper"
rm -rf "$DATA"

# 1. A small demo repo with one staged change on a ticket branch (no skills inside it!)
rm -rf demo-repo && mkdir demo-repo && cd demo-repo
git init -q -b main
git config user.name "Demo"; git config user.email "demo@example.com"
cat > cart.py <<'EOF'
def cart_total(items, discount=0.0):
    """Total of (price, qty) items after a discount (0.10 = 10%)."""
    subtotal = sum(price * qty for price, qty in items)
    return round(subtotal * (1 - discount), 2)
EOF
git add . && git commit -q -m "Initial cart"
git checkout -q -b feature/PAY-142-discount-cap
sed -i 's/^    subtotal = sum/    discount = min(discount, 0.5)  # never more than 50% off\n    subtotal = sum/' cart.py
git add cart.py

# 2. Key (hidden while you paste)
read -rsp "Paste your Groq API key and press Enter: " API_KEY; echo
export API_KEY
export PYTHONUNBUFFERED=1

echo; echo "=== Run 1: commit (type y when it asks to run a command) ==="; echo
python "$AGENT" "$PLUGIN" "Commit my staged changes, then save a note about what you committed." 2>&1 | tee ../run-1-commit.txt
{ echo; echo "=== resulting commit message ==="; git log -1 --format=%B; } >> ../run-1-commit.txt

echo; echo "=== Run 2: a NEW session asks the notes server ==="; echo
python "$AGENT" "$PLUGIN" "What did I commit for PAY-142? Check my notes." 2>&1 | tee ../run-2-notes.txt

unset API_KEY
cd "$HERE"
echo; echo "Commit message:"; git -C demo-repo log -1 --format=%B
echo "Notes file (in PLUGIN_DATA): $DATA/notes.md"
[ -f "$DATA/notes.md" ] && cat "$DATA/notes.md" | tee notes-after-run.txt
echo; echo "Done. Logs saved."
