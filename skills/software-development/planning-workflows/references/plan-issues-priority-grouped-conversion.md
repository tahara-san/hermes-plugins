# Plan-issues priority grouped conversion

Use when the user invokes `/skill plan-issues <priority>` or asks to convert `tasks/out-of-scope-issues/<priority>/` into implementation task docs.

## Session-derived pattern

1. Treat the request as a docs-only issue-conversion workflow. Do **not** implement fixes during conversion.
2. Load `planning-workflows`, then read all matching issue files for the requested priority, including nested `manual/` entries.
3. Ask one early scope/decision question when the grouping could reasonably vary. Good choices include:
   - all issues grouped into multiple task dirs;
   - only frontend-owned product/code issues;
   - only E2E/test-infra issues;
   - only backend/cross-repo contract issues.
4. Check existing `tasks/` dirs and `git status --short` before writing so new plans do not duplicate in-flight work or absorb unrelated dirty state.
5. Group issues by class and ownership, not one task per issue. Build a dependency graph across groups and name every generated directory `tasks/<implementation-order>-<task-name>/` with a zero-padded order starting at `01`. Give independent groups the same number when parallel implementation is safe; increment only for a dependent implementation wave. Prefer class-level task names such as:
   - E2E/test-infra stabilization;
   - signout/session state hardening;
   - backend public contract;
   - backend retry/infrastructure bug;
   - model/schema contract;
   - UI/auth/cache policy;
   - runtime config contract;
   - editor/accessibility reliability.
6. For backend-owned issues discovered from a frontend repo, read backend source only enough to ground the plan. If the backend checkout is dirty with unrelated work, record that and keep new docs in the origin workspace unless the user explicitly directs backend-repo plan creation.
7. Each generated task dir should include `spec.md` and `todo.md` with:
   - source issue links;
   - goal/current evidence;
   - scope and out-of-scope;
   - explicit no-migration / no-backward-compatibility constraints when requested;
   - acceptance criteria;
   - decisions/open gates that must stop implementation if unclear;
   - implementation phases;
   - verification commands;
   - kickoff prompt and review-gate expectations.
8. Preserve original out-of-scope issue files during conversion. Do not remove or edit them unless the user explicitly asks for cleanup after the mapping is clear.
9. After writing, verify coverage mechanically: every source issue maps to exactly one generated plan, with no missing or multi-mapped issue unless deliberately documented. When deleting converted issue files in the same session, create or update a compact coverage-map artifact (for example `tasks/<priority>-priority-issue-conversion-coverage.md`) before removal so the provenance remains durable after the originals are gone.
10. Because `plan-issues` invokes task-doc creation, run the explicit `plan-doc` review gate on the generated plans unless the user explicitly waives it. Do not treat embedded future review-gate wording in `spec.md` as satisfying this requirement. Build one self-contained immutable plan-doc bundle per generated task, run both required review legs (external **Codex interactive TUI** GPT-5.6 SOL @ xhigh in managed `tmux` per `codex-cli-review-lane.md` + Claude Code default Opus 4.8 via the CLI-based `claude-i` workflow), save raw artifacts and an aggregate verdict under each generated task's `reviews/`, and rerun both legs if reviewer feedback changes docs. Do not use noninteractive `codex exec` or `codex review`, which cause severe timeout issues.
11. Finalize every generated task's immutable bundle first, then launch every required independent review lane before waiting for, polling, monitoring, adjudicating, or fixing findings from any one lane. When task bundles and artifact paths are independent, launch Codex and Claude for all generated tasks before waiting on any reviewer, then aggregate per task. The implementation-order prefix does not impose review order; serialize only when a task bundle genuinely depends on unresolved findings from an earlier task review, and record that dependency. If any interactive Codex TUI has not produced a passing parseable verdict, save a pending/blocker artifact naming its task, tmux session, raw pane capture, and bundle path, and report the conversion as pending rather than complete.
12. Run a lightweight docs sanity check such as `git diff --check -- <new task dirs>` and report untracked task dirs separately. This sanity check is not a substitute for the required plan-doc review gate.
13. If the user then asks to remove processed issue files, delete only the exact source issue files that were mapped into generated plans in this session. Before deletion, confirm the candidate list against the coverage map and current status; after deletion, verify the issue directory/search result and scoped git status. Do not remove unmapped, manual, or newly discovered issue files by priority glob alone.
14. If an out-of-scope issue file is partially stale against current source, do not preserve stale claims as task truth. Record the source issue as converted, but write the generated task around current evidence: state which claim is stale/resolved, keep any still-active sub-issue, and make implementation start with a contract/evidence gate rather than a forced code change.

## Pitfalls

- Do not push through ambiguous product/ownership decisions. The user specifically values active clarification for plan-issues conversions.
- For rapid-request, race-condition, or write-conflict issues discovered from E2E/full-suite runs, do not frame retry logic as the default fix. Encode a decision gate: first classify whether tests/callers are clobbering shared state with rapid API calls; prefer test serialization/isolation or caller cleanup when that is the cause. If any plan would add retry logic, require explicit user clarification and a narrow idempotent boundary.
- Do not create migration or backward-compatibility steps when the user asks for current-contract/no-compat plans.
- Avoid over-reading unrelated repos. For cross-repo issues, enough source evidence to plan is useful; modifying or deeply auditing a dirty secondary repo is not.
- Do not claim plan-doc review completion unless the explicit plan-doc review stack actually ran. For issue conversion, embedding review gates in the generated task docs is not the same as running them.
- When a source issue is examined during conversion but **not** mapped to a generated plan because current source shows it stale/resolved, do not treat it as "covered by these plans" during a later cleanup request. Remove only the exact issue files mapped to generated task dirs unless the user explicitly asks to remove stale/resolved examined issues too. Update the coverage map before deletion so it records which mapped source files were removed and which examined-but-unconverted files were intentionally kept.
