"""notes-server: a tiny MCP server that gives any AI agent a notebook."""
from pathlib import Path
from mcp.server import MCPServer

NOTES = Path(__file__).with_name("notes.md")
mcp = MCPServer("notes")


@mcp.tool()
def add_note(text: str) -> str:
    """Save a short note for later."""
    with NOTES.open("a", encoding="utf-8") as f:
        f.write(f"- {text}\n")
    return "Saved."


@mcp.tool()
def search_notes(query: str) -> str:
    """Find saved notes that contain the query (not case-sensitive)."""
    if not NOTES.exists():
        return "No notes yet."
    lines = NOTES.read_text(encoding="utf-8").splitlines()
    hits = [line for line in lines if query.lower() in line.lower()]
    return "\n".join(hits) or "No matching notes."


@mcp.resource("notes://all")
def all_notes() -> str:
    """Every saved note."""
    return NOTES.read_text(encoding="utf-8") if NOTES.exists() else ""


if __name__ == "__main__":
    mcp.run()  # talks over stdin/stdout by default
