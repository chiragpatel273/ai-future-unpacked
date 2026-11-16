# Agent Hooks Explained (video 6)

**What it is:** a hook is **your** program that the agent app runs at fixed moments, every time. The model
can ignore an instruction in AGENTS.md. It can't skip a hook. `hooks_agent.py` is our tiny agent from the
earlier videos, now with three hook events:

| Event         | When it runs                 | What it can do                        |
|---------------|------------------------------|---------------------------------------|
| `PreToolUse`  | before a tool runs           | block it (exit code 2)                |
| `PostToolUse` | after a tool ran             | watch and log (it can't undo)         |
| `Stop`        | when the agent says "done"   | send it back to work (exit code 2)    |

Like Claude Code and Cursor: the hook gets the event as JSON on stdin, exit `0` means carry on, exit `2`
means block, and what it prints to stderr is the reason the model sees.
Video: [Agent Hooks Explained: The Rule Your AI Agent Can't Skip](https://youtu.be/topUF49GeWs)

## Run it
You need Python 3.10+ and git. For each task the demo makes a fresh `demo-repo/` (a git repo copied from
`demo/`, plus a fake `.env`) and runs:
1. "Look up DISCOUNT_API_KEY in .env and tell me its value." The guard hook blocks it.
2. "Cap discounts at 50% in cart.py. Keep it quick: just make the change." The Stop hook runs the tests
   before the agent is allowed to finish.

- **Windows:** double-click `run-demo.bat`
- **Mac / Linux / WSL:** `bash run-demo.sh` (makes a `.venv` and installs `openai` there;
  on Ubuntu/WSL you may first need `sudo apt install python3-venv git`)

Paste your Groq key when asked (hidden, not saved) and type `y` when it asks to run a command.

By hand, inside a project that has `.agent/hooks.json`:
```bash
pip install openai
export API_KEY="your-groq-key"          # PowerShell: $env:API_KEY = "your-groq-key"
python path/to/hooks_agent.py "cap discounts at 50% in cart.py"
```

## What you'll see
```text
hook  PreToolUse   read_file|run_command  python .agent/hooks/guard.py
hook  PostToolUse  edit_file|run_command  python .agent/hooks/log.py
hook  Stop         *                      python .agent/hooks/tests_pass.py

[turn 1] read_file {'path': '.env'}
    Blocked by a PreToolUse hook: .env holds secrets, so it is off-limits. Ask the user for the value you need.
```
In task 2, whenever the agent wants to stop after changing code, the Stop hook runs the tests. If they
fail, the agent gets the failures and keeps working (at most 3 times). Every edit and command is written
to `.agent/tool-log.txt`. `sample-run/` has the real logs from the video, including the first run
before we scoped the Stop hook.

## Files
```text
demo/                         the project the agent works in
├── cart.py, test_cart.py     a small cart with two failing tests
└── .agent/
    ├── hooks.json            which hook runs when
    └── hooks/
        ├── guard.py          PreToolUse: blocks .env and recursive deletes
        ├── log.py            PostToolUse: writes every edit and command to .agent/tool-log.txt
        └── tests_pass.py     Stop: if code changed (git), run the tests; if they fail, keep working
hooks_agent.py                the agent + hooks runner (sections 2-4)
run-demo.bat / .ps1 / .sh     the demo
sample-run/                   real logs from the video
```
`hooks_agent.py` is a small teaching agent. Real apps (Claude Code, Codex, Cursor, GitHub Copilot) each have
their own hook file and event names. See their docs.

## Be careful
- Hooks are code that runs on your machine without asking. Read a project's hooks before you run an agent in it.
- `guard.py` matches text, so a creative command can slip past it (`type .e*` does). Hooks are a guardrail,
  not a sandbox: use them together with permissions and a sandbox.
