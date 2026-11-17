"""code-mode-agent: the tiny agent from our earlier videos, with a Code Mode switch.

Normal mode: the model asks for one tool call at a time (read_file, search, ...).
Every result goes back into its conversation, and the whole conversation is sent
again on the next turn.

Code Mode: the model gets ONE tool, run_code. It writes a short Python script that
calls our tools as normal functions, loops, filters, and prints only what it needs.
Only the printed output goes back into the conversation.

    pip install openai
    set API_KEY (and optionally BASE_URL and MODEL), then, inside your project:
    python path/to/code_mode_agent.py "list the broken links in the docs"
    set CODE_MODE=1 to turn Code Mode on.

WARNING: this is a teaching version. run_code runs Python on your computer in a
separate process with a time limit. It is NOT a sandbox: the code can do anything
Python can. Real tools run the code in an isolated sandbox (Cloudflare) or check
every tool call in it against your permission rules (Claude Code).
"""
import glob, json, os, re, subprocess, sys, tempfile
from openai import OpenAI, BadRequestError, APIStatusError

MODEL = os.environ.get("MODEL", "openai/gpt-oss-120b")
CODE_MODE = os.environ.get("CODE_MODE") == "1"
HERE = os.path.dirname(os.path.abspath(__file__))
client = OpenAI(api_key=os.environ.get("API_KEY", "none"),
                base_url=os.environ.get("BASE_URL", "https://api.groq.com/openai/v1"),
                max_retries=8)                   # free plans rate-limit: wait and retry

SYSTEM = """You are a careful coding agent in the current folder.
Use the tools to read files and run commands. Make small edits.
When you are done, reply with a short summary."""
SYSTEM += "\nCommands run in " + ("Windows cmd." if os.name == "nt" else "bash.")

# ---------- 1. Tools (the same tools as before) ----------
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

def edit_file(path, old, new, **_):
    text = read_file(path)
    if text.count(old) != 1:
        return "Error: 'old' must appear exactly once in the file."
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))
    return f"Edited {path}."

def file_exists(path, **_):
    return "yes" if os.path.exists(path) else "no"

def run_command(command):
    if input(f"\n  Run `{command}`? [y/N] ").strip().lower() != "y":
        return "The user declined to run this command."
    result = subprocess.run(command, shell=True, text=True, capture_output=True,
                            timeout=60, encoding="utf-8", errors="replace")
    return (result.stdout + result.stderr)[-4000:] or "(no output)"

TOOLS = {"read_file": read_file, "list_files": list_files, "search": search,
         "file_exists": file_exists, "edit_file": edit_file, "run_command": run_command}

def tool(name, description, **params):
    props = {p: {"type": "string", "description": d} for p, d in params.items()}
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": props, "required": list(params)}}}

SPECS = [
    tool("read_file", "Read a text file and return its contents.", path="Path to the file"),
    tool("list_files", "List every file in a folder.", folder="Folder, e.g. ."),
    tool("search", "Find lines matching a regex in all files.", pattern="Regex", folder="Folder, e.g. ."),
    tool("file_exists", "Check if a file exists. Returns yes or no.", path="Path to the file"),
    tool("edit_file", "Replace one exact snippet of text in a file.", path="Path to the file",
         old="Exact text to replace (must appear once)", new="Replacement text"),
    tool("run_command", "Run a shell command.", command="The command to run"),
]

# ---------- 2. Code Mode: one tool that runs the model's code ----------
CODE_TOOLS = ["read_file", "list_files", "search", "file_exists", "edit_file"]   # no shell inside code

RUN_CODE = tool("run_code",
    "Run a Python script. Inside it you can call these functions directly, they return strings:\n"
    "  read_file(path)        -> the file's text\n"
    "  list_files(folder)     -> one path per line\n"
    "  search(pattern, folder) -> matching lines as path:line: text\n"
    "  file_exists(path)      -> 'yes' or 'no'\n"
    "  edit_file(path, old, new) -> replace one exact snippet\n"
    "The Python standard library is available. Use loops and ifs. "
    "Only what you print() comes back to you, so print just the result you need.",
    code="The Python script")

CODE_HINT = """You have one tool, run_code. Do the work by writing a Python script that calls
the functions, loops over the data and prints only the final result.
Work with files only through the functions read_file, list_files, search, file_exists, edit_file.
Keep each script short (under 40 lines) and end it with print()."""

def run_code(code, **_):
    """Run the model's script in a new Python process. Return what it printed."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
    try:
        r = subprocess.run([sys.executable, __file__, "--child", f.name], text=True,
                           capture_output=True, timeout=60, encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return "Error: the code ran longer than 60 seconds and was stopped."
    finally:
        os.remove(f.name)
    out, calls = r.stdout, 0
    m = re.search(r"\n?__TOOL_CALLS__ (\d+)\s*$", out)
    if m:
        out, calls = out[:m.start()], int(m.group(1))
    STATS["inner_calls"] += calls
    print(f"    ({calls} tool calls ran inside the code)")
    return (out + r.stderr)[-4000:] or "(the code printed nothing)"

def child(path):
    """Runs inside the new process: our tools become plain functions, then the script runs."""
    counter = {"n": 0}
    def counted(fn):
        def wrapper(*a, **k):
            counter["n"] += 1
            return fn(*a, **k)
        return wrapper
    env = {name: counted(TOOLS[name]) for name in CODE_TOOLS}
    try:
        exec(compile(open(path, encoding="utf-8").read(), "your_code.py", "exec"), env)
    finally:
        print(f"\n__TOOL_CALLS__ {counter['n']}")

# ---------- 3. The loop ----------
STATS = {"turns": 0, "calls": 0, "inner_calls": 0, "biggest": 0, "total": 0}

def run_agent(task, max_turns=30):
    specs, system = (SPECS, SYSTEM) if not CODE_MODE else ([RUN_CODE], SYSTEM + "\n" + CODE_HINT)
    messages = [{"role": "system", "content": system}, {"role": "user", "content": task}]
    for turn in range(1, max_turns + 1):
        try:
            response = client.chat.completions.create(model=MODEL, messages=messages, tools=specs)
        except BadRequestError as e:                  # e.g. the model wrote broken JSON for a tool call
            print(f"\n[turn {turn}] bad tool call, asking the model to try again")
            messages.append({"role": "user", "content": f"Your last tool call failed: {e.message}. Try again."})
            continue
        except APIStatusError as e:                   # e.g. the request is bigger than the plan allows
            size = re.search(r"Requested (\d+)", str(e.message))
            print(f"\n[turn {turn}] STOPPED: the provider refused this request ({e.status_code}).")
            if size:
                print(f"  This request needed {int(size.group(1)):,} tokens. That is more than your plan allows.")
            print("  " + str(e.message)[:200])
            return "Stopped: request refused."
        reply, used = response.choices[0].message, response.usage
        STATS["turns"] += 1
        STATS["total"] += used.total_tokens
        STATS["biggest"] = max(STATS["biggest"], used.prompt_tokens)
        print(f"\n[turn {turn}] context: {used.prompt_tokens:,} tokens")
        message = {"role": "assistant", "content": reply.content or ""}
        if reply.tool_calls:
            message["tool_calls"] = [c.model_dump() for c in reply.tool_calls]
        messages.append(message)
        if not reply.tool_calls:                                     # done
            print("[done]\n\n" + (reply.content or ""))
            return reply.content or ""
        for c in reply.tool_calls:
            name = c.function.name
            STATS["calls"] += 1
            try:
                args = json.loads(c.function.arguments or "{}")
                if name == "run_code":
                    print("  run_code:")
                    print("\n".join("    | " + line for line in args.get("code", "").splitlines()))
                    result = run_code(**args)
                else:
                    print(f"  {name} {json.dumps(args)[:150]}")
                    result = TOOLS[name](**args)
            except Exception as e:                                   # errors go back to the model
                result = f"Error: {e}"
            print(f"    -> {len(str(result)):,} characters back")
            messages.append({"role": "tool", "tool_call_id": c.id, "content": str(result)})
    return "Stopped: too many turns."

if __name__ == "__main__":
    if sys.argv[1:2] == ["--child"]:
        child(sys.argv[2])
        sys.exit()
    print(f"Code Mode: {'ON' if CODE_MODE else 'off'}   model: {MODEL}")
    run_agent(" ".join(sys.argv[1:]))
    inner = f" (+{STATS['inner_calls']} inside the code)" if CODE_MODE else ""
    print(f"\nModel turns: {STATS['turns']}   tool calls: {STATS['calls']}{inner}")
    print(f"Biggest context: {STATS['biggest']:,} tokens   Tokens used in total: {STATS['total']:,}")
