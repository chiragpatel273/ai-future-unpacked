"""mcp-agent: the tiny agent from video 2, now plugged into an MCP server.

The agent no longer has its own tools. It asks the MCP server what tools exist,
shows them to the model, and lets the server run whatever the model picks.
    pip install openai "mcp>=2.3"
    set API_KEY (and optionally BASE_URL, MODEL), then:
    python mcp_agent.py "remember the client demo is on Friday at 3pm"
"""
import asyncio, json, os, sys
from openai import OpenAI
from mcp import Client, StdioServerParameters

llm = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url=os.environ.get("BASE_URL", "https://api.groq.com/openai/v1"),
)
MODEL = os.environ.get("MODEL", "openai/gpt-oss-120b")

# Any MCP server works here. This one starts notes_server.py and talks over stdio.
SERVER = StdioServerParameters(command=sys.executable, args=["notes_server.py"])

SYSTEM = """You are a helpful assistant with access to tools.
Use them when they help. When you are done, reply with a short answer."""


async def run_agent(task, max_turns=10):
    async with Client(SERVER) as mcp:
        # 1. Ask the server for its tools, and turn them into the model's tool menu
        tools = (await mcp.list_tools()).tools
        menu = [{"type": "function", "function": {
                    "name": t.name, "description": t.description,
                    "parameters": t.input_schema}} for t in tools]
        print("Tools from the MCP server:", ", ".join(t.name for t in tools))

        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": task}]
        for turn in range(1, max_turns + 1):
            reply = llm.chat.completions.create(
                model=MODEL, messages=messages, tools=menu
            ).choices[0].message
            message = {"role": "assistant", "content": reply.content or ""}
            if reply.tool_calls:
                message["tool_calls"] = [c.model_dump() for c in reply.tool_calls]
            messages.append(message)

            if not reply.tool_calls:          # no tool requested: done
                print(f"\n[turn {turn}] done\n\n{reply.content}")
                return reply.content

            for call in reply.tool_calls:     # 2. the MCP server runs each tool
                args = json.loads(call.function.arguments or "{}")
                print(f"\n[turn {turn}] {call.function.name} {args}")
                result = await mcp.call_tool(call.function.name, args)
                text = "\n".join(c.text for c in result.content if c.type == "text")
                print("   ", text[:300])
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": text})
        print("Stopped: too many turns.")


if __name__ == "__main__":
    asyncio.run(run_agent(" ".join(sys.argv[1:]) or input("Task: ")))
