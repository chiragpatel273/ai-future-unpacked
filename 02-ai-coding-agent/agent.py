"""tiny-agent: an AI coding agent in under 100 lines of Python.

Works with any OpenAI-compatible API (Groq, OpenAI, OpenRouter, Ollama...).
    pip install openai
    set API_KEY (and optionally BASE_URL and MODEL), then:
    python agent.py "fix the failing test"
"""
import json, os, subprocess, sys
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

# ---------- 3. The loop ----------
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
    run_agent(" ".join(sys.argv[1:]) or input("Task: "))
