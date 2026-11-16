"""PostToolUse hook: writes every edit and command to .agent/tool-log.txt. It can't undo anything."""
import json, sys, datetime

call = json.load(sys.stdin)
with open(".agent/tool-log.txt", "a", encoding="utf-8") as log:
    log.write(f"{datetime.datetime.now():%H:%M:%S}  {call['tool_name']}  {json.dumps(call['tool_input'])[:120]}\n")
