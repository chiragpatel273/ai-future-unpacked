"""Stop hook: the agent wants to finish. If it changed code, the tests must pass. Exit 2 = keep working."""
import subprocess, sys

changed = subprocess.run(["git", "status", "--porcelain", "--", "*.py"],
                         capture_output=True, text=True).stdout
if not changed.strip():
    sys.exit(0)                                   # no code changed: nothing to check

result = subprocess.run([sys.executable, "-m", "unittest", "-q"],
                        capture_output=True, text=True)
if result.returncode != 0:
    print("The tests fail. Fix them before you finish:\n"
          + result.stderr[-1500:], file=sys.stderr)
    sys.exit(2)
sys.exit(0)
