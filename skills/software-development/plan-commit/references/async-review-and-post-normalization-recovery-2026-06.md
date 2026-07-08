# Async review + post-normalization recovery pattern (2026-06)

Use this reference when a plan-commit flow is blocked by an asynchronous delegate review or when generated task artifacts need whitespace normalization after a consistency verdict.

## Proven sequence

1. If a required `delegate_task` verdict did not re-enter the parent chat, recover the subagent session before rerunning or waiving:
   - Search `~/.hermes/logs/agent.log` for the delegation id and review prompt phrase.
   - Extract the `platform=subagent` session id.
   - Read it with `session_search(session_id="<id>", profile="default")`.
   - If the transcript has a parseable verdict, save it as the canonical review artifact and mark the old pending marker `recovered_superseded`.
   - If the session has only the prompt, save a pending marker with delegation id, session id, bundle path, blocked stage, and resume steps; stop before staging/committing.
2. When `git diff --cached --check` fails only inside intended generated review bundles:
   - Normalize only the intended generated artifacts (usually strip line-end whitespace; do not edit unrelated files).
   - Restage the intended scope and rerun `git diff --cached --check`.
   - Generate a post-normalization consistency bundle over the staged state.
   - Dispatch/read a bounded read-only consistency review.
   - If the review is asynchronous, wait/recover by session id as above; do not commit until its JSON verdict is saved.
3. Save the post-normalization verdict under the task directory (for example `reviews/post-normalization-artifact-consistency.json`), stage it, rerun staged name-status/stat/check, then commit.
4. After the artifact commit is pushed/read back, run `git rm -r --dry-run -- tasks/<slug>` and proceed with the cleanup commit only if the dry-run lists only that task directory.

## Pitfalls

- A dispatch id alone is not a passed review. Commit only after a final JSON verdict is saved.
- Session DB persistence can lag after the log shows subagent API/tool activity. If the log shows no `Turn ended`, wait briefly; if it shows `Turn ended` but `session_search` is stale, retry once with a changed read strategy rather than rerunning the review immediately.
- Frozen historical review bundles may contain checklist rows that were pending at bundle-generation time. Current `todo.md`, `final-report.md`, and aggregate review JSON are canonical for active completion state; reviewers should treat old bundle rows as historical unless the task docs point to them as current.
- If a final report says task-artifact/cleanup commits are pending, that is correct before the artifact commit. Do not rewrite history after the cleanup commit just to update an already-deleted task directory; report the pushed commit readbacks instead.
