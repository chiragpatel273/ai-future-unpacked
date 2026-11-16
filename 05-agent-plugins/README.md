# Agent Plugins Explained (video 5)

**What it is:** `dev-helper/` is an **Agent Plugins 1.0** package: one folder that bundles the
commit-message skill (video 4) and the notes MCP server (video 3). `plugin_agent.py` is our agent, now able
to load a plugin folder: it checks `plugin.json`, finds the skills, starts the MCP servers, and skips
anything broken instead of crashing.
Video: Agent Plugins Explained: Skills + MCP in One Folder *(link added on release)*

## Run it
The demo builds a small git repo with one staged change (and no skills in it), then runs two tasks
with the plugin:
1. "Commit my staged changes, then save a note about what you committed." (skill + MCP server)
2. "What did I commit for PAY-142? Check my notes." (a new session reads the note back)

- **Windows:** double-click `run-demo.bat`
- **Mac / Linux / WSL:** `bash run-demo.sh` (makes a `.venv` and installs `openai` and `mcp` there;
  on Ubuntu/WSL you may first need `sudo apt install python3-venv git`)

Paste your Groq key when asked (hidden, not saved) and type `y` when it asks to run a command.

By hand:
```bash
pip install openai "mcp>=2.3"
export API_KEY="your-groq-key"          # PowerShell: $env:API_KEY = "your-groq-key"
python plugin_agent.py ./dev-helper "commit my staged changes"
```

## What you'll see
```text
Plugin: dev-helper 1.0.0
  skill  commit-message
  server notes (stdio)
  server notes connected: add_note, search_notes
```
Then the agent loads the skill, commits `feat(cart): cap discount at 50%` with a reason and
`Refs: PAY-142`, and saves a note with `add_note`. The second run finds it with `search_notes`.
The note is stored in the plugin's data folder (`~/.tiny-agent/plugin-data/dev-helper/`), which
survives plugin updates. `sample-run/` has the real logs from the video.

## Files
```text
dev-helper/
├── plugin.json                  who the plugin is ($schema + name are required)
├── skills/commit-message/       an Agent Skill
│   ├── SKILL.md
│   └── scripts/check_message.py
├── mcp.json                     MCP servers to start
└── servers/notes_server.py      the notes MCP server (saves to PLUGIN_DATA)
plugin_agent.py                  the agent + plugin loader (section 2)
run-demo.bat / .ps1 / .sh        the demo
sample-run/                      real logs from the video
```
`plugin.json` and `mcp.json` validate against the official 1.0.0 schemas
(https://github.com/agentplugins/agent-plugins-spec). `plugin_agent.py` is a small teaching client:
it supports skills and local (stdio) MCP servers only.

`mcp.json` starts the server with `python`. Inside a virtual environment (as `run-demo.sh` uses),
`python` exists on Mac and Linux too. Without one, install `python-is-python3` or change `"command"` to `"python3"`.

## Use the same folder in VS Code
Turn on `chat.plugins.enabled`, then run **Chat: Install Plugin from Source** and pick the `dev-helper` folder.

## Be careful
A plugin can start programs on your machine (its MCP servers), and Agent Plugins 1.0 has no permission
system. Read `mcp.json` and the code before installing a plugin from anyone you don't trust.
