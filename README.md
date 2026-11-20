# AI Future Unpacked: code from the videos

**AI explained simply, then we build it.** This repo has the runnable code for every build on the
[AI Future Unpacked](https://www.youtube.com/@AIFutureUnpacked) YouTube channel. Each folder is one
video, small enough to read in a few minutes.

| # | Video | Code |
|---|-------|------|
| 1 | [How AI Coding Agents Actually Work (It's Just a Loop)](https://youtu.be/KNyDTPgmryY) | explainer, no code |
| 2 | [Build an AI Coding Agent from Scratch in Python](https://youtu.be/ZXbikEMg_9Q) | [`02-ai-coding-agent/`](02-ai-coding-agent/): the ~100-line agent and the buggy demo it fixes |
| 3 | [What is MCP? Build Your Own MCP Server in 34 Lines](https://youtu.be/XG8_rFOPqVY) | [`03-mcp-server/`](03-mcp-server/): a notes MCP server and the agent that uses it |
| 4 | [Agent Skills Explained: How One Text File Teaches Your AI Agent](https://youtu.be/2A747iHL86U) | [`04-agent-skills/`](04-agent-skills/): skills support for the agent, plus a commit-message skill |
| 5 | [Agent Plugins Explained: Skills + MCP in One Folder](https://youtu.be/9woCB9uvZ-Y) | [`05-agent-plugins/`](05-agent-plugins/): a plugin with a skill and an MCP server, and the agent that loads it |
| 6 | [Agent Hooks Explained: The Rule Your AI Agent Can't Skip](https://youtu.be/topUF49GeWs) | [`06-agent-hooks/`](06-agent-hooks/): hooks for the agent: block secrets, log every action, and run the tests before "done" |
| 7 | [Subagents Explained: How AI Agents Use Helpers (and Keep Context Clean)](https://youtu.be/h8boPshOjO8) | [`07-subagents/`](07-subagents/): a `delegate` tool and an explorer subagent, plus a demo shop with three bugs to investigate |
| 8 | [Code Mode Explained: Why AI Agents Write Code Instead of Calling Tools](https://youtu.be/ab-bNKSDD-4) | [`08-code-mode/`](08-code-mode/): a `run_code` tool that lets the model write a script to call the tools, plus demo docs with broken links |

The folders build on each other: each video takes the agent from the one before and adds one idea.
You can still run any folder on its own.

### Claude Code tips
Standalone videos that measure real Claude Code behaviour. These use your own Claude Code login, not the Groq setup below.

| Video | Code |
|-------|------|
| [Why Claude Code Hits Your Limit So Fast (I Ran 51 Tests)](https://youtu.be/H5bkAmzCoic) | [`claude-code-limits/`](claude-code-limits/): scripts that measure Claude Code's tokens per request, plus my raw logs |

## How to use this repo

### 1. One-time setup (about 5 minutes)
- **Python 3.10 or newer** from [python.org](https://www.python.org/downloads/).
  On Windows, tick **"Add python.exe to PATH"** in the installer.
- **Git** from [git-scm.com](https://git-scm.com/downloads) (the demos in folders 04, 05 and 06 use it).
- **A free API key** from [Groq](https://console.groq.com): sign in, open *API Keys*, create one.
  Keep it private: never paste it into a file you commit.

Check it worked (in a new terminal):
```bash
python --version     # Mac/Linux: python3 --version
git --version
```

### 2. Get the code
```bash
git clone https://github.com/chiragpatel273/ai-future-unpacked.git
cd ai-future-unpacked
```
No git? Use the green **Code → Download ZIP** button on GitHub, then unzip it.

### 3. Pick a folder and run it
Every folder's README has the same parts: **What it is → Run it → What you'll see → Files**.

- **Windows:** folders with a `run-demo.bat` just need a double-click. It sets everything up and asks for your key.
- **Mac, Linux or WSL:** run `bash run-demo.sh` in folders that have one.
- **By hand:** each README also shows the exact commands.

The demo scripts ask for your key with hidden input and don't save it anywhere.

### 4. Use another model (optional)
The code works with any OpenAI-compatible API. Set these before running:

| Provider | `BASE_URL` | `MODEL` (example) |
|---|---|---|
| Groq (default) | `https://api.groq.com/openai/v1` | `openai/gpt-oss-120b` |
| OpenAI | `https://api.openai.com/v1` | a model from your account |
| OpenRouter | `https://openrouter.ai/api/v1` | a model id from openrouter.ai |
| Ollama (local) | `http://localhost:11434/v1` | a model you've pulled (key can be any text) |

```powershell
$env:BASE_URL = "https://openrouter.ai/api/v1"; $env:MODEL = "..."   # Windows PowerShell
```
```bash
export BASE_URL="https://openrouter.ai/api/v1" MODEL="..."           # Mac / Linux / WSL
```
Smaller models are often worse at using tools, so results can differ from the videos.

## If something goes wrong
| You see | Fix |
|---|---|
| `'python' is not recognized` | Reinstall Python with "Add to PATH" ticked, then open a new terminal. |
| `python: command not found` (Mac/Linux) | Use `python3`, or run the folder's `run-demo.sh`, which uses a virtual environment. |
| `ModuleNotFoundError: No module named 'openai'` (or `mcp`) | `pip install openai "mcp>=2.3"` (Mac/Linux: inside a venv, see below). |
| `error: externally-managed-environment` (Linux/WSL) | `python3 -m venv .venv && source .venv/bin/activate`, then `pip install ...` again. |
| `401` / `Invalid API Key` | The key is wrong or was revoked. Create a new one at console.groq.com. |
| `429` / `rate limit` | The free plan has per-minute limits. The code waits and retries; if it still fails, wait a minute. |
| `413` / `Request too large` | One request is bigger than the free plan's per-minute token limit. Use a model with higher limits, or turn on Code Mode (video 8), which keeps requests small. |
| `Not logged in · Please run /login` (claude-code-limits) | The script found a Claude Code that isn't logged in. Run `claude` in the same place (Windows or WSL) and type `/login`. |
| `'git' is not recognized` | Install Git, then open a new terminal. |
| `run-demo.ps1 cannot be loaded ... disabled on this system` | Double-click `run-demo.bat` instead: it runs the script without changing your settings. |
| `bash: run-demo.sh: /bin/bash^M: bad interpreter` | The file got Windows line endings. Run `sed -i 's/\r$//' run-demo.sh` and try again. |

## Be careful
These agents can read files and run commands on your machine. Run them in a folder you don't mind
them touching, and read what a command does before you type `y`.
The Code Mode agent (video 8) runs Python the model wrote. It is not a sandbox: use it on its demo folder only.

## License
MIT. Use it, change it, build on it.
