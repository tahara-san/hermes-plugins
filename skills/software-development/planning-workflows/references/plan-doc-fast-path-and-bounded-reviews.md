# Plan-doc fast path and bounded external reviews

Use this when an explicit `plan-doc` task starts drifting into long discovery or external review overhead.

## Problem pattern

A `plan-doc` session can stall when the agent front-loads too much inspection before creating the first artifact, or lets an external reviewer roam the repo instead of judging the prepared bundle. The user may experience this as silence or pipeline bloat even when the final docs are good.

## Faster sequence

1. **Bound discovery first.** Read only the source issue/task, `git status --short`, package/test-script context, and the smallest relevant config/source excerpts needed to avoid hallucinating.
2. **Create the task bundle early.** Write `spec.md`, `todo.md`, kickoff prompt, and the initial review bundle before doing broad searches.
3. **Review the concrete bundle.** Run Codex-style and Claude Code reviews against the saved bundle rather than continuing open-ended repo exploration.
4. **Adjudicate before churning.** Do not apply non-blocking suggestions that are already satisfied, factually stale, or based on unrelated plan shapes; record the adjudication in the review artifact instead.
5. **Only rerun reviews when plan docs changed.** Saving raw/aggregate review artifacts after approval does not require editing the plan docs; avoid unnecessary reruns unless the reviewed plan content changed.

## Bounded Claude Code plan review prompt rules

For `claude-i` plan-doc reviews:

- Start with the prepared bundle and task-doc paths.
- Say `read-only review`, `do not edit`, and `do not run tests/builds/package installs/long commands`.
- If Claude starts broad repo exploration or long command activity, interrupt quickly and ask for a verdict from already-read evidence.
- Save the deviation honestly in the Claude review artifact; do not count a wedged or incomplete pane as approval.
- If the final verdict cites non-blocking suggestions that do not match the actual docs, verify with a narrow text search or file read and record them as reviewer noise rather than patching the docs.

## User-facing communication

If the user asks why the task is slow, answer directly and optimize the pipeline immediately. Acknowledge avoidable overhead in plain terms, then produce the missing artifact or bounded review instead of sending another long process recap.
