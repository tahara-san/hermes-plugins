# Plan-doc issue conversion when current source already satisfies the issue

Use this when converting a parked `tasks/out-of-scope-issues/...` file into a `tasks/<slug>/` plan and live source/tests already appear to satisfy the reported issue.

## Pattern

1. **Convert the issue, do not re-implement by inertia.** Create the normal `spec.md`, `todo.md`, and `kickoff-prompt.md`, but make the plan verification/closure-first: `/plan-code` starts by re-reading current source/tests and may close as a no-change verification if the contract still holds.
2. **Preserve historical traceability.** Copy the issue's concrete failure details into the new plan: old helper/function names, approximate line numbers, sibling diagnosis filenames, observed broken path, and suggested fix. If current source has evolved, explicitly map the old failure point to the new current helper names so implementers do not resurrect stale code shape.
3. **Remove the parked issue only after the task docs exist.** The new task dir becomes the durable home for the issue details; verify the old issue file is gone before final reporting.
4. **Separate current-state evidence from future acceptance criteria.** Record read-only evidence such as existing helpers and focused tests, but phrase acceptance criteria as the contract to preserve, not a claim that implementation work is required.
5. **Make verification commands honest for untracked task docs.** `git diff --check -- tasks/<slug>` does not check untracked files unless Git knows about them. For newly created plan docs, either use `git add -N` deliberately or add a small explicit scan over top-level task markdown. If review artifacts are excluded from the reviewed scope, say the scan intentionally targets top-level task docs and excludes `reviews/`.
6. **Keep duplicate kickoff snippets synchronized.** If the spec includes an embedded copy-paste prompt and there is also a standalone `kickoff-prompt.md`, update both after reviewer suggestions. Reviewers often catch stale duplicate command blocks or phase numbering in the embedded prompt after the canonical section was fixed.
7. **Supersede and rerun after useful non-blocking suggestions.** Save passing-but-superseded raw reviews and bundles, patch only task docs, regenerate the bundle, and rerun both required plan-doc review legs. Do not churn on purely cosmetic suggestions after final approval; record their disposition in the aggregate.
8. **Recover final delegate reviews before marking the gate complete.** If `delegate_task` does not surface in the parent chat, use logs to find the subagent session and recover the final verdict with `session_search(session_id=...)`. A dispatch ID is not approval.
9. **Use a final artifact-consistency check after artifact-only edits.** Writing raw review artifacts, aggregate JSON, or changing a TODO review row after semantic review makes the artifact set differ from the reviewed bundle. Save a narrow consistency JSON that checks required files, parseable verdicts, issue removal, TODO status, and explicitly excludes itself from scope.

## Good final report shape

- Name the new task dir and deleted issue file.
- State whether current code already appears to satisfy the issue.
- List verification commands and real outputs.
- Name final Codex-style, Claude Code, aggregate, and artifact-consistency artifacts.
- Report unrelated pre-existing dirty work separately.

## Pitfalls

- Do not claim `git diff --check` validates untracked task docs.
- Do not let a stale embedded kickoff prompt contradict the standalone prompt.
- Do not count superseded delegate/Claude approvals after task docs change.
- Do not create fake implementation-review artifacts for a docs-only/no-change-closure plan.
