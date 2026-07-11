---
name: planning-workflows
description: "Use when planning, documenting, executing, cleaning, or converting implementation plans and task directories across Hermes/Claude-style workflows."
version: 1.0.5
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, implementation-plans, plan-mode, tasks, execution, cleanup]
    related_skills: [subagent-driven-development, requesting-code-review, test-driven-development]
---

# Planning Workflows

## Overview

This umbrella skill covers the planning class: writing implementation plans, operating in plan-only mode, creating structured task docs, executing existing task plans, converting out-of-scope issue logs, and cleaning completed task directories.

Use `references/codex-cli-review-lane.md` for every Codex review lane. It defines the required **interactive Codex TUI** (`codex` in a managed `tmux` session), GPT-5.6 SOL/xhigh pin, pane-capture attestation, artifacts, failure handling, and the prohibition on noninteractive `codex exec` / `codex review` commands or a Hermes reviewer subagent. The noninteractive commands cause severe timeout issues in this workflow.

Migrated detailed references are under `references/` with source prefixes. Use `references/plan-code-delta-review-rerounds.md` when an explicit `plan-code` review gate has a prior clean full-review baseline and post-fix rerounds can safely review only changed, semantically affected, or no-baseline content while carrying unchanged clean verdicts forward. Use `references/out-of-scope-issue-cleanup-audit.md` when the user asks to clean or triage `tasks/out-of-scope-issues/` without immediate removals: enumerate every issue, verify against current source or external source of truth, classify fixed/stale/partial/active, and report cleanup candidates only. Use `references/plan-doc-issue-conversion-currently-satisfied.md` when converting a single out-of-scope issue into a plan-doc and current source/tests already appear to satisfy it: create verification-first task docs, preserve historical issue traceability, remove the issue only after docs exist, keep duplicate kickoff prompts synchronized, and use final artifact-consistency after review artifact/TODO edits. Use `references/plan-code-multi-task-batch-and-no-change-closures.md` when the user invokes `plan-code` over a directory containing multiple task dirs: triage implementable/no-change/blocked tasks first, close already-satisfied tasks with source/test snapshots instead of churn, and save pending Codex-interactive-review blocker artifacts when the required interactive verdict has not returned. Use `references/plan-issues-priority-grouped-conversion.md` when the user invokes `/skill plan-issues <priority>` or asks to convert priority-filtered out-of-scope issues into grouped task dirs: read all issue files including `manual/`, ask an early scope decision when grouping is ambiguous, group by class/ownership, preserve source issue files, and mechanically verify every issue maps to exactly one generated plan. Use `references/plan-doc-clarification-defaults.md` when a plan-doc interview times out or the agent must choos...... [truncated]

## When to Use

- The user wants a plan instead of execution.
- The user asks to create `tasks/<task-name>/` planning documents.
- The user asks to execute an existing plan phase-by-phase.
- The user asks to convert out-of-scope issue logs into task plans.
- The user asks to clean, classify, or delete completed task directories.
- The user asks for a high-quality implementation plan for another agent or developer.

## Explicit Slash-Flow Contracts

When the user explicitly invokes `/skill plan-doc`, `/plan-doc`, `/skill plan-code`, `/plan-code`, or says to use `plan-doc` / `plan-code`, treat that as a workflow contract, not a suggestion. These flows are fail-closed: if any required artifact or gate cannot be completed, stop and report the blocker instead of continuing as ordinary implementation.

### First Response Checklist

Before any implementation edit in an explicit slash-flow turn, state the selected mode and immediately perform the required first action:

- `plan-doc`: identify/create the task directory, then create or update task docs.
- `plan-code`: read the existing task docs first, then execute the documented TODOs.

Do not substitute a normal implementation plan, memory of the workflow, or an after-the-fact summary for these required first actions.

### Default Parallel Review Stack

Unless the user explicitly overrides the review stack, explicit `plan-doc` and `plan-code` workflows use a two-reviewer gate:

| Review lane | Required invocation | Executable policy |
|---|---|---|
| **Codex interactive TUI review** | Start bare `codex` in a managed `tmux` session against a saved, self-contained bundle; **GPT-5.6 SOL @ xhigh effort** is required. Follow `references/codex-cli-review-lane.md` exactly. | Run `--model gpt-5.6-sol -c 'model_reasoning_effort="xhigh"'` in a read-only sandbox, paste the prompt through the TUI, save a raw pane capture + schema-constrained normalized verdict, and verify the TUI model/effort attestation. Never use noninteractive `codex exec`, `codex review`, or `delegate_task` for this lane or as fallback. |
| **Claude Code Opus 4.8 @ xhigh effort review** | Claude Code CLI through the interactive `claude-i` workflow, not `claude -p`; verify and record the TUI model/effort banner. | This lane intentionally uses the local `claude` CLI because Hermes cannot directly delegate messages to Claude Code. |

The Codex lane must remain an external **interactive Codex TUI** lane. If the executable, authentication, GPT-5.6 SOL, xhigh effort, required TUI attestation, or parseable artifact is unavailable or mismatched, retry the same pinned interactive session flow with a narrower bundle or fail closed unless the user explicitly waives the lane. A waiver omits the lane; a substitution requires an explicit user override and must be recorded as a deviation. A Hermes `delegate_task` reviewer or noninteractive `codex exec` / `codex review` command never satisfies this lane.

Parallel launch is the default contract, not an optimization. Build one immutable review bundle first, then launch every required independent review lane before waiting for, polling, monitoring, adjudicating, or fixing findings from any one lane. In the default stack, start the Claude Code Opus 4.8 @ xhigh effort review through `claude-i` and the pinned interactive Codex TUI session against that same bundle; do not run Codex to completion and only then launch Claude Code, or vice versa. Serialize lanes only when the user explicitly requests it or a concrete shared-resource/safety constraint prevents concurrency; record that deviation and fail closed if it leaves a required lane incomplete. Start Codex through `tmux`, monitor and recover it only with bounded `tmux capture-pane` calls, and retain the session name; do not use a foreground/background one-shot `terminal` process or `process(wait)` / `process(log)` for Codex. Save separate raw reviewer artifacts plus one aggregate verdict artifact that records both verdicts, bundle path/hash, reviewer tool/model/effort attestation, interactive session state, static-scan status, verification status, and timestamp. Blocking findings from either reviewer fail the gate; non-blocking suggestions may be recorded without churn.

### Legacy-reference override

Some older reference artifacts may use terms such as “Codex CLI process”, “Codex-style reviewer”, or `delegate_task` recovery. They are historical evidence only and must not be followed to launch or satisfy a required Codex review. This interactive-TUI contract takes precedence: start bare `codex` in managed `tmux`, never run `codex exec`/`codex review`, and require the interactive attestation plus parseable verdict.

For `plan-doc`, review reruns are normally full dual-lane because the task docs are the product and are small enough to re-review. For `plan-code`, the first round of each gate is full dual-lane; after a clean baseline exists, post-fix reruns may follow `references/plan-code-delta-review-rerounds.md` so unchanged, unaffected files carry recorded clean verdicts forward while changed, semantically affected, and no-baseline files are reviewed. If the impact boundary is uncertain, rerun the full gate.

If the user waives or skips one review leg mid-session (for example, "skip Claude Code review for this task/session" after repeated stalls), record that as an explicit workflow override and do not invoke that reviewer again unless the user later explicitly asks for it. A later direct request such as "run Claude Code review on the diffs" supersedes the skip, but keep the rerun narrowly scoped to what was requested instead of restarting the full default gate.

For `plan-doc`, the bundle is the task docs, relevant current-code context, package/test-script context, git status, and any untracked task files. For `plan-code`, the full bundle is the implementation diff plus relevant untracked files, task docs, verification evidence, and static-scan results; a delta rerun bundle must also include prior clean baseline ids/artifact paths, changed files, semantically affected unchanged files, no-baseline files, carried-forward files, and the delta-interactions summary.

### `plan-doc` Required Sequence

For explicit `plan-doc` requests:

1. Stop before code changes unless the user explicitly combines planning and implementation.
2. Create or update `tasks/<task-name>/spec.md`.
3. Create or update `tasks/<task-name>/todo.md` or phase TODO files.
4. Include goal, scope/out-of-scope, acceptance criteria, decisions/open gates, implementation phases, verification commands, simplify/review gates, and manual-handling notes.
5. Include a copy-pasteable kickoff prompt for the implementer. The kickoff prompt must mention the task directory, objective, ordered phases, the default parallel Codex interactive TUI GPT-5.6 SOL @ xhigh + Claude Code Opus 4.8 @ xhigh effort review stack, verification commands, out-of-scope constraints, and final-report expectations.
6. Run the default parallel review stack on the plan-doc bundle unless the user explicitly overrides review. Save the Codex raw `tmux capture-pane` artifact and schema-constrained verdict, the Claude Code Opus 4.8 @ xhigh effort (`claude-i`) artifact, and an aggregate plan-review verdict under `tasks/<task-name>/reviews/`. For Codex, retain the managed tmux session name and recover only through bounded pane captures; a session name, startup banner, or partial pane is not approval. Follow `references/codex-cli-review-lane.md` for exact recovery and rerun behavior.
7. If reviewer suggestions change the plan docs, regenerate the bundle and rerun both review legs before presenting the plan as reviewed.
8. Save each raw review artifact immediately after that review leg completes. If saving the artifact fails or tools become unstable, fail closed: stop before launching any remaining review leg, report the exact artifact path that could not be saved, preserve the reviewer verdict in the main response, and instruct the user how to resume. If the legs were launched in parallel before the save failure surfaced, do not adjudicate or aggregate the gate; cancel, discount, or mark any in-flight companion verdict as incomplete/stale before stopping. Do not proceed to a new Claude Code review or aggregate verdict creation when the preceding Codex interactive TUI pane capture/verdict could not be durably written.
9. Present the docs/kickoff to the user and stop unless implementation was explicitly authorized.
10. If a required step is skipped, say exactly which step was skipped and why; do not imply the flow was completed.

### `plan-code` Required Sequence

For explicit `plan-code` requests:

0. Treat `plan-code` as an implementation workflow. If the user mentions a "final review", "post-implementation review", Claude review, or review artifact in the same request, that review is the final gate **after** implementation unless the current tree already contains a completed implementation and updated task progress. Do not run only the review against untouched plan docs and call the task done; either start coding or explicitly report that no implementation exists and ask whether to implement now.
1. Read `tasks/<task-name>/spec.md` and `todo.md` before editing implementation files.
2. If task docs are missing or lack acceptance criteria / review gates / verification, create or update them before coding.
3. Execute the TODOs phase-by-phase and update progress as work completes. If a required review returns blocking findings during the same active `plan-code` flow, continue fixing those blockers on your own, rerun impacted verification, update the clean-baseline ledger/scope notes, and rerun required reviews using a full or delta bundle per `references/plan-code-delta-review-rerounds.md`. Do not stop to ask for permission to fix review blockers unless the fix requires a product decision, broad scope change, destructive operation, or explicit user choice.
4. Run the simplify gate after implementation and after review/build fixes; for reruns, scope simplify to changed and semantically affected files unless the impact boundary is uncertain. Record any intentional non-simplification when broad refactors would increase risk.
5. Run the default parallel review stack before completion: Codex interactive TUI with GPT-5.6 SOL @ xhigh per `references/codex-cli-review-lane.md` plus Claude Code Opus 4.8 @ xhigh effort via `claude-i`, both against the same saved full implementation bundle. Launch both lanes before waiting on either one. Save the full-round clean baseline before carrying any verdict forward.
6. Save the final aggregate review verdict under `tasks/<task-name>/reviews/final-review.json` or document why an equivalent artifact path was used. The aggregate verdict must reference the Codex raw-pane and normalized-verdict artifacts and the Claude Code Opus 4.8 @ xhigh effort (`claude-i`) artifact, record the model/effort actually attested by each CLI, and name each review round as full or delta; the task is not complete unless both required legs pass or the user explicitly waives one.
7. If any code, test, fixture, migration, task doc, or intended commit artifact changes after review, the prior approval is stale for the changed/affected scope. Rerun impacted verification, classify the fix with `references/plan-code-delta-review-rerounds.md`, and rerun the review gate as full or delta according to that classification. If the reviewer-driven fix changes scope or reveals a missing handoff step, update the task spec/TODO before the rerun so the final artifact describes what was actually implemented. Before the final review, either put TODO/progress docs into their intended final state or plan one last artifact-consistency review after changing them; do not make unchecked final TODO edits after the final approval and then claim the review covered the final bundle. When finalizing docs after async reviewers or compaction, re-read the live TODO/progress snippets immediately before patching, because sibling agents or resume-time updates may have changed wording; patch the current active block narrowly, then search for stale `pending`/`incomplete` phrases and convert historical checkpoints to past tense so they do not contradict the final completion entry.
8. If review artifacts themselves are saved after the review verdict (for example Claude pane captures, final-review JSON, or consistency-review JSON), avoid infinite stale-artifact loops by using one of these patterns:
   - create a pending placeholder artifact before the final consistency review and overwrite it with the verdict afterward; or
   - run a final read-only artifact-consistency review scoped only to task docs/review artifacts after writing the verdict.
   Do not leave `passed: null` / pending placeholders behind in final artifacts.
9. Run the verification commands from the task docs with real tool output.
10. If the user later asks to commit/push a completed `plan-code` task, first reconcile the task progress docs with the actual completed work: update/check off completed TODO items, confirm no unchecked/in-progress/blocked items remain for the target task (ignore status-legend examples, but not real checklist rows), and stage only that task's implementation/docs/review artifacts. If a remaining `[!]` item is a genuine completed verification deviation rather than pending work (for example authenticated browser smoke was environment-blocked but covered by tests and review), convert it to a checked item that explicitly documents the deviation before staging. If an unchecked real TODO contradicts the current source (for example a required reconciliation source, transaction invariant, or test matrix row was not actually implemented), do not paper it over as a doc cleanup: return to implementation, add/adjust focused tests, rerun impacted verification, regenerate the bundle, and rerun final review before staging. If the TODO/final-report claims a specific reviewer/tool, broad test command, or artifact path, verify the saved artifact actually substantiates that claim; otherwise rewrite the doc to the truthful fallback or mark the command N/A before final consistency review. Any TODO/review-artifact edit made for commit readiness is a post-review artifact change: rerun a final artifact-consistency review on the exact pre-commit bundle before committing. Leave unrelated incomplete `tasks/` directories uncommitted unless the user explicitly includes them. When task directories are untracked/stale or unrelated task dirs are present, follow `references/plan-code-commit-readiness-untracked-tasks.md`: avoid `git add -A`, stage intended implementation paths explicitly, and report whether task removal was an untracked cleanup rather than a tracked deletion.
11. If `plan-code` legitimately stopped at an early blocker gate before implementation (for example a fail-closed data-contract gate), do not pretend the normal simplify/review/final-review sequence ran. If the user asks to commit/push that blocked outcome, commit only the blocker documentation/artifacts that were produced, run lightweight artifact checks such as scoped `git diff --check`, and report the commit as a blocker artifact rather than a completed implementation. Do not create a fake passing final-review artifact for code that was never implemented.
12. If the user explicitly asks for a final review while the task is still docs-only/unimplemented, run the requested read-only review gate against a bundle that proves the current state, save a failing `CHANGES_REQUIRED` artifact if the reviewer returns one, and report the task as blocked/not complete. A failing final-review artifact is allowed as durable evidence of the gate; it does not satisfy completion or replace the missing implementation/simplify/verification steps.
13. Final response must include completed phases, verification commands/results, review artifact path and verdict, remaining risks, and any deviations.

### Mandatory Final Self-Audit

Before finalizing an explicit `plan-doc` or `plan-code` flow, perform and report a compact audit:

- Task docs created/updated: yes/no
- TODO/progress updated: yes/no
- Kickoff prompt provided or used: yes/no/not applicable
- Simplify gate run: yes/no/not applicable
- Codex interactive TUI GPT-5.6 SOL @ xhigh review run and attested: yes/no/not applicable
- Claude Code Opus 4.8 @ xhigh effort (`claude-i`) review run: yes/no/not applicable
- Review baselines and delta/full rerun scopes recorded: yes/no/not applicable
- Parallel review aggregate artifact saved: yes/no/not applicable
- Post-review edits made: yes/no
- Review rerun after post-review edits: yes/no/not applicable
- Verification passed with real output: yes/no/not applicable
- Deviations documented: yes/no/not applicable

Any required `no` blocks claiming completion.

## Choose the Mode

### Plan-only mode

Use when the current turn must produce a markdown plan and avoid implementation. Inspect context read-only, write the plan under `.hermes/plans/` when appropriate, and do not mutate project code.

### Write implementation plans

Write for an implementer with little context: exact files, current behavior, target behavior, step-by-step tasks, tests, verification, risks, and rollback/cleanup notes. Favor bite-sized tasks and explicit acceptance criteria.

### Task document creation

For Claude/Hermes `plan-doc` style work, create `tasks/<task-name>/spec.md` plus `todo.md` or phase TODOs. Include dependency/parallelization analysis, decision gates, manual-handling notes, simplify/review gates, and verification. When the plan is an API/public-contract rename, use `references/api-rename-plan-pattern.md` for the compatibility-alias/canonical-response pattern.

When the plan-doc is still in discussion mode and the user is choosing between flows, keep replies short and decision-oriented: state the current decision point, the recommended default if useful, and then wait. Do not send long descriptive recaps while the user is reading or deciding. After the user chooses, patch the task docs directly and summarize only the changed plan semantics plus files touched.

If the user overrides normal review gates (for example, “skip Claude-i review but keep Codex review”), preserve that exactly in the plan’s review-gate section and final-report checklist instead of applying the default review stack mechanically. “Codex review” means the external pinned Codex interactive TUI lane unless the user explicitly requests a different reviewer.

When updating an existing plan after a user reports a quality problem, keep the spec at the policy/acceptance-criteria level unless the user explicitly approves an implementation strategy. Do not turn an observed regression into tailored fixture logic or prescribe a dictionary/heuristic overlay just because the current code happens to be heuristic; capture the observed data, the acceptance criteria, and a decision gate to evaluate/replace the provider instead.

When updating an existing plan-doc from a bug report or behavior complaint, first ground the spec change in read-only evidence where practical: inspect current task docs, relevant implementation/tests, and local/dev data if the user explicitly asks to compare real data (for example stored DB fields vs freshly computed results). Record durable findings in the task's `notes.md`, convert them into concrete `spec.md` decisions, and add executable TODO/verification items so `/plan-code` cannot skip the newly discovered edge case. If a clarification times out or is not provided, choose the safest interpretation that preserves the user's stated goal and document that choice as a decision rather than leaving the plan ambiguous.

When the user asks for a new clean task after a previous task direction was blocked, superseded, or based on a wrong assumption, create a fresh `tasks/<new-slug>/` file set instead of mutating the old task. In the new `spec.md`, state which old task it supersedes and what contract changed; leave the old task intact unless the user explicitly asks to remove it. If the user later asks whether the old directory can be removed, inspect tracked/untracked status and unique content first, then recommend a tracked deletion (`git rm -r tasks/<old-slug>`) only when the new task captures the intended replacement.

For bug-report `plan-doc` work where the real repro flow is complex or user-operated (uploads, payments, auth-specific UI, cross-device steps), do not interrupt the docs-only task by asking the user to manually retry unless the plan itself cannot be written without it. Instead, encode a Phase 1 evidence gate and a copy-pasteable manual-test request in the TODO/kickoff prompt: capture the exact hidden error boundary first, ask the user for one focused manual run only if local automation/log inspection cannot expose it, and require the implementer to record the user's result before changing source code. Also check `git status --short` before creating task docs and explicitly avoid unrelated untracked task directories so plan-doc output does not absorb another agent/user's work.

When the user asks for an external/Claude review of the plan itself, run it as a read-only plan-doc review gate rather than treating it like implementation review. Bundle the current task docs explicitly (including untracked `tasks/<slug>/` files, git status, relevant package scripts, and a simple secret/static scan), ask the reviewer for a bounded verdict, incorporate useful non-blocking doc suggestions, then regenerate the bundle and rerun the review so the saved artifact is not stale. Validate the saved bundle before dispatch: if Hermes `read_file`/script helpers inserted cache/dedup placeholders (for example `dedup`, `content_returned: false`, or “refer to earlier read_file result”) instead of real file contents, or if truncation/omission markers appear, regenerate the bundle from direct filesystem reads before review. Save the final review under `tasks/<slug>/reviews/` (for example `claude-plan-doc-review.md`) and report whether any suggestions remain. For multi-repo plan-docs, include each repo's task docs/status and relevant source excerpts in the same immutable bundle, but keep implementation handoff docs in their owning repos when the implementers will work there; record the aggregate verdict in the origin task directory and name companion backend/frontend docs explicitly in the final report. If a first review produces blockers or useful non-blocking plan improvements, save that initial artifact as superseded/initial, patch the docs, regenerate the bundle, and rerun all required review legs before claiming the plan is reviewed. If a reviewer cites project docs or guide files as contract evidence, classify their authority before accepting the finding: for Buffdemy backend, `docs/` is context-only by default, so a docs-only blocker should be saved as superseded, the plan/bundle should be patched to state the authority rule, and both review legs should be rerun. If parallel review legs are running and one reviewer returns `CHANGES_REQUIRED` before the othe... ... [truncated]

### Plan execution

For `plan-code` style work, load the existing plan, decide serial vs parallel execution, implement safe independent batches, update progress, run simplify/review gates, verify builds/tests, and report completion with evidence. If the user invokes a slash-skill flow such as `/skill plan-doc` or later asks whether `plan-code` was followed, treat that as a workflow contract: explicitly load/consult the governing skill or umbrella, document any deviation, and run the missing gate rather than claiming the flow was satisfied by ordinary implementation.

When the user asks to "resume and complete" an existing task but explicitly says to first examine/report remaining tasks and not implement or test without approval, treat the first turn as a read-only resume audit. Read the task docs, current relevant source, and git status; distinguish stale unchecked TODOs from implemented code; identify unrelated dirty work; report remaining implementation/test/doc-reconciliation work; then stop for approval. Do not run tests, builds, browser smoke, or make task-doc checkbox edits during that audit even if they look obvious.

When a `plan-code` task spans a large backend/API surface and the final review produces late blockers after prior green verification, first use `references/plan-code-large-diff-budget-and-checkpoints.md`: checkpoint current passing evidence, split by contract-level micro-bundles, fix only blockers that can be regression-tested and re-reviewed within the remaining budget, and stop with a fail-closed handoff rather than starting broad unverified patches near the tool/time limit. If the blockers are live-path data-integrity mismatches across outbox deltas, cron reconciliation, unique indexes, or wallet/payment semantics, also use `references/plan-code-review-driven-data-integrity-loops.md`: align live update semantics with reconciliation semantics, search for exact stale patterns after each patch, regenerate the final bundle, and rerun a focused review after the last code change.

For Buffdemy backend Elasticsearch/search projection lifecycle execution, use `references/buffdemy-search-projection-plan-code-lifecycle.md`: reset/backfill is a real implementation gate; if a non-destructive reconciliation path is chosen, prove it converges stale docs (non-ready rows, empty-content parents, missing roots) and rerun final reviews after adding or fixing the command.

When a plan labels a step as manual, first distinguish **human-only decision/observation** from **agent-runnable verification**. If the manual item is just commands, unit tests, Docker tests, repo inspection, env/preflight checks, or other tool-executable evidence, run it yourself and record the output instead of asking the user to do it. Stop for the user only when the gate requires an external human action/decision or a manual UI/device observation that cannot be exercised with available tools. If a direct host command is unavailable, try the project-documented container/dev-stack path before handing it back to the user.

When a plan replaces a heuristic with a third-party provider or native dependency, treat deployment viability as part of execution, not a follow-up note: verify the dependency installs/loads in the target runtime, exercise the relevant dev/container path, and run the production/build path where practical before marking the phase complete. If deployment is not viable, stop and report the blocker rather than silently falling back to the old heuristic.

When a plan-code task adds a new required canonical field and no-compat/pre-service data reset is allowed, treat existing local/dev data as an execution gate: query the live dev DB through the configured app/container environment, run a one-off inline update/reset if needed, record before/after counts, and verify no disposable migration script remains. If you update an obvious typed fixture outside the documented focused test set and its own extra test is blocked by a pre-existing harness issue, do not broaden into test-harness repair unless required; rerun the documented verification plus typecheck/lint and record the extra-test blocker as a deviation. See `references/plan-code-required-field-db-update-and-extra-test-deviation.md`.

When a `plan-code` task spans multiple repos and local verification depends on a running service/container, verify the live service's source mount or deployment source before editing a different checkout or claiming live smoke coverage. If the task's planned backend path differs from the backend actually serving the frontend, document the mismatch in task notes and stop before modifying the live path unless the user explicitly approves switching repos/paths. See `references/cross-repo-live-backend-path-gate.md`.

For Buffdemy2-web Article/ArticleComment editor-route or owner-action work, use the authenticated Playwright save/restore smoke pattern in `references/buffdemy2-web-plan-code-editor-smoke.md`: stored auth states for owner/non-owner/anonymous checks, temporary marker edits restored before completion, and console scanning for runtime i18n misses.

For Buffdemy2-web browser/API smoke when the dev server is already running on the user's host, use `references/buffdemy2-web-host-smoke.md`: probe and target `host.docker.internal:3000` from Hermes/WSL. If saved Playwright auth cookies are scoped to `localhost`, refresh/regenerate storage state for `host.docker.internal` or configure an explicit bridge; do not silently switch host-run server checks to agent-local `localhost`.

For Buffdemy2-web E2E stabilization work, use `references/buffdemy2-web-e2e-stabilization.md`: target host-running services through `host.docker.internal`, make cleanup failures visible, inspect frontend/backend API schema contracts before changing locators, handle titleless backend tiny shapes (such as list-item `ArticleTinyData`) as intentional metadata-only references, scope modal locators, harden comment/mention helpers against stale toasts/caret drift, and record dev-server/browser-project blockers separately from real test failures. When Hermes must rerun E2E against a temporary local Next server or auth/storage state fails before product assertions, also use `references/buffdemy2-web-e2e-local-env-auth.md` for base-URL, Redis, callback, and Playwright auth-state alignment.

For Buffdemy notification summary key cleanup/refactors, use `references/buffdemy-notification-summary-mapping.md`: verify `/workspace/dev/buffdemy-backend` as the target backend, treat `/workspace/dev/buffdemy2-api` as legacy unless explicitly requested, prefer target-first public keys, and first confirm whether the product is pre-service. If notification data can be flushed, plan a canonical-only reset with no legacy aliases/dual-accept/migration; use staged compatibility only when production/backward compatibility is required.

When a `plan-code` request asks for a clean worktree from a base branch but the current checkout is dirty, an old worktree path is broken/stale, or the user explicitly waives actual test runs, use `references/clean-worktree-plan-code-salvage-and-test-waiver.md`: create a separate clean worktree, salvage only scoped task files if useful, regenerate review artifacts instead of reusing stale approvals, mark waived tests as deviations, and normalize generated review bundles before staging.

### Issue conversion

For `plan-issues` style work, scan `tasks/out-of-scope-issues`, filter by priority, group and deduplicate issues, resolve decisions up front, and explicitly load/use the `plan-doc` skill workflow for each generated task. Name each new directory `tasks/<implementation-order>-<task-name>/` with a zero-padded order such as `01-`; tasks in the same safe parallel implementation wave share a number, while dependent waves increment it. Do not implement fixes during issue conversion.

Because issue conversion invokes task-doc creation, the generated task plans require the explicit `plan-doc` review gate unless the user explicitly waives it. A coverage map and `git diff --check` are useful but insufficient. Build and finalize one self-contained immutable bundle per generated task. For every task whose bundle and artifact paths are independent, launch its Codex interactive TUI GPT-5.6 SOL @ xhigh and Claude Code Opus 4.8 @ xhigh effort (`claude-i`) lanes before waiting on any generated-task review lane. The implementation-order prefix does not impose review order; it controls later implementation. Serialize a task's review only when its bundle genuinely depends on unresolved findings from an earlier task review, and record that dependency. Patch affected docs, regenerate only affected bundles, and rerun both lanes for each changed task. A started session is not approval; save a pending/blocker artifact and report the flow as incomplete if the required interactive Codex TUI session has no passing, parseable, attested verdict.

### Plan cleanup

For `plan-clean` style work, classify task directories as complete, incomplete, or ambiguous. Use dry-run first. Delete only confirmed paths inside `tasks/`, and only when all checkable plan items including verification are complete.

When the user asks to re-examine incomplete or ambiguous task directories, do a read-only **codebase audit**, not just a checkbox recount. Task docs can drift: stale unchecked TODOs may remain after a completed implementation, while all-checked tasks can still be incomplete if current code violates the spec or focused tests fail. Read the task docs, extract acceptance criteria, inspect the current code/tests (and referenced cross-repo surfaces when applicable), run proportional focused verification when safe, then classify as complete, complete-with-caveat, incomplete, or parked/deferred. Use `references/plan-clean-codebase-audit.md` for the detailed pattern and red flags.

If the audit finds that current source implements a newer/reset contract while old phase TODOs describe a superseded hybrid/migration path, use `references/stale-task-reset-reconciliation.md`: reconcile the task docs as completed/superseded/deferred instead of blindly coding obsolete checkboxes, run focused verification, and save fresh final review artifacts when the workflow requires them.

## Cross-Cutting Rules

- Planning output must be concrete enough for another capable agent to execute without rediscovery.
- For indexed repositories, use Codebase Memory MCP as the first source-discovery pass in plan-doc/plan-code work: check indexed projects/status, then prefer graph/code search and path tracing before direct grep-style scans. Use direct file tools for exact reads, untracked/generated files, or when the index is missing/stale; if skipped, say why. Avoid hardcoding machine-specific Codebase Memory project names in durable task docs or repo instructions because different machines can index the same repo under different names.
- When writing a copy-paste handoff prompt for a host-side developer/agent from inside the Hermes `/workspace` mount, translate paths to the recipient's filesystem view, but do not assume a single Buffdemy host convention. Ask once or follow the user's latest correction exactly (for example a user may want `/workspace/dev/...` rendered as `~/workspace/dev/...`, not `~/dev/...`; they may later reverse that for a host-side agent). Keep internal Hermes tool paths unchanged unless the active workspace tag says otherwise.
- For copy-paste handoff prompts, avoid nested Markdown code fences that can break rendering around path blocks. If the user reports broken Markdown or asks for plain text, regenerate the whole prompt as plain text with simple headings and un-fenced command/path lines.
- Do not hide unresolved decisions; mark them as gates.
- Preserve out-of-scope findings for later triage instead of silently dropping them.
- Execution claims require real test/build/tool output.
- For `/plan-code` verification inside disposable Docker containers, if known-good credentials or test URIs arrive inside the container as redaction placeholders, stop retrying inline `docker create -e` / `docker exec ... export` variants. Use the TDD skill's `references/docker-secret-safe-test-runners.md` pattern: copy in a tiny runner script that constructs the env var inside the container, then run the real package-local test/build command through it.
- For `/plan-code` focused RED/GREEN runs in stale disposable images, avoid chasing missing-module failures one file at a time. Copy the current app/package source subtree and package-local config into the container first, then rerun from the package directory so RED reflects product behavior. See the TDD skill's `references/disposable-container-monorepo-red-green.md`.
- Cleanup is conservative: ambiguity means keep or ask, not delete.
- When a user asks to remove a completed task directory after commit/push, first verify the latest commit contains the task artifacts and the branch is synced with upstream, run `git rm -r --dry-run -- tasks/<slug>`, confirm the dry-run lists only that directory, then apply `git rm -r -- tasks/<slug>`. Report the staged deletion separately from committing/pushing it.

## Mid-task Contract Changes

- When the user changes requirements during `/skill plan-code`, follow `references/mid-task-contract-changes.md`: test the new contract, remove stale compatibility paths, update plan artifacts, rerun verification, and regenerate/re-review final bundles.
- When the change is specifically “this is pre-service; no backward-compat code; DB/index can be reset,” follow `references/pre-service-no-compat-plan-code-cleanup.md`: tighten producer/message/consumer/model boundaries, remove old-shape fixture support, delete disposable rewrite/runbook artifacts before commit, and regenerate review bundles from current file contents so deleted compatibility prose is not preserved as live evidence.
- When a backend/API gate resolves with a simplified generic selector contract, refresh the blocked frontend plan before coding: write `backend-contract.md`, update spec/TODO/progress, mark stale handoff prompts/review bundles as historical, and clarify that “hydration” may simply mean resolving stored IDs through the normal public lookup while save payloads stay ID-only. See `references/generic-selector-search-and-identity-apis.md`.
- When task docs created by the agent contain an over-specific TODO that is not actually required by the user's source instructions and would broaden the public/API contract, do **not** implement the broader behavior just to satisfy the checkbox. Re-read the source instructions, keep the narrower requested contract, and patch the task docs before review to document the intentional deviation and why the generated TODO was not implemented.
- If file/terminal tools become inconsistent during a mandatory `/plan-code` review or finalization step (for example minimal commands are interrupted, file reads contradict earlier state, or the active checkout cannot be verified), fail closed: stop making edits/review claims, report the exact blocker, and resume only after tool access is stable. Do not fabricate review artifacts or mark gates complete from memory.
- When a final artifact-consistency review is used to validate completed task docs and review artifacts, avoid self-referential stale loops: either exclude the consistency artifact itself from the review scope and state that explicitly in the saved JSON, or create a placeholder before review and do not judge its timestamp/content as part of the same review. After rerunning reviews or writing final verdict artifacts, remove or clearly supersede stale duplicate review files so the task directory contains one canonical artifact per gate.

## Verification Checklist

- [ ] Mode was selected explicitly from the user's request.
- [ ] Plan/task docs include paths, commands, tests, and acceptance criteria.
- [ ] Execution updated progress and verified with real outputs.
- [ ] Cleanup used dry-run/classification before any deletion.
