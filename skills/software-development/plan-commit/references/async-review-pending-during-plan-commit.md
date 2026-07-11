# Async review pending during plan-commit

Use this when a `plan-commit` flow reaches a mandatory review or artifact-consistency gate that was dispatched via `delegate_task` but has not re-entered the parent chat.

## Durable lesson

A dispatched async delegate is not a passing gate. Plan-commit must stop before staging or committing the repo whose artifacts depend on that gate unless the verdict is recovered and saved, or the user explicitly waives it.

This can happen in two places:

1. **Implementation review recovery before commit-readiness** — recover the missing implementation review from Hermes logs/session history and save the canonical verdict before creating aggregate final-review artifacts.
2. **Pre-commit artifact-consistency review after artifact edits** — if task docs are patched during commit prep (for example to add a secondary repo commit SHA/readback), run the consistency review and wait/recover it before staging the task artifacts.

## Sequence

1. Search logs for the delegation id and identify the subagent session id.
   - Search rotated logs too (`~/.hermes/logs/agent.log*`), not just the current file.
   - A dispatch line often includes `Dispatched async delegation batch deleg_xxx` followed immediately by a subagent session id like `20260625_162936_81a722` in the same log window.
2. Read the subagent session directly with `session_search(session_id=..., profile="default")`.
   - If `session_search` returns a persisted-output file because the session is large, read/parse that saved JSON file instead of treating the oversized result as failure.
   - Inspect the final assistant messages for a parseable verdict; a completed subagent may have used tools and only emitted the JSON verdict in the last message.
3. If the session contains a parseable final verdict:
   - save it as the canonical review artifact;
   - mark any pending marker as superseded rather than deleting it when it already exists in the task directory (for traceability, set `superseded_by`, `superseded_at`, and a non-blocking completion status);
   - create/update the aggregate final-review artifact and task docs;
   - run a narrow final artifact-consistency check because these artifact edits happened after the implementation reviews;
   - continue the commit flow only after that consistency check passes.
4. If the session only contains the prompt or no parseable verdict yet:
   - save a pending marker under `tasks/<slug>/reviews/` with delegation id, subagent session id, bundle path, blocked commit stage, and resume steps;
   - do not stage or commit artifacts that depend on the review;
   - report that the implementation may already be pushed but the artifact/cleanup commits are blocked on the pending gate.

## Pending marker fields

Use a JSON marker like:

```json
{
  "status": "pending",
  "reviewer": "Hermes async artifact-consistency reviewer",
  "delegation_id": "deleg_xxx",
  "subagent_session_id": "20260623_121719_b445b3",
  "bundle_path": "tasks/<slug>/reviews/pre-commit-artifact-consistency-bundle.md",
  "purpose": "pre-commit artifact consistency review after secondary repo commit readback was patched into task artifacts",
  "commit_flow_status": "secondary implementation commit pushed; task-artifact commit and cleanup commit blocked until this verdict is saved as passing",
  "resume_steps": [
    "Recover or wait for the subagent verdict.",
    "If passed, save the canonical verdict and supersede this marker.",
    "Then stage exact intended paths, run staged readback/checks, commit/push artifacts, and only then cleanup-delete the task dir."
  ]
}
```

## Pitfall

Do not create a passing aggregate/final consistency artifact or commit task artifacts while the only evidence is a dispatch id. A prompt-only subagent transcript is not a verdict.