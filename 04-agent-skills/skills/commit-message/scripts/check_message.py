"""Checks a commit message against our team's rules. Prints OK or the problems."""
import re, sys

TYPES = ("feat", "fix", "refactor", "docs", "test", "chore")

def check(subject, why, footer):
    problems = []
    m = re.fullmatch(r"(\w+)\(([\w./-]+)\): (.+)", subject)
    if not m:
        problems.append('subject must look like "type(scope): summary"')
    else:
        kind, _, summary = m.groups()
        if kind not in TYPES:
            problems.append(f"type must be one of: {', '.join(TYPES)}")
        if len(summary) > 60:
            problems.append(f"summary is {len(summary)} characters (max 60)")
        if summary.endswith("."):
            problems.append("summary must not end with a full stop")
        if summary.split()[0].lower().endswith("ed"):
            problems.append('use the imperative: "cap", not "capped"')
    if len(why.split()) < 4:
        problems.append("add one sentence explaining why")
    if not re.fullmatch(r"Refs: [A-Z]+-\d+", footer):
        problems.append('footer must be "Refs: TICKET-123"')
    return problems

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit('usage: check_message.py "<subject>" "<why>" "<footer>"')
    problems = check(*sys.argv[1:])
    print("OK" if not problems else "\n".join("- " + p for p in problems))
