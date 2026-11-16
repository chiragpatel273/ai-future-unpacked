# Agent Plugins: one folder for Skills + MCP (AI Future Unpacked, video 6)

`dev-helper/` is an **Agent Plugins 1.0** package. It bundles what we built in two earlier videos:

```text
dev-helper/
├── plugin.json                  who the plugin is ($schema + name are required)
├── skills/commit-message/       an Agent Skill (from "Agent Skills Explained")
│   ├── SKILL.md
│   └── scripts/check_message.py
├── mcp.json                     MCP servers to start
└── servers/notes_server.py      the notes MCP server (from "What is MCP?")
```

`plugin.json` and `mcp.json` validate against the official 1.0.0 schemas
(https://github.com/agentplugins/agent-plugins-spec).

`plugin_agent.py` is our tiny agent, now able to load a plugin folder: it checks `plugin.json`,
finds the skills, starts the MCP servers with `PLUGIN_ROOT` / `PLUGIN_DATA`, and skips anything broken
without crashing. It is a small teaching client: it supports skills and stdio MCP servers only.

## Run it

**Linux / WSL / macOS:** `bash run-demo.sh` (it makes a `.venv` and installs `openai` and `mcp` there).
On Ubuntu/WSL you may first need: `sudo apt install python3-venv git`

**Windows:** double-click `run-demo.bat`.

Paste a free Groq API key (console.groq.com) when asked. It runs two tasks:
1. "Commit my staged changes, then save a note" (skill + MCP server)
2. "What did I commit for PAY-142? Check my notes." (a new session reads the note back)

Or by hand:
```powershell
pip install openai "mcp>=2.3"
$env:API_KEY = "your-groq-key"
python plugin_agent.py .\dev-helper "commit my staged changes"
```

`mcp.json` starts the server with `python`. Inside a virtual environment (as `run-demo.sh` uses), `python` exists on
Linux and macOS too. Without one, install `python-is-python3` or change `"command"` to `"python3"`.

## Use the same folder in VS Code
Turn on `chat.plugins.enabled`, then run **Chat: Install Plugin from Source** and pick the `dev-helper` folder.

## Be careful
A plugin can start programs on your machine (its MCP servers). Read `mcp.json` and the code before
installing a plugin from anyone you don't trust.

## The run from the video
`sample-run/` holds the real, unedited logs shown in the video (gpt-oss-120b on Groq's free plan):
`run-1-commit.txt` (the skill writes the commit, the MCP server saves a note) and
`run-2-notes.txt` (a new session finds the note again).
