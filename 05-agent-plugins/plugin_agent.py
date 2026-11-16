"""plugin-agent: the tiny agent from our earlier videos, now loading an Agent Plugin.

An Agent Plugin (Agent Plugins 1.0) is one folder:
    plugin.json   who the plugin is          (required)
    skills/       Agent Skills, one per folder (optional)
    mcp.json      MCP servers to start         (optional)

    pip install openai "mcp>=2.3"
    set API_KEY (and optionally BASE_URL and MODEL), then:
    python plugin_agent.py path/to/plugin "commit my staged changes"
"""
import asyncio, contextlib, json, os, re, subprocess, sys
from pathlib import Path
from openai import OpenAI
from mcp import Client, StdioServerParameters

MODEL = os.environ.get("MODEL", "openai/gpt-oss-120b")

SYSTEM = """You are a careful coding agent in the current folder.
Use the tools to read files and run commands. Make small edits.
When you are done, reply with a short summary."""

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

# ---------- 2. Load the plugin (Agent Plugins 1.0) ----------
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
FIELDS = {"$schema", "name", "version", "description", "author", "homepage",
          "repository", "license", "keywords", "extensions"}
NAME_RULE = re.compile(r"^(?!.*(--|\.\.))[a-z0-9]([a-z0-9.-]{0,62}[a-z0-9])?$")

def load_plugin(folder):
    root = Path(folder).resolve()
    manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    if manifest.get("$schema") != SCHEMA:                 # pick rules by version
        sys.exit(f"Rejected: {root.name} is not an Agent Plugins 1.0 plugin.")
    if not NAME_RULE.match(str(manifest.get("name", ""))):
        sys.exit(f"Rejected: invalid plugin name {manifest.get('name')!r}.")
    name = manifest["name"]
    print(f"Plugin: {name} {manifest.get('version', '')}")
    for field in sorted(set(manifest) - FIELDS):         # unknown field: warn, go on
        print(f"  ! ignoring unknown field '{field}' in plugin.json")
    data = Path.home() / ".tiny-agent" / "plugin-data" / name   # survives updates
    data.mkdir(parents=True, exist_ok=True)
    skills = find_skills(root / "skills")
    servers = find_servers(root, data)
    return skills, servers

def find_skills(folder):
    skills = {}
    for skill_md in sorted(folder.glob("*/SKILL.md")):   # one level deep only
        try:
            _, header, body = skill_md.read_text(encoding="utf-8").split("---", 2)
            meta = dict(line.split(":", 1) for line in header.strip().splitlines() if ":" in line)
            meta = {k.strip(): v.strip() for k, v in meta.items()}
            skills[meta["name"]] = {"description": meta["description"],
                                    "body": body.strip(), "dir": skill_md.parent}
            print(f"  skill  {meta['name']}")
        except (ValueError, KeyError):                    # a bad skill is skipped
            print(f"  ! skipped invalid skill in {skill_md.parent.name}")
    return skills

def find_servers(root, data):
    file = root / "mcp.json"
    if not file.is_file():
        return {}                                         # no MCP servers: fine
    config = json.loads(file.read_text(encoding="utf-8"))
    if config.get("$schema") != MCP_SCHEMA:
        print("  ! mcp.json is for another version: MCP turned off, skills still load")
        return {}
    places = {"PLUGIN_ROOT": str(root), "PLUGIN_DATA": str(data)}
    expand = lambda text: re.sub(r"\$\{(PLUGIN_ROOT|PLUGIN_DATA)\}", lambda m: places[m[1]], text)
    servers = {}
    for name, s in config.get("mcpServers", {}).items():
        if s.get("type") != "stdio":                      # this demo speaks stdio only
            print(f"  ! skipped server '{name}': transport {s.get('type')!r} not supported here")
            continue
        command = s["command"]
        if command.startswith("./"):                      # bundled program, inside the plugin
            path = (root / command).resolve()
            if root not in path.parents:
                print(f"  ! skipped server '{name}': command leaves the plugin folder")
                continue
            command = str(path)
        elif "/" in command or "\\" in command:          # otherwise: a plain program name
            print(f"  ! skipped server '{name}': command must be a name or start with ./")
            continue
        servers[name] = StdioServerParameters(
            command=command,
            args=[expand(a) for a in s.get("args", [])],
            env={**os.environ, **{k: expand(v) for k, v in s.get("env", {}).items()}, **places},
            cwd=expand(s.get("cwd", "${PLUGIN_ROOT}")))
        print(f"  server {name} (stdio)")
    return servers

# ---------- 3. Skills: names up front, full instructions on demand ----------
def add_skills(skills):
    global SYSTEM
    if not skills:
        return
    SYSTEM += "\n\nSkills you can load. When a task matches one, call activate_skill first:\n"
    SYSTEM += "\n".join(f"- {n}: {s['description']}" for n, s in skills.items())
    def activate_skill(skill):
        s = skills[skill]
        return (f'<skill_content name="{skill}">\n{s["body"]}\n\n'
                f'Skill folder: {s["dir"].as_posix()}\n</skill_content>')
    TOOLS["activate_skill"] = activate_skill
    spec = tool("activate_skill", "Load a skill's full instructions.", skill="The skill to load")
    spec["function"]["parameters"]["properties"]["skill"]["enum"] = list(skills)
    TOOL_SPECS.append(spec)

# ---------- 4. MCP servers: start them, add their tools ----------
async def connect(servers, stack):
    for name, params in servers.items():
        try:
            session = await stack.enter_async_context(Client(params))
            tools = (await session.list_tools()).tools
        except Exception as e:                            # one broken server is skipped
            print(f"  ! server '{name}' failed to start: {e}")
            continue
        for t in tools:
            TOOLS[t.name] = (session, t.name)
            TOOL_SPECS.append({"type": "function", "function": {
                "name": t.name, "description": t.description, "parameters": t.input_schema}})
        print(f"  server {name} connected: {', '.join(t.name for t in tools)}")

async def call(name, args):
    target = TOOLS[name]
    if isinstance(target, tuple):                         # a tool from an MCP server
        session, tool_name = target
        result = await session.call_tool(tool_name, args)
        return "\n".join(c.text for c in result.content if c.type == "text")
    return target(**args)                                 # a built-in tool or skill

# ---------- 5. The loop (same as always) ----------
async def run_agent(task, max_turns=20):
    client = OpenAI(api_key=os.environ["API_KEY"],
                    base_url=os.environ.get("BASE_URL", "https://api.groq.com/openai/v1"),
                    max_retries=6)               # free plans rate-limit: wait and retry
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": task}]
    for turn in range(1, max_turns + 1):
        reply = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SPECS).choices[0].message
        message = {"role": "assistant", "content": reply.content or ""}
        if reply.tool_calls:
            message["tool_calls"] = [c.model_dump() for c in reply.tool_calls]
        messages.append(message)
        if not reply.tool_calls:
            print(f"\n[turn {turn}] done\n\n{reply.content}")
            return reply.content
        for c in reply.tool_calls:
            args = json.loads(c.function.arguments or "{}")
            print(f"\n[turn {turn}] {c.function.name} {args}")
            try:
                result = await call(c.function.name, args)
            except Exception as e:                        # errors go back to the model
                result = f"Error: {e}"
            print("   ", str(result).strip()[:300])
            messages.append({"role": "tool", "tool_call_id": c.id, "content": str(result)})
    print("Stopped: too many turns.")

async def main(folder, task):
    skills, servers = load_plugin(folder)
    add_skills(skills)
    async with contextlib.AsyncExitStack() as stack:
        await connect(servers, stack)
        if task:
            await run_agent(task)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], " ".join(sys.argv[2:])))
