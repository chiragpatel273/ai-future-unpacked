# tiny-agent

An AI coding agent in ~100 lines of Python, from the AI Future Unpacked video
"Build an AI Coding Agent from Scratch in Python".

## Run it (Windows PowerShell)
```powershell
pip install openai
$env:API_KEY = "your-groq-key"        # free key from console.groq.com
cd demo
python ..\agent.py "fix the failing test" | Tee-Object run-log.txt
```
Type `y` when it asks to run a command.

Optional: `$env:MODEL` (default `openai/gpt-oss-120b`) and `$env:BASE_URL`
(default Groq) to use OpenAI, OpenRouter, Ollama or any OpenAI-compatible API.

## The demo
`demo/cart.py` has a bug: the discount is applied twice. `demo/test_cart.py` catches it.
Reset the demo with `git checkout demo/cart.py` or by restoring the original line
`total = discounted * (1 - discount)`.
