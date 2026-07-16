# Plan-code resume after task artifacts were committed/removed

Use when a `/plan-code` task is resumed after prior work may have been committed, cleaned up, or moved by another agent/user while the conversation still contains stale task-dir context.

## Pattern

1. **Trust the current checkout over the transcript.** Re-check `git status --short`, branch, HEAD, and recent commits before editing or recreating task files.
2. **Search before recreating missing task dirs.** If `tasks/<slug>/` is absent, verify whether it was committed and then removed/cleaned up in recent history. Do not resurrect a completed/removed task directory just because earlier conversation context mentions it.
3. **Continue the live remaining gate if it still matters.** If the blocked item was an environment gate (for example canonical E2E host was down) and the host is back, run the gate against the current branch/HEAD and save the log somewhere non-invasive when the original task dir is gone (for example `/tmp/...`), unless the user explicitly asks to restore artifacts.
4. **Report current-state truthfully.** Say when the original task artifacts are no longer in the checkout, name the current HEAD, and distinguish current verification results from historical task-doc status.
5. **Keep unrelated new task dirs untouched.** If `git status` shows only unrelated untracked task dirs, do not fold them into the resumed task or stage them opportunistically.

## Buffdemy2-web E2E example

- Canonical host check: `curl -I --max-time 10 http://host.docker.internal:3000`.
- If restored, rerun the previously blocked focused command first, then the full suite if still requested by the plan-code contract.
- When `tasks/e2e-suite-stability-medium-followups/` has been removed by later commits, write continuation logs under `/tmp/buffdemy2-web-e2e-logs/` and report the path instead of recreating the removed directory.
