# What is MCP? Build Your Own MCP Server (video 3)

**What it is:** `notes_server.py` is a complete MCP server in about 30 lines: two tools (`add_note`,
`search_notes`) and one resource (`notes://all`). `mcp_agent.py` is the agent from video 2, upgraded to get
its tools from any MCP server instead of hard-coding them. Built with the official MCP Python SDK (v2.3+).
Video: [What is MCP? Build Your Own MCP Server in 34 Lines](https://youtu.be/XG8_rFOPqVY)

## Run it
Windows (PowerShell):
```powershell
pip install openai "mcp>=2.3"
$env:API_KEY = "your-groq-key"     # free at console.groq.com
python mcp_agent.py "save a note: client demo on Friday at 3pm, then tell me what's on Friday"
```
Mac / Linux / WSL:
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install openai "mcp>=2.3"
export API_KEY="your-groq-key"
python mcp_agent.py "save a note: client demo on Friday at 3pm, then tell me what's on Friday"
```

## What you'll see
The agent starts the notes server, discovers its two tools, saves the note with `add_note`, then finds it
again with `search_notes`. The notes are stored in `notes.md` next to the server.

## Plug the same server into Claude Code
```bash
claude mcp add --transport stdio notes -- python /full/path/to/notes_server.py
claude mcp list        # should show: notes ... Connected
```
Then ask Claude Code: "what's in my notes about Friday?"

## Files
```text
notes_server.py   the MCP server (tools + resource)
mcp_agent.py      the agent, now getting its tools over MCP
```
