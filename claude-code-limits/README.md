# Why Claude Code hits your limit so fast (I ran 51 tests)

Code and raw logs for the video **[Why Claude Code Hits Your Limit So Fast (I Ran 51 Tests)](https://youtu.be/mvpItwNsG0I)**.

`cc_tests.py` runs real Claude Code sessions on a real open-source project, [more-itertools](https://github.com/more-itertools/more-itertools) v10.7.0, and records how many tokens each one used. Every run is `claude -p ... --output-format json`, which reports the tokens per request. Each test runs 3 times.

| Test | What it compares |
|---|---|
| quick question | a one-line question in a new session |
| long session | 5 questions in one session, then the same last question in a new session |
| vague vs specific | "Improve the error handling in this project" vs a question about one function |
| Opus | the quick, vague, specific and test prompts on Opus |
| noisy output | `python3 -m unittest -v` raw vs a PreToolUse hook that filters the output |
| CLAUDE.md | a 107-line CLAUDE.md vs a 7-line one (plus `/context` for each) |

## Run it

You need Claude Code installed and logged in, and Python 3.9+. It uses your own plan or API key: 39 Sonnet and 12 Opus prompts, about 20-30 minutes. It downloads more-itertools once from GitHub.

```bash
python3 cc_tests.py                  # macOS, Linux or WSL
CC_REPEATS=1 python3 cc_tests.py     # quicker: each test once
```

On Windows with `claude` on your PATH, use `python cc_tests.py`. If Claude Code is installed inside WSL, double-click `run-tests.bat`: it runs the script inside WSL.

If it stops part-way, run it again: finished runs are skipped. Results go to `results/`: one JSON per run, `results.tsv`, `console.txt`, the `/context` reports and the test-output sizes.

## How to read the numbers

- **tokens_read**: input + cache write + cache read, added up over every request that prompt needed.
- **last_request**: the size of the last request, from `usage.iterations`.
- **api_price_usd**: Claude Code's own list-price estimate (`total_cost_usd`). With `--continue` it is a running total, so the script subtracts the previous value. On a Pro or Max plan you don't pay this, and Anthropic doesn't publish exactly how tokens map to plan limits.

## My results (18 Nov 2026, Claude Code 2.1.326, Max plan)

Raw logs: `sample-results/` (local paths and my list of installed skills removed). Values are run 1 / run 2 / run 3.

| Test | Result |
|---|---|
| quick question, new session (Sonnet) | 1 request; 29,806 / 27,173 / 27,173 tokens; 0 files read |
| long session: size of each request after Q1 → Q5 (median) | 33,623 → 40,056 → 46,734 → 49,127 → 54,258 |
| same last question: end of long session vs new session | 108,085 / 104,287 / 49,471 vs 27,171 × 3 tokens; API price $0.026 / $0.038 / $0.008 vs $0.053 / $0.054 / $0.053 |
| vague prompt (Sonnet) | 7 / 5 / 6 requests; 167,908 / 126,883 / 167,418 tokens; output 1,733 / 1,478 / 1,469 |
| specific prompt (Sonnet) | 2 / 2 / 2 requests; 58,368 / 59,672 / 57,886 tokens; output 322 / 413 / 372 |
| vague prompt (Opus) | 9 / 25 / 7 requests; 327,732 / 464,315 / 248,867 tokens; $0.35 / $0.54 / $0.32 vs Sonnet $0.13 / $0.11 / $0.13 |
| quick question (Opus) | 27,239 tokens × 3; $0.12 each vs Sonnet $0.07 / $0.06 / $0.06 |
| test output raw vs hook (Sonnet) | 92,903 / 92,560 / 91,248 vs 92,543 / 91,269 / 91,709 tokens: no real difference |
| `/context` memory files | 1.8k (107-line CLAUDE.md) vs 121 (7 lines); skills 9.9k |

Why the hook made no difference: the raw test output was 71,397 characters. Claude Code only keeps about 30,000 characters of a successful command inline; past that, Claude gets a saved-file path plus a preview of up to the first 2,000 characters ([tools reference, Output limits](https://code.claude.com/docs/en/tools-reference)). My filter left 15,843 characters, which all went inline.

Why a fresh session cost more at API prices: a new session writes its setup into the cache (1-hour cache writes cost 2× normal input on Anthropic's price list), while a long session re-reads its cache (0.05× input).

These are 3 runs each on one project and one setup. Your skills, project and prompts will change the numbers.

## Files

- `cc_tests.py`: runs the tests and saves the logs
- `instructions/`: the big and lean CLAUDE.md files
- `run-tests.bat`: runs the script inside WSL from Windows
- `sample-results/`: my raw logs

Sources: Claude Code docs, [Manage costs effectively](https://code.claude.com/docs/en/costs) and [Tools reference](https://code.claude.com/docs/en/tools-reference); Anthropic [pricing](https://platform.claude.com/docs/en/about-claude/pricing).
