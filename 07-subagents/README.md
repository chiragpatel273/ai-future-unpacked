# Subagents Explained (video 7)

**What it is:** a subagent is a helper agent. The main agent hands it a task, the helper starts with an
**empty conversation**, does the messy work (listing, searching and reading files), and only its **short
report** comes back. The main agent's context stays small. `subagents_agent.py` is our tiny agent from the
earlier videos plus one new tool, `delegate`. The same loop runs the main agent and every helper:

|                          | Main agent                 | Helper (subagent)                          |
|--------------------------|----------------------------|--------------------------------------------|
| Conversation             | the whole task so far      | starts empty: only its own task            |
| Instructions             | the coding agent prompt    | the body of its `.md` file                 |
| Tools                    | all tools + `delegate`     | only the tools in its file (no `delegate`) |
| What the main agent sees |                            | only the final report                      |

If the model asks for several helpers in one turn, they run in parallel.
Video: [Subagents Explained: How AI Agents Use Helpers (and Keep Context Clean)](https://youtu.be/h8boPshOjO8)

## Run it
You need Python 3.10+. The demo runs the same task twice, each time in a fresh `demo-repo/` copied from `demo/`:

> Customers reported three problems. 1) Coupon SAVE10 gives no discount at all when the cart has a sale item.
> 2) A US order of exactly 50.00 dollars still pays shipping, but we promise free shipping from 50 dollars.
> 3) The order email for 3 mugs shows 12.00 on the mug line, but 3 mugs cost 36.00. For each problem, find the
> cause: the file, the function and the line. If you have helper agents, use one per problem. Do not change any
> code yet. Reply with a short report.

1. **No subagents** (the `.agent` folder is removed): the main agent reads the files itself.
2. **With the explorer:** the main agent sends one explorer per problem, in parallel, and gets back only their reports.

(The demo shop has these three bugs on purpose.)

- **Windows:** double-click `run-demo.bat`
- **Mac / Linux / WSL:** `bash run-demo.sh` (makes a `.venv` and installs `openai` there;
  on Ubuntu/WSL you may first need `sudo apt install python3-venv`)

Paste your Groq key when asked (hidden, not saved). It also asks which model to use: press Enter for the
default. The runs in the video used `qwen/qwen3.8-27b`.

By hand, inside a project that has `.agent/agents/`:
```bash
pip install openai
export API_KEY="your-groq-key"          # PowerShell: $env:API_KEY = "your-groq-key"
python path/to/subagents_agent.py "find out why the SAVE10 coupon fails"
```

## What you'll see
```text
subagent  explorer: Searches and reads the codebase to answer a question. Use it before reading files yourself.

[main turn 1] context: 958 tokens
  delegate {"agent": "explorer", "task": "Bug hunt, read-only. Problem: a coupon named \"SAVE10\" ...
  delegate {"agent": "explorer", "task": "Bug hunt, read-only. Problem: a US order of EXACTLY 50.00 ...
  delegate {"agent": "explorer", "task": "Bug hunt, read-only. Problem: the order confirmation email ...

        [explorer turn 1] context: 668 tokens
          list_files {"folder": "."}
        ...
```
Every turn prints `context: N tokens`, the size of what was sent to the model. Helpers print indented.
The last line is the tokens used by all agents together. In the video's runs:

|                                     | Run 1: no helpers | Run 2: three explorers |
|-------------------------------------|------------------:|-----------------------:|
| Files the main agent read           | 11                | 3 (to double-check)    |
| Main agent's context at the end     | 6,640 tokens      | 2,830 tokens           |
| Tokens used by all agents together  | 42,380            | 24,252                 |

`sample-run/` has those real logs, plus two earlier runs that taught us something (see below).

## Files
```text
demo/                          the project the agent works in (a tiny shop, with 3 bugs on purpose)
├── shop/                      cart, pricing, coupons, rules, shipping, tax, orders, emails, products
├── tests/test_pricing.py
├── docs/CHANGELOG.md
└── .agent/agents/explorer.md  the helper: name, description, tools, then its instructions
subagents_agent.py             the agent: tools (1), subagents (2), the loop (3)
run-demo.bat / .ps1 / .sh      the demo
sample-run/                    real logs from the video
```
Helpers live in `.agent/agents/`, the same idea as `.claude/agents/` (Claude Code), `.cursor/agents/`
(Cursor) and `.github/agents/` (VS Code / GitHub Copilot). Codex uses TOML files in `.codex/agents/`.
`subagents_agent.py` is a small teaching agent: real apps each have their own fields and settings. See their docs.

## Good to know
- **Ask for helpers.** In our first try the model had the explorer and never used it
  (`sample-run/earlier/1-never-used-the-helper.txt`). Codex, for example, only starts subagents when you ask,
  or when your instructions do.
- **Helpers pay off for answers, not edits.** When the task was "fix it", the main agent used the explorer and
  then read the same files again, because it has to see a file to edit it (`sample-run/earlier/2-fix-task-read-files-again.txt`).
- **Cost:** every helper is its own model conversation, so subagents usually cost more tokens in total.
  In our run the total went down, because run 1 re-sent one growing conversation 11 times. Don't count on it.
- **The report is all the main agent gets.** Tell helpers exactly what to report.
- Reading in parallel is easy. Several helpers editing the same files can conflict.
