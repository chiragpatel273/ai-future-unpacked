---
name: commit-message
description: Writes git commit messages the way our team wants them. Use when the user asks to commit, write a commit message, or save their staged changes.
---

# Commit messages: our team's rules

1. See what is staged: `git diff --cached`. If nothing is staged, stop and say so.
2. Find the ticket ID in the branch name: `git branch --show-current`.
   Example: `feature/PAY-142-discount-cap` means the ticket is `PAY-142`.
3. Write three parts:
   - **Subject:** `<type>(<scope>): <summary>`
     - type is one of: feat, fix, refactor, docs, test, chore
     - scope is the main file or area, e.g. `cart`
     - summary in the imperative ("cap", not "capped"), max 60 characters, no full stop
   - **Why:** one sentence on why the change was needed (not what it does)
   - **Footer:** `Refs: <ticket ID>`
4. Check it before committing (run from the repo root):
   `python .agents/skills/commit-message/scripts/check_message.py "<subject>" "<why>" "<footer>"`
   If it prints problems, fix them and check again until it prints OK.
5. Commit with exactly those three parts:
   `git commit -m "<subject>" -m "<why>" -m "<footer>"`
