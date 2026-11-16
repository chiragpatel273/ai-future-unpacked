"""hooks-agent: the tiny agent from our earlier videos, now with hooks.

A hook is YOUR program. The agent runs it at fixed moments, every time:
    PreToolUse    before a tool runs     -> can block it
    PostToolUse   after a tool ran       -> can watch (can't undo)
    Stop          when the agent is done -> can send it back to work

Hooks are listed in .agent/hooks.json in the project folder. Like Claude Code, Cursor and Codex:
the hook gets the event as JSON on stdin, exit 0 = carry on, exit 2 = block, and what it
prints to stderr is the reason the model sees.

    pip install openai
    set API_KEY (and optionally BASE_URL and MODEL), then, inside your project:
    python path/to/hooks_agent.py "fix the failing test"
"""
import json, os, re, subprocess, sys
from openai import OpenAI, BadRequestError

MODEL = os.environ.get("MODEL", "openai/gpt-oss-120b")

SYSTEM = """You are a careful coding agent in the current folder.
Use the tools to read files and run commands. Make small edits.
When you are done, reply with a short summary."""
SYSTEM += "\nCommands run in " + ("Windows cmd." if os.name == "nt" else "bash.")

# ---------- 1. Built-in tools (same as before) ----------
def read_file(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def edit_file(path, old, new):
    text = read_file(path)
    if text.count(old) != 1:
        return "Error: 'old' must appear exactly once in the file."
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))
    return f"Edited {path}."

def run_command(command):
    if input(f"\n  Run `{command}`? [y/N] ").strip().lower() != "y":
        return "The user declined to run this command."
    result = subprocess.run(command, shell=True, text=True, capture_output=True,
                            timeout=60, encoding="utf-8", errors="replace")
    return (result.stdout + result.stderr)[-4000:] or "(no output)"

TOOLS = {"read_file": read_file, "edit_file": edit_file, "run_command": run_command}

def tool(name, description, **params):
    props = {p: {"type": "string", "description": d} for p, d in params.items()}
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": props, "required": list(params)}}}

TOOL_SPECS = [
    tool("read_file", "Read a text file and return its contents.", path="Path to the file"),
    tool("edit_file", "Replace one exact snippet of text in a file.", path="Path to the file",
         old="Exact text to replace (must appear once)", new="Replacement text"),
    tool("run_command", "Run a shell command.", command="The command to run"),
]

# ---------- 2. Hooks: load .agent/hooks.json ----------
def load_hooks(path=".agent/hooks.json"):
    if not os.path.exists(path):
        return {}
    hooks = json.load(open(path, encoding="utf-8"))["hooks"]
    for event, handlers in hooks.items():
        for h in handlers:
            print(f"hook  {event:<12} {h.get('matcher', '*'):<22} {' '.join([h['command'], *h.get('args', [])])}")
    return hooks

HOOKS = {}

# ---------- 3. Run the hooks for one event ----------
def run_hooks(event, data, tool_name=None):
    """Run every matching hook. Returns the reason if one of them blocks (exit 2), else None."""
    for h in HOOKS.get(event, []):
        if tool_name and not re.fullmatch(h.get("matcher", ".*"), tool_name):
            continue
        command = sys.executable if h["command"] == "python" else h["command"]
        try:
            p = subprocess.run([command, *h.get("args", [])],          # no shell: one program + its args
                               input=json.dumps({"hook_event_name": event, **data}),
                               text=True, capture_output=True, timeout=h.get("timeout", 60))
        except Exception as e:
            print(f"   ! hook failed to run: {e} (ignored)")
            continue
        if p.returncode == 2:                                           # 2 = block, stderr = why
            return p.stderr.strip() or "Blocked by a hook."
        if p.returncode != 0:                                           # other errors don't block
            print(f"   ! hook exited {p.returncode} (ignored)")
    return None

# ---------- 4. The loop, with hooks at three moments ----------
def run_agent(task, max_turns=20, max_stops=3):
    client = OpenAI(api_key=os.environ["API_KEY"],
                    base_url=os.environ.get("BASE_URL", "https://api.groq.com/openai/v1"),
                    max_retries=6)               # free plans rate-limit: wait and retry
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": task}]
    stops = 0
    for turn in range(1, max_turns + 1):
        try:
            reply = client.chat.completions.create(
                model=MODEL, messages=messages, tools=TOOL_SPECS).choices[0].message
        except BadRequestError as e:                  # e.g. the model wrote broken JSON for a tool call
            print(f"\n[turn {turn}] bad tool call, asking the model to try again")
            messages.append({"role": "user", "content": f"Your last tool call failed: {e.message}. Try again."})
            continue
        message = {"role": "assistant", "content": reply.content or ""}
        if reply.tool_calls:
            message["tool_calls"] = [c.model_dump() for c in reply.tool_calls]
        messages.append(message)

        if not reply.tool_calls:                                        # the agent says it's done
            reason = run_hooks("Stop", {"stop_hook_active": stops > 0})
            if reason and stops < max_stops:                            # Stop hook: not done yet
                stops += 1
                print(f"\n[turn {turn}] wants to stop -> Stop hook says no:\n    {reason[:300]}")
                messages.append({"role": "user", "content": f"A Stop hook says you are not done yet:\n{reason}"})
                continue
            print(f"\n[turn {turn}] done\n\n{reply.content}")
            return reply.content

        for c in reply.tool_calls:
            name, args = c.function.name, json.loads(c.function.arguments or "{}")
            print(f"\n[turn {turn}] {name} {args}")
            reason = run_hooks("PreToolUse", {"tool_name": name, "tool_input": args}, name)
            if reason:                                                  # PreToolUse hook: blocked
                result = f"Blocked by a PreToolUse hook: {reason}"
            else:
                try:
                    result = TOOLS[name](**args)
                except Exception as e:                                  # errors go back to the model
                    result = f"Error: {e}"
                run_hooks("PostToolUse", {"tool_name": name, "tool_input": args,
                                          "tool_response": str(result)[:2000]}, name)
            print("   ", str(result).strip()[:300])
            messages.append({"role": "tool", "tool_call_id": c.id, "content": str(result)})
    print("Stopped: too many turns.")

if __name__ == "__main__":
    HOOKS = load_hooks()
    run_agent(" ".join(sys.argv[1:]))
