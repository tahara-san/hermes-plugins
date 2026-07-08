# Plan-doc external review gate

Use this when a user asks for Claude/external review of planning docs themselves, before implementation.

## Why this exists

Plan docs are often untracked files under `tasks/<slug>/`. A plain `git diff` review bundle can miss them entirely. Plan-doc reviews also commonly produce useful non-blocking clarifications; if you patch the docs after the review, the previous approval is stale and should be rerun before claiming the gate passed.

## Recommended flow

1. Create a review bundle outside the repo, usually under `/tmp/hermes-review/<slug>/plan-doc-review-bundle.md`.
2. Include:
   - exact `spec.md` / `todo.md` paths,
   - `git status --short`,
   - full contents of the task docs, not just diff,
   - relevant package scripts if the docs cite verification commands,
   - a lightweight static/secret scan result for the docs.
3. For cross-repo plans, verify and state the authoritative target repository before building the bundle. If a similarly named legacy repo exists, mark it explicitly as out-of-scope/stale evidence. Include source snippets/package scripts from the target repo, not just the current workspace, so the reviewer can catch repo-scope mistakes.
4. Run the reviewer read-only. For Claude Code, follow the `claude-i` skill’s interactive tmux workflow; avoid `claude -p` when the user specifically requested that workflow.
5. Ask for a bounded verdict:
   - `VERDICT: APPROVED` or `CHANGES_REQUIRED`,
   - blocking findings,
   - non-blocking suggestions,
   - one-paragraph summary.
6. If the reviewer returns `CHANGES_REQUIRED`, patch the plan docs first, regenerate the bundle, and rerun the reviewer. Do not save or cite an approval until the verdict is current for the post-fix docs.
7. If the plan was reviewed against the wrong repository, API version, or stale evidence, mark the old review artifact `SUPERSEDED / STALE` in-place and rerun the review with a corrected bundle. Do not delete the stale artifact; keep the audit trail but make the invalid scope obvious at the top.
8. Incorporate blocking findings and any useful suggestions you choose to adopt into the task docs.
9. Regenerate the bundle and rerun the review until the final verdict is current for the final docs.
10. If the rerun returns `APPROVED` with cosmetic/non-blocking suggestions that you intentionally do not adopt, record them in the review artifact instead of patching after approval; patching after approval makes the verdict stale and requires another rerun.
11. Save an artifact under `tasks/<slug>/reviews/`, for example `claude-plan-doc-review.md`, containing timestamp, reviewer, scope, bundle path, static scan result, process summary, final verdict, and any non-blocking suggestions left unapplied.

## Common clarifications reviewers catch

- Limits that are not simultaneously saturable: make tests validate each boundary in isolation rather than an all-max payload.
- Byte caps versus JavaScript `.length` / UTF-16 units: keep frontend warning units distinct from backend byte budgets.
- Recursive validators: prefer iterative or otherwise bounded walkers so pathological input cannot overflow recursion or force full serialization before budget failure.
- Custom handler-level validation: add handler-path tests, not only schema tests.
- Review workflow wording: make the skill/workflow invocation concrete and consistent across `spec.md`, `todo.md`, and the kickoff prompt.

## Artifact wording pattern

```markdown
# Claude Plan-Doc Review — <task title>

- Timestamp: `<ISO timestamp>`
- Reviewer: Claude Code via `claude-i` interactive tmux workflow
- Mode: read-only plan-doc review
- Scope:
  - `tasks/<slug>/spec.md`
  - `tasks/<slug>/todo.md`
- Review bundle: `/tmp/hermes-review/<slug>/plan-doc-review-bundle.md`
- Static scan result: No obvious secret-like strings found.

## Final verdict

```text
VERDICT: APPROVED
...
```
```
