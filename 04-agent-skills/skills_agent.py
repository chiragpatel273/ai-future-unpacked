"""skills-agent: the tiny agent from video 2, plus Agent Skills support.

Skills are folders with a SKILL.md file in .agents/skills/. The agent sees each
skill's name and description, and loads the full instructions only when needed.
    pip install openai
    set API_KEY (and optionally BASE_URL and MODEL), then:
    python skills_agent.py "commit my staged changes"
Set NO_SKILLS=1 to run the same agent without skills.
"""
import json, os, subprocess, sys
from pathlib import Path
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url=os.environ.get("BASE_URL", "https://api.groq.com/openai/v1"),
)
MODEL = os.environ.get("MODEL", "openai/gpt-oss-120b")

SYSTEM = """You are a careful coding agent in the current folder.
Use the tools to read files and run commands. Make small edits.
After changing code, run the tests again.
When you are done, reply with a short summary."""

# ---------- 1. The tools: plain Python functions ----------
def read_file(path):
    with open(path) as f:
        return f.read()

def edit_file(path, old, new):
    text = read_file(path)
    if text.count(old) != 1:
        return "Error: 'old' must appear exactly once in the file."
    with open(path, "w") as f:
        f.write(text.replace(old, new))
    return f"Edited {path}."

def run_command(command):
    if input(f"\n  Run `{command}`? [y/N] ").strip().lower() != "y":
        return "The user declined to run this command."
    result = subprocess.run(command, shell=True, text=True,
                            capture_output=True, timeout=60)
    return (result.stdout + result.stderr)[-4000:] or "(no output)"

TOOLS = {"read_file": read_file, "edit_file": edit_file,
         "run_command": run_command}

# ---------- 2. The tool menu: what the model is told ----------
def tool(name, description, **params):
    props = {p: {"type": "string", "description": d}
             for p, d in params.items()}
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": props,
                       "required": list(params)}}}

TOOL_SPECS = [
    tool("read_file", "Read a text file and return its contents.",
         path="Path to the file"),
    tool("edit_file", "Replace one exact snippet of text in a file.",
         path="Path to the file",
         old="Exact text to replace (must appear once)",
         new="Replacement text"),
    tool("run_command", "Run a shell command, e.g. to run the tests.",
         command="The command to run"),
]

# ---------- 3. Skills: know-how, loaded only when needed ----------
def find_skills(root=".agents/skills"):
    skills = {}
    for skill_md in sorted(Path(root).glob("*/SKILL.md")):
        _, header, body = skill_md.read_text(encoding="utf-8").split("---", 2)
        meta = {}
        for line in header.splitlines():          # name: ..., description: ...
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
        skills[meta["name"]] = {"description": meta["description"],
                                "body": body.strip(), "dir": skill_md.parent}
    return skills

def activate_skill(skill):
    s = SKILLS[skill]
    files = [p.relative_to(s["dir"]).as_posix() for p in s["dir"].rglob("*")
             if p.is_file() and p.name != "SKILL.md"]
    return (f'<skill_content name="{skill}">\n{s["body"]}\n\n'
            f'Skill folder: {s["dir"].as_posix()}\n'
            f'Files: {", ".join(files) or "none"}\n</skill_content>')

SKILLS = {} if os.environ.get("NO_SKILLS") else find_skills()
if SKILLS:
    SYSTEM += ("\n\nSkills you can load. "
               "When a task matches one, call activate_skill first:\n")
    SYSTEM += "\n".join(f"- {n}: {s['description']}" for n, s in SKILLS.items())
    TOOLS["activate_skill"] = activate_skill
    spec = tool("activate_skill", "Load a skill's full instructions.",
                skill="The skill to load")
    spec["function"]["parameters"]["properties"]["skill"]["enum"] = list(SKILLS)
    TOOL_SPECS.append(spec)

# ---------- 4. The loop ----------
def run_agent(task, max_turns=20):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": task}]
    for turn in range(1, max_turns + 1):
        reply = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SPECS
        ).choices[0].message
        message = {"role": "assistant", "content": reply.content or ""}
        if reply.tool_calls:
            message["tool_calls"] = [c.model_dump() for c in reply.tool_calls]
        messages.append(message)

        if not reply.tool_calls:          # no tool requested: done
            print(f"\n[turn {turn}] done\n\n{reply.content}")
            return reply.content

        for call in reply.tool_calls:     # run every tool it asked for
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            print(f"\n[turn {turn}] {name} {args}")
            try:
                result = TOOLS[name](**args)
            except Exception as e:        # errors go back to the model
                result = f"Error: {e}"
            print("   ", str(result).strip()[:300])
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": str(result)})

    print("Stopped: too many turns.")

if __name__ == "__main__":
    print("Skills found:", ", ".join(SKILLS) or "none (skills off)")
    run_agent(" ".join(sys.argv[1:]) or input("Task: "))
