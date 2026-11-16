#!/usr/bin/env bash
# run-demo.sh - Mac / Linux / WSL version of run-demo.bat.
# Runs skills_agent twice on the same staged change: first WITHOUT skills, then WITH.
# Saves run-without-skills.txt and run-with-skills.txt. Your API key is typed here and not saved.
set -u
cd "$(dirname "$0")"
HERE="$PWD"
AGENT="$HERE/skills_agent.py"

# Python packages in a local virtual environment (.venv)
if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv || { echo "Install venv first:  sudo apt install python3-venv git"; exit 1; }
fi
source .venv/bin/activate
python -c "import openai" 2>/dev/null || pip install -q --upgrade openai

# 1. A small demo repo with one staged change on a ticket branch
rm -rf demo-repo && mkdir demo-repo && cd demo-repo
git init -q -b main
git config user.name "Demo"; git config user.email "demo@example.com"
cat > cart.py <<'PY'
def cart_total(items, discount=0.0):
    """Total of (price, qty) items after a discount (0.10 = 10%)."""
    subtotal = sum(price * qty for price, qty in items)
    return round(subtotal * (1 - discount), 2)
PY
mkdir -p .agents && cp -r ../skills .agents/skills
git add . && git commit -q -m "Initial cart and team skills"
git checkout -q -b feature/PAY-142-discount-cap
sed -i.bak 's/^    subtotal = sum/    discount = min(discount, 0.5)  # never more than 50% off\
    subtotal = sum/' cart.py && rm -f cart.py.bak
git add cart.py

# 2. Key (hidden while you paste)
read -rsp "Paste your Groq API key and press Enter: " API_KEY; echo
export API_KEY PYTHONUNBUFFERED=1
TASK="Commit my staged changes."

echo; echo "=== Run 1: WITHOUT skills (type y when it asks to run a command) ==="; echo
NO_SKILLS=1 python "$AGENT" "$TASK" 2>&1 | tee ../run-without-skills.txt
MSG1=$(git log -1 --format=%B)
printf '\n=== resulting commit message ===\n%s\n' "$MSG1" >> ../run-without-skills.txt
git reset -q --soft HEAD~1   # undo that commit, keep the change staged

echo; echo "=== Run 2: WITH the commit-message skill ==="; echo
python "$AGENT" "$TASK" 2>&1 | tee ../run-with-skills.txt
MSG2=$(git log -1 --format=%B)
printf '\n=== resulting commit message ===\n%s\n' "$MSG2" >> ../run-with-skills.txt

unset API_KEY
cd "$HERE"
echo; echo "Without skills:"; echo "$MSG1"
echo; echo "With skills:"; echo "$MSG2"
echo; echo "Done. Logs saved in run-without-skills.txt and run-with-skills.txt."
