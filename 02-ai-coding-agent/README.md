# Build an AI Coding Agent from Scratch (video 2)

**What it is:** a working AI coding agent in about 100 lines of Python (`agent.py`): a model, three tools
(read a file, edit a file, run a command) and a loop. The `demo/` folder has a small bug for it to fix.
Video: [Build an AI Coding Agent from Scratch in Python](https://youtu.be/ZXbikEMg_9Q)

## Run it
Windows (PowerShell):
```powershell
pip install openai
$env:API_KEY = "your-groq-key"        # free key from console.groq.com
cd demo
python ..\agent.py "fix the failing test"
```
Mac / Linux / WSL:
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install openai
export API_KEY="your-groq-key"
cd demo
python ../agent.py "fix the failing test"
```
Type `y` when it asks to run a command. Want to use another model? See the main README.

## What you'll see
The agent runs the tests, reads `cart.py`, finds that the discount is applied twice, fixes that one
line and runs the tests again. If `pytest` isn't installed, it asks to install it first.

## Files
```text
agent.py           the agent: model + tools + loop
demo/cart.py       a shopping-cart function with a bug (the discount is applied twice)
demo/test_cart.py  the test that catches it
```
To run the demo again, put the bug back: `git checkout demo/cart.py`
(or restore the line `total = discounted * (1 - discount)`).
