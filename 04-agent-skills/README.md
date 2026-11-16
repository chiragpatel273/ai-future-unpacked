# Agent Skills Explained (video 4)

**What it is:** the agent from video 2, plus **Agent Skills** support in about 30 lines, and an example
skill that teaches it your team's commit-message rules. A skill is a folder with a `SKILL.md` file. The agent
sees each skill's name and description, and loads the full instructions only when a task needs them.
Video: [Agent Skills Explained](https://youtu.be/2A747iHL86U)

## Run it
The demo builds a small git repo with one staged change, then runs the agent twice: first **without**
skills, then **with** the commit-message skill, so you can compare.

- **Windows:** double-click `run-demo.bat`
- **Mac / Linux / WSL:** `bash run-demo.sh`

Paste your Groq key when asked (hidden, not saved) and type `y` when it asks to run a command.

By hand, from inside your own project (skills go in `.agents/skills/`):
```bash
pip install openai
export API_KEY="your-groq-key"          # PowerShell: $env:API_KEY = "your-groq-key"
python path/to/skills_agent.py "Commit my staged changes."
```
Set `NO_SKILLS=1` to run the same agent without skills.

## What you'll see
Without the skill, you get a generic message like "Update cart functionality". With it, the agent loads
the skill, finds the ticket ID in the branch name, checks its message with the skill's script, and commits
`feat(cart): ...` with a reason and `Refs: PAY-142`. Both logs are saved as `run-without-skills.txt` and
`run-with-skills.txt`.

## Files
```text
skills_agent.py                                  the agent (skills code is section 3)
skills/commit-message/SKILL.md                   the skill: our team's commit rules
skills/commit-message/scripts/check_message.py   the checker the skill runs
run-demo.bat / run-demo.ps1 / run-demo.sh        the demo
```

## Use the same skill in other tools
The skill follows the open Agent Skills format (agentskills.io), so the same folder works in other
skills-compatible tools. In Claude Code, put it in `.claude/skills/`; other tools document which folder they
read (many read `.agents/skills/`). Only install skills you trust: they are instructions and code your
agent will follow.
