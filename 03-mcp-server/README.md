# notes-server + mcp-agent (AI Future Unpacked, video 3)

**notes_server.py** is a complete MCP server in ~30 lines: two tools (`add_note`, `search_notes`) and one resource (`notes://all`).
**mcp_agent.py** is the tiny agent from video 2, upgraded so it gets its tools from any MCP server instead of hard-coding them.

Built with the official MCP Python SDK (v2.3+, speaks the 2026-07-28 spec).

## Run the agent
```powershell
pip install openai "mcp>=2.3"
$env:API_KEY = "your-groq-key"     # free at console.groq.com
python mcp_agent.py "save a note: client demo on Friday at 3pm, then tell me what's on Friday"
```

## Plug the same server into Claude Code
```bash
claude mcp add --transport stdio notes -- python /full/path/to/notes_server.py
claude mcp list        # should show: notes ... Connected
```
Then ask Claude Code: "what's in my notes about Friday?"
