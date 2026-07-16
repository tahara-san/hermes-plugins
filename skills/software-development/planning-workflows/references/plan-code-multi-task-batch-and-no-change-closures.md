# Plan-code multi-task batches and no-change closures

Use when the user invokes `/plan-code` over a directory containing multiple task dirs, especially when some are implementable, some are already satisfied by current source/tests, and some are blocked by explicit product/decision gates.

## Batch triage first

1. Inventory all `tasks/*/spec.md` + `todo.md` pairs and current git status before editing.
2. Classify each task:
   - **implementable now** — acceptance criteria and gates are concrete enough to code/test;
   - **no-change closure candidate** — current source/tests already satisfy the task contract and the spec allows closing as verification/regression coverage;
   - **blocked** — the task docs require a product/source-of-truth/manual decision before implementation.
3. Execute only implementable tasks. Do not invent missing product decisions to make a blocked task runnable.
4. For blocked tasks, still re-read the source files named in Phase 0 when practical, then save a concise blocker report and mark only evidence/setup rows complete. Mark unresolved decision rows `[!]`, not `[x]`.

## No-production-change closure

When a task may already be satisfied:

1. Re-read the current implementation and tests named in the task docs.
2. Run the documented focused verification commands if available.
3. If current source/tests pass and the spec permits no-change closure, do **not** churn production code just to make a diff.
4. Update `todo.md` and `final-report.md` truthfully:
   - state no RED failure was produced because current source already satisfied the contract;
   - state no production source was changed;
   - list the exact tests/build/static checks that proved the contract.
5. Still build a final review bundle containing current source/test snapshots, task docs, and verification evidence. A docs-only diff is not enough for reviewers to judge a no-change source closure.

## Review sequencing in multi-task batches

- Build one immutable bundle per task directory; do not mix unrelated task diffs unless the tasks are intentionally coupled.
- Finalize one immutable bundle per task, then launch every independent interactive Codex TUI and Claude Code `claude-i` lane before waiting on any generated-task reviewer. Use the same saved bundle for both lanes of each task.
- If Claude approves but the interactive Codex TUI has not produced a parseable attested verdict, save `reviews/codex-implementation-review-pending.json` with:
  - `passed: false`
  - `status: BLOCKED_PENDING_CODEX_REVIEW`
  - tmux session and raw pane capture
  - bundle path and hash
  - completed companion review artifact(s)
  - exact resume steps
- Leave live TODO rows `[!]` for the pending Codex review and aggregate `final-review.json`. Do not create a passing aggregate until the Codex verdict is saved or explicitly waived.

## Final response wording

For a batch where some tasks completed implementation but mandatory review is pending, say the implementation is verified but `plan-code` is not fully complete. Distinguish:

- executable tasks implemented/verified;
- no-change tasks verified/closed as current-source satisfied;
- blocked tasks stopped at decision gate;
- pending review gates that prevent claiming completion.
