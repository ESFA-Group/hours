---
description: Commit this session's changes with a brief message
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*)
---

Commit the working-tree changes. Be fast: no exploration, no extra file reads, no thinking out loud.

Current state:

- Status: !`git status --short`
- Staged diff: !`git diff --cached --stat`
- Unstaged diff: !`git diff --stat`
- Recent messages for style: !`git log --oneline -5`

Do exactly this:

1. If the working tree is clean, say so in one line and stop.
2. Stage the changes from this session with `git add`. Skip anything clearly
   unrelated or accidental (stray logs, `db.sqlite3`, `debug_*.xlsx`, editor
   junk). If something looks unintended, leave it unstaged and mention it in
   one line afterwards.
3. Commit with a brief message: one lowercase summary line under ~60 chars,
   present tense, matching the style in the log above. Add a short body only
   if the summary genuinely cannot carry it. End the message with:
   `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`
4. Do not push. Do not create a branch. Do not amend earlier commits.
5. Reply with just the short hash, the summary line, and anything left
   unstaged. No recap of the work.

$ARGUMENTS
