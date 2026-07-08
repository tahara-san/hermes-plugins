# Buffdemy plan-code Fable 5 review override

Use this reference only when the user explicitly requests Fable 5 for a Buffdemy plan-code review gate. Otherwise use the default `claude-i` model guidance.

## Selector procedure

1. Start Claude Code interactively in tmux as usual.
2. Capture the initial banner. If it already shows `Fable 5`, proceed.
3. If it shows another model, open `/model`.
4. Move to the `Fable` row deliberately and capture the selector before confirming. In tmux, a plain `Down` key may not move; use `C-n`/`C-p` when needed.
5. Confirm the selection session-only with `s` for task-local overrides.
6. Capture again and verify the banner says `Fable 5 with <effort> effort` before pasting the substantive review prompt.
7. If Claude reports it set the old model, do not proceed. Reopen `/model`, capture the cursor on Fable, and retry.

## Review-bundle practice

- Build a self-contained bundle that includes both repos when the task spans backend and frontend.
- Include tracked diffs, full contents/diffs for untracked files, task docs, and exact verification commands/results.
- Avoid truncating diffs in bundles for mandatory review gates. If a previous bundle was truncated or a reviewer needed to inspect omitted paths, regenerate an uncapped final bundle before the approval rerun.

## Bounded review loop

Fable 5 may perform several read-only spot checks. Approve scoped read-only inspections that answer a concrete uncertainty, but bound the session if it keeps exploring:

1. After a few spot checks or several minutes, send a no-more-tools verdict request.
2. If the request is queued behind a tool call, interrupt with `Ctrl-C`.
3. Ask for the explicit `VERDICT / BLOCKERS / WARNINGS / NOTES` structure based only on already-reviewed context.
4. Save the raw pane even if the top verdict line scrolls out; if the verdict header is missing, restate or mark the artifact as partial rather than pretending it is complete.

## After fixes

- If the review finds a blocker or worth-addressing warning and you change code/docs, rerun the relevant verification.
- Regenerate a final bundle after the fix.
- Run a short Fable 5 final delta review against the regenerated bundle and save it under `tasks/<slug>/reviews/`.
- Record operational warnings separately from code blockers when the task explicitly forbids migration/backward-compatibility code.

## Cleanup

After verdict capture, clear the input line with `Ctrl-U`, send `/exit`, and kill the tmux session if it remains. Re-check the worktree for accidental Claude metadata or edits.
