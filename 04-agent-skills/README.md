# skills-agent (AI Future Unpacked, video 4)

The tiny agent from video 2, plus **Agent Skills** support in about 30 lines.
A skill is a folder with a `SKILL.md` file. The agent sees each skill's name and description,
and loads the full instructions only when a task needs them (progressive disclosure).

```
skills_agent.py                     # the agent (skills code is section 3)
skills/commit-message/SKILL.md      # an example skill: our team's commit rules
skills/commit-message/scripts/check_message.py
```

## Try it
Put skills in your project under `.agents/skills/`, then run the agent from the project folder:
```powershell
pip install openai
$env:API_KEY = "your-groq-key"      # free key from console.groq.com
python path\to\skills_agent.py "Commit my staged changes."
```
Set `NO_SKILLS=1` to run the same agent without skills and compare.
On Windows, `run-demo.bat` builds a small demo repo and runs both versions for you.

## Use the same skill in other tools
The skill follows the open Agent Skills format (agentskills.io), so the same folder works in other
skills-compatible tools. In Claude Code, put it in `.claude/skills/`; for other tools, check their docs
for the skills folder they read (many read `.agents/skills/`).
Only install skills you trust: they are instructions and code your agent will follow.
