"""subagents-agent: the tiny agent from our earlier videos, now with subagents.

A subagent is a helper agent. The main agent hands it a task, the helper starts
with an EMPTY conversation, does the messy work (reading and searching files),
and only its short report comes back. The main agent's context stays small.

Helpers are Markdown files in .agent/agents/ in the project folder, like
Claude Code (.claude/agents/) and Cursor (.cursor/agents/):

    ---
    name: explorer
    description: Use to search and read the codebase. Returns a short report.
    tools: read_file, list_files, search
    ---
    You are a code explorer. ...   (this text is the helper's system prompt)

    pip install openai
    set API_KEY (and optionally BASE_URL and MODEL), then, inside your project:
    python path/to/subagents_agent.py "find and fix the coupon bug"
"""
import glob, json, os, re, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI, BadRequestError

MODEL = os.environ.get("MODEL", "openai/gpt-oss-120b")
client = OpenAI(api_key=os.environ.get("API_KEY", "none"),
                base_url=os.environ.get("BASE_URL", "https://api.groq.com/openai/v1"),
                max_retries=8)                   # free plans rate-limit: wait and retry

SYSTEM = """You are a careful coding agent in the current folder.
Use the tools to read files and run commands. Make small edits.
When you are done, reply with a short summary."""
SYSTEM += "\nCommands run in " + ("Windows cmd." if os.name == "nt" else "bash.")
HELPERS = """You have helper agents (the delegate tool). Delegate searching and reading
the codebase to a helper. Read a file yourself only right before you edit it."""

# ---------- 1. Tools ----------
def read_file(path, **_):          # **_ : ignore extra arguments the model invents
    with open(path, encoding="utf-8") as f:
        return f.read()

def list_files(folder=".", **_):
    return "\n".join(p for p in sorted(glob.glob(f"{folder}/**/*", recursive=True))
                     if os.path.isfile(p) and "/." not in p.replace("\\", "/"))

def search(pattern, folder=".", **_):
    hits = []
    for p in list_files(folder).splitlines():
        try:
            for n, line in enumerate(open(p, encoding="utf-8"), 1):
                if re.search(pattern, line, re.I):
                    hits.append(f"{p}:{n}: {line.rstrip()}")
        except UnicodeDecodeError:
            pass
    return "\n".join(hits[:200]) or "(no matches)"

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

TOOLS = {"read_file": read_file, "list_files": list_files, "search": search,
         "edit_file": edit_file, "run_command": run_command}

def tool(name, description, **params):
    props = {p: {"type": "string", "description": d} for p, d in params.items()}
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": props, "required": list(params)}}}

SPECS = {
    "read_file": tool("read_file", "Read a text file and return its contents.", path="Path to the file"),
    "list_files": tool("list_files", "List every file in a folder.", folder="Folder, e.g. ."),
    "search": tool("search", "Find lines matching a regex in all files.", pattern="Regex", folder="Folder, e.g. ."),
    "edit_file": tool("edit_file", "Replace one exact snippet of text in a file.", path="Path to the file",
                      old="Exact text to replace (must appear once)", new="Replacement text"),
    "run_command": tool("run_command", "Run a shell command.", command="The command to run"),
}

# ---------- 2. Subagents: load .agent/agents/*.md ----------
def load_agents(folder=".agent/agents"):
    agents = {}
    for path in sorted(glob.glob(f"{folder}/*.md")):
        head, body = re.match(r"---\n(.*?)\n---\n(.*)", read_file(path), re.S).groups()
        meta = dict(line.split(":", 1) for line in head.splitlines() if ":" in line)
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        agents[meta["name"]] = {"description": meta["description"], "prompt": body.strip(),
                                "tools": [t.strip() for t in meta.get("tools", "").split(",") if t.strip()]
                                         or ["read_file", "list_files", "search"],
                                "model": meta.get("model", MODEL)}
        print(f"subagent  {meta['name']}: {meta['description']}")
    return agents

AGENTS = {}
SPENT = {"tokens": 0}            # tokens used by ALL agents (main + helpers)
_lock = threading.Lock()

def delegate(agent, task):
    """Run a helper agent on its own, fresh conversation. Only its final report comes back."""
    a = AGENTS[agent]
    return run_agent(task, system=a["prompt"], tools=a["tools"], model=a["model"], who=agent)

def delegate_spec():
    names = ", ".join(f"{n} ({a['description']})" for n, a in AGENTS.items())
    return tool("delegate", "Hand a task to a helper agent. It starts with an empty conversation, "
                "so put everything it needs in the task. You get back only its report. "
                f"Helpers: {names}",
                agent="Helper name", task="The full task for the helper")

# ---------- 3. The loop (the same loop runs the main agent AND every helper) ----------
def run_agent(task, system=SYSTEM, tools=None, model=MODEL, who="main", max_turns=20):
    tools = tools or list(TOOLS)
    specs = [SPECS[t] for t in tools]
    if who == "main" and AGENTS:                                  # only the main agent can delegate
        specs.append(delegate_spec())
        system += "\n" + HELPERS
    pad = "" if who == "main" else "        "                     # helpers print indented
    messages = [{"role": "system", "content": system}, {"role": "user", "content": task}]
    for turn in range(1, max_turns + 1):
        try:
            response = client.chat.completions.create(model=model, messages=messages, tools=specs)
        except BadRequestError as e:                  # e.g. the model wrote broken JSON for a tool call
            print(f"\n{pad}[{who} turn {turn}] bad tool call, asking the model to try again")
            messages.append({"role": "user", "content": f"Your last tool call failed: {e.message}. Try again."})
            continue
        reply = response.choices[0].message
        with _lock:
            SPENT["tokens"] += response.usage.total_tokens
        print(f"\n{pad}[{who} turn {turn}] context: {response.usage.prompt_tokens:,} tokens")
        message = {"role": "assistant", "content": reply.content or ""}
        if reply.tool_calls:
            message["tool_calls"] = [c.model_dump() for c in reply.tool_calls]
        messages.append(message)
        if not reply.tool_calls:                                     # done: this text is the report
            print(f"{pad}[{who}] done\n")
            print("\n".join(pad + line for line in (reply.content or "").splitlines()))
            return reply.content or ""

        def call(c):
            name, args = c.function.name, json.loads(c.function.arguments or "{}")
            print(f"{pad}  {name} {json.dumps(args)[:150]}")
            try:
                return delegate(**args) if name == "delegate" else TOOLS[name](**args)
            except Exception as e:                                   # errors go back to the model
                return f"Error: {e}"
        if all(c.function.name == "delegate" for c in reply.tool_calls):
            results = list(ThreadPoolExecutor().map(call, reply.tool_calls))   # helpers run in parallel
        else:
            results = [call(c) for c in reply.tool_calls]
        for c, result in zip(reply.tool_calls, results):
            print(f"{pad}    -> {len(str(result)):,} characters back")
            messages.append({"role": "tool", "tool_call_id": c.id, "content": str(result)})
    return "Stopped: too many turns."

if __name__ == "__main__":
    AGENTS = load_agents()
    run_agent(" ".join(sys.argv[1:]))
    print(f"\nTokens used by all agents together: {SPENT['tokens']:,}")
