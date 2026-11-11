# AI Future Unpacked — code from the videos

**AI explained simply, then we build it.** This repo has the runnable code for every build on the
[AI Future Unpacked](https://www.youtube.com/@AIFutureUnpacked) YouTube channel. Each folder is one
video, small enough to read in a few minutes.

| # | Video | Code |
|---|-------|------|
| 1 | [How AI Coding Agents Actually Work (It's Just a Loop)](https://youtu.be/KNyDTPgmryY) | explainer, no code |
| 2 | [Build an AI Coding Agent from Scratch in Python](https://youtu.be/ZXbikEMg_9Q) | [`02-ai-coding-agent/`](02-ai-coding-agent/): the ~100-line agent and the buggy demo it fixes |
| 3 | [What is MCP? Build Your Own MCP Server in 34 Lines](https://youtu.be/XG8_rFOPqVY) | [`03-mcp-server/`](03-mcp-server/): a notes MCP server and the agent that uses it |

## What you need
- Python 3.10 or newer
- A free API key from [Groq](https://console.groq.com) (or any OpenAI-compatible API: set `BASE_URL` and `MODEL`)

Each folder's README has the exact commands.

## Quick start
```bash
git clone https://github.com/chiragpatel273/ai-future-unpacked.git
cd ai-future-unpacked/03-mcp-server
pip install openai "mcp>=2.3"
export API_KEY="your-groq-key"      # PowerShell: $env:API_KEY = "your-groq-key"
python mcp_agent.py "save a note: client demo on Friday at 3pm, then tell me what's on Friday"
```

## Be careful
These agents can read files and run commands on your machine. Run them in a folder you don't mind
them touching, and read what a command does before you approve it.

## License
MIT. Use it, change it, build on it.
