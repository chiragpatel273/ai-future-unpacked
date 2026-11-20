"""Measures where Claude Code's tokens go, on a real open-source project, 3 times each.

Project: more-itertools v10.7.0 (downloaded once from GitHub into project/).
Every run is `claude -p ... --output-format json`, which reports the tokens it used.
Uses your Claude Code login. Results go to results/ (one JSON per run + results.tsv).
If it stops part-way, run it again: finished runs are skipped.

    python3 cc_tests.py                 (or double-click run-tests.bat to run it inside WSL)
    CC_REPEATS=1 python3 cc_tests.py    (a quicker, single-run version)
"""
import io, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
PROJECT = os.path.join(HERE, "project")
WORK = os.environ.get("CC_WORK", os.path.join(tempfile.gettempdir(), "cc-tests-work"))   # fast local disk
TAG = "v10.7.0"
ZIP_URL = f"https://codeload.github.com/more-itertools/more-itertools/zip/refs/tags/{TAG}"
REPEATS = int(os.environ.get("CC_REPEATS", "3"))
PY = "python" if os.name == "nt" else "python3"
TEST_CMD = f"{PY} -m unittest -v"
QUIET_CMD = f"{PY} .claude/quiet_tests.py"
ALLOWED = f"Read,Grep,Glob,Bash({TEST_CMD}),Bash({PY} -m unittest *),Bash({QUIET_CMD})"

QUICK = ("One quick question: what does more_itertools.chunked do with the leftover items "
         "when they don't fill a whole chunk?")
LONG = [
    "Explain how windowed works in more_itertools/more.py, including the fillvalue and step arguments. Read the code you need.",
    "How is the package organised? Which kinds of functions live in more.py and which in recipes.py?",
    "Explain how peekable lets you look ahead and push items back.",
    "Which functions in recipes.py also appear as recipes in the Python itertools docs? List five, one line each.",
    QUICK,
]
VAGUE = "Improve the error handling in this project. Do not change any files; reply with a short list."
SPECIFIC = ("In more_itertools/more.py, does chunked raise an error when n is 0? "
            "Do not change any files; reply in two sentences.")
TESTS = (f"Run the test suite with: {TEST_CMD} . Tell me how many tests ran and whether any failed, "
         "in two sentences. Do not change any files.")
FIRST = "What does more_itertools.first do when the iterable is empty and no default is given? One sentence."

# (label, prompts, setup, folder) - folder "same:<label>" reuses that run's folder in a new session
SONNET = [
    ("quick-question", [QUICK], None, None),
    ("long-session", LONG, None, None),
    ("fresh-after-long", [QUICK], None, "same:long-session"),
    ("vague-prompt", [VAGUE], None, None),
    ("specific-prompt", [SPECIFIC], None, None),
    ("tests-raw", [TESTS], None, None),
    ("tests-hook", [TESTS], "hook", None),
    ("claude-md-big", [FIRST], "big", None),
    ("claude-md-lean", [FIRST], "lean", None),
]
OPUS = [
    ("quick-question", [QUICK], None, None),
    ("vague-prompt", [VAGUE], None, None),
    ("specific-prompt", [SPECIFIC], None, None),
    ("tests-raw", [TESTS], None, None),
]

QUIET = r'''"""Runs the tests, but prints only what isn't a passing test (failures, errors, the summary)."""
import subprocess, sys
r = subprocess.run([sys.executable, "-m", "unittest", "-v"], capture_output=True, text=True)
for line in (r.stdout + r.stderr).splitlines():
    if not line.rstrip().endswith("... ok"):
        print(line)
sys.exit(r.returncode)
'''
HOOK = r'''import json, sys
data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "").strip()
if cmd.replace("python3", "python") == "python -m unittest -v":
    data["tool_input"]["command"] = cmd.split()[0] + " .claude/quiet_tests.py"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "updatedInput": data["tool_input"]}}))
else:
    print("{}")
'''


def find_claude():
    found = shutil.which("claude") or shutil.which("claude.cmd") or shutil.which("claude.exe")
    if found:
        return found
    home = os.path.expanduser("~")
    for p in [os.path.join(home, ".local", "bin", "claude.exe"),
              os.path.join(os.environ.get("APPDATA", ""), "npm", "claude.cmd")]:
        if os.path.isfile(p):
            return p
    return None


CLAUDE = find_claude()


def get_project():
    if os.path.isdir(os.path.join(PROJECT, "more_itertools")):
        return
    print(f"Downloading more-itertools {TAG} ...", flush=True)
    data = urllib.request.urlopen(ZIP_URL, timeout=120).read()
    tmp = PROJECT + "-tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    zipfile.ZipFile(io.BytesIO(data)).extractall(tmp)
    inner = os.path.join(tmp, os.listdir(tmp)[0])
    shutil.move(inner, PROJECT)
    shutil.rmtree(tmp, ignore_errors=True)


def setup(work, kind):
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(PROJECT, work)
    if kind in ("big", "lean"):
        shutil.copy(os.path.join(HERE, "instructions", f"CLAUDE-{kind}.md"), os.path.join(work, "CLAUDE.md"))
    if kind == "hook":
        d = os.path.join(work, ".claude")
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "quiet_tests.py"), "w", encoding="utf-8").write(QUIET)
        hook_py = os.path.join(d, "filter_tests.py")
        open(hook_py, "w", encoding="utf-8").write(HOOK)
        settings = {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [
            {"type": "command", "command": f'"{sys.executable}" "{hook_py}"'}]}]}}
        json.dump(settings, open(os.path.join(d, "settings.json"), "w"), indent=2)


def claude(work, prompt, model, cont):
    cmd = [CLAUDE, "-p", prompt, "--output-format", "json", "--model", model, "--allowedTools", ALLOWED]
    if cont:
        cmd.append("--continue")
    t0 = time.time()
    p = subprocess.run(cmd, cwd=work, text=True, capture_output=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=900)
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        data = {"error": "no JSON", "stdout": p.stdout[-2000:], "stderr": p.stderr[-2000:]}
    data["_seconds"] = round(time.time() - t0, 1)
    return data


def row(model, label, rep, i, r, cost):
    u = r.get("usage") or {}
    it = (u.get("iterations") or [{}])[-1]
    read = sum(u.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    last = sum(it.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return [model, label, rep, i + 1, r.get("num_turns"), u.get("input_tokens", 0), u.get("cache_creation_input_tokens", 0),
            u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0), read, last, r.get("_seconds"),
            round(cost, 4), r.get("is_error")]


def measure_test_output():
    """How big the test output is, raw and filtered (saved once)."""
    path = os.path.join(OUT, "test-output-size.txt")
    if os.path.exists(path):
        return
    work = os.path.join(WORK, "measure")
    setup(work, "hook")
    raw = subprocess.run([sys.executable, "-m", "unittest", "-v"], cwd=work, capture_output=True, text=True)
    quiet = subprocess.run([sys.executable, ".claude/quiet_tests.py"], cwd=work, capture_output=True, text=True)
    raw_txt = raw.stdout + raw.stderr; quiet_txt = quiet.stdout + quiet.stderr
    open(path, "w", encoding="utf-8").write(
        f"raw: {len(raw_txt)} characters, {len(raw_txt.splitlines())} lines\n"
        f"filtered: {len(quiet_txt)} characters, {len(quiet_txt.splitlines())} lines\n"
        f"--- filtered output ---\n{quiet_txt}")
    print(open(path, encoding="utf-8").read().split("--- filtered")[0], flush=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(OUT, "console.txt"), "a", encoding="utf-8")
    def say(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True); log.write(s + "\n"); log.flush()
    if not CLAUDE:
        say("Claude Code (claude) was not found here.")
        return 3
    ver = subprocess.run([CLAUDE, "--version"], capture_output=True, text=True).stdout.strip()
    say(f"\n=== {time.strftime('%Y-%m-%d %H:%M')}  claude: {CLAUDE}  version: {ver}  repeats: {REPEATS}")
    get_project()
    if not os.environ.get("CC_SKIP_MEASURE"):
        measure_test_output()
    plan = [(m, e) for rep in range(1, REPEATS + 1) for m, exps in (("sonnet", SONNET), ("opus", OPUS))
            for e in exps]
    done_runs = 0
    for rep in range(1, REPEATS + 1):
        for model, exps in (("sonnet", SONNET), ("opus", OPUS)):
            for label, prompts, kind, folder in exps:
                done_runs += 1
                out = os.path.join(OUT, model, f"{label}-r{rep}.json")
                if os.path.exists(out):
                    continue
                os.makedirs(os.path.dirname(out), exist_ok=True)
                if folder:
                    work = os.path.join(WORK, model, f"{folder.split(':')[1]}-r{rep}")
                else:
                    work = os.path.join(WORK, model, f"{label}-r{rep}")
                    setup(work, kind)
                say(f"[{done_runs}/{len(plan)}] {model} {label} run {rep}")
                results, prev = [], 0.0
                for i, prompt in enumerate(prompts):
                    r = claude(work, prompt, model, cont=i > 0)
                    if "not logged in" in str(r.get("result", "")).lower():
                        say(f"This Claude Code ({CLAUDE}) is not logged in.")
                        return 3
                    cost = (r.get("total_cost_usd") or 0) - prev
                    prev = r.get("total_cost_usd") or 0
                    results.append({"prompt": prompt, "row": row(model, label, rep, i, r, cost), "result": r})
                    rw = results[-1]["row"]
                    say(f"    prompt {i + 1}: {rw[4]} requests, {rw[9]:,} tokens read, {rw[8]:,} output, {rw[11]} s")
                if rep == 1 and kind in ("big", "lean") and model == "sonnet":
                    c = subprocess.run([CLAUDE, "-p", "/context", "--model", model], cwd=work, text=True,
                                       capture_output=True, encoding="utf-8", errors="replace",
                                       stdin=subprocess.DEVNULL, timeout=300)
                    open(os.path.join(OUT, f"context-{label}.txt"), "w", encoding="utf-8").write(c.stdout + c.stderr)
                json.dump(results, open(out, "w", encoding="utf-8"), indent=2)
    # one table of everything
    with open(os.path.join(OUT, "results.tsv"), "w", encoding="utf-8") as f:
        f.write("model\texperiment\trepeat\tprompt\trequests\tinput\tcache_write\tcache_read\toutput\t"
                "tokens_read\tlast_request\tseconds\tapi_price_usd\terror\n")
        for model in ("sonnet", "opus"):
            d = os.path.join(OUT, model)
            for name in sorted(os.listdir(d)):
                for x in json.load(open(os.path.join(d, name), encoding="utf-8")):
                    f.write("\t".join(str(v) for v in x["row"]) + "\n")
    shutil.rmtree(WORK, ignore_errors=True)
    say("\nDone. Results in results/results.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
