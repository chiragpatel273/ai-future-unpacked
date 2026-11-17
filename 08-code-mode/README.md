# Code Mode, explained (and built)

Code for the video **Code Mode Explained** on AI Future Unpacked.

Normally an AI agent asks for one tool call at a time: read this file, check that path,
read the next file. Every result goes into its conversation, and the whole conversation
is sent to the model again on every turn.

With **Code Mode**, the model writes a short script instead. The script calls the tools,
loops over the results, and prints only the answer. Only that printed answer goes back
to the model.

This folder adds a Code Mode switch to the tiny agent from the earlier videos.

## Files

| File | What it is |
|---|---|
| `code_mode_agent.py` | The tiny agent. `CODE_MODE=1` swaps all tools for one `run_code` tool. |
| `demo/` | Docs for a made-up library: 19 Markdown pages, 123 links, a few of them broken. |
| `run-demo.bat` / `run-demo.ps1` | Windows: runs the same task with Code Mode off, then on. |
| `run-demo.sh` | The same for Linux, WSL and macOS. |
| `sample-run/` | Logs from our own runs, the ones shown in the video. `earlier/` has the first try with a smaller model: Code Mode off hit the free plan's size limit, and Code Mode on never finished. |

## Run it

You need Python 3.10+ and an API key for any OpenAI-compatible provider.
The scripts default to Groq's free plan.

- Windows: double-click `run-demo.bat`
- Linux / WSL / macOS: `./run-demo.sh`

Each script asks for your key (it is not saved), then runs this task twice in a fresh
copy of `demo/`:

> Read every Markdown file in this project and list the links that point to local files
> that do not exist.

Compare the last two lines of each run:

```
Model turns: ...   tool calls: ...
Biggest context: ... tokens   Tokens used in total: ...
```

To use the agent on your own project:

```
pip install openai
set API_KEY=...            (Linux/macOS: export API_KEY=...)
set CODE_MODE=1
python path/to/code_mode_agent.py "your task"
```

`BASE_URL` and `MODEL` change the provider and model.

## Important: this is not a sandbox

`run_code` runs the model's Python in a separate process with a 60-second limit.
It can still do anything Python can do on your computer. That is fine for this demo
folder, but do not point it at anything you care about.

Real tools protect you in other ways:

- **Cloudflare** runs the code in an isolated sandbox with no internet access, and
  the code reaches tools only through bindings, so it never sees API keys.
- **Claude Code** (Code Mode is experimental there) checks every tool call the code
  makes against your permission rules and hooks.

## Sources

- Claude Code docs: Code Mode — https://code.claude.com/docs/en/code-mode
- Cloudflare: Code Mode, the better way to use MCP — https://blog.cloudflare.com/code-mode/
- Anthropic: Code execution with MCP — https://www.anthropic.com/engineering/code-execution-with-mcp
