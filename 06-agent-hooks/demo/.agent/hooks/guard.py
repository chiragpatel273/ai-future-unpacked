"""PreToolUse hook: runs before read_file and run_command. Exit 2 blocks the call."""
import json, re, sys

SECRETS = r"(^|[\\/\s\"'])\.env\b"                      # .env, ./.env, "type .env" ...
DELETES = r"\brm\s+-\w*[rf]\w*[rf]|Remove-Item\b.*-Recurse|\brmdir\s+/s"

call = json.load(sys.stdin)                       # the app sends the tool call as JSON
name, args = call["tool_name"], call["tool_input"]
text = args.get("path", "") if name == "read_file" else args.get("command", "")

if re.search(SECRETS, text):
    print(".env holds secrets, so it is off-limits. "
          "Ask the user for the value you need.", file=sys.stderr)
    sys.exit(2)
if name == "run_command" and re.search(DELETES, text, re.I):
    print("Recursive deletes are blocked. "
          "Delete specific files, or ask the user.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)                                       # anything else: carry on
