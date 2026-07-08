---
name: plan-doc
description: Use when the user wants Hermes to create task planning documents before implementation (Claude Code /plan-doc style). Produces tasks/<task-name>/spec.md plus todo.md or phase TODOs, with decision gates, dependency/parallelization analysis, manual-handling notes, simplify review, and the default parallel Codex + Claude Code default Opus 4.8 (`claude-i`) review gate preserved for Hermes workflows.
version: 1.1.0
author: Hermes Agent (migrated from Claude Code planner plugin)
license: MIT
metadata:
  hermes:
    tags: [planning, task-docs, claude-code-migration, workflow]
    related_skills: [writing-plans, plan-code, plan-issues, simplify, requesting-code-review, claude-i]
---

# plan-doc

Create structured task documents under `tasks/<task-name>/` before any code is written.
This is the Hermes adaptation of the Claude Code `/plan-doc` workflow.

## When to Use

Use this skill when the user says or implies:
- `/plan-doc ...`
- "create a spec", "write a plan", "plan this feature", "spec this out"
- a non-trivial feature, fix, refactor, or system change should be documented before coding

Do not implement code in this skill. The output is planning files plus a kickoff prompt for `plan-code`.

## Hermes Adaptation Notes

Claude Code concepts map to Hermes as follows:

- `AskUserQuestion` -> use `clarify` when a blocking decision cannot be resolved from code or project rules.
- `Read` / `Glob` / `Grep` / `Write` / `Edit` -> use `read_file`, `search_files`, `write_file`, and `patch`.
- `Bash` -> use `terminal` only for git/project commands and verification.
- `EnterPlanMode` / `ExitPlanMode` -> no direct Hermes equivalent; preserve the same behavior by running a strict decision gate before writes and asking for approval when decisions materially affect the plan.
- `/simplify` -> load/use the `simplify` skill for a simplification pass.
- `/codex-chunk` -> use the default parallel review stack: Codex-style review via `requesting-code-review`/Codex/fresh reviewer plus Claude Code Opus 4.8 @ xhigh effort through `claude-i` (Opus 4.8 @ xhigh effort required). Preserve the Codex leg even if Codex CLI is unavailable by using the documented fallback reviewer.
- `/goal` -> include a kickoff prompt that sets a standing goal before `/plan-code`, so Hermes keeps advancing through every task, phase, review gate, and verification step until completion. The goal must allow stopping only for genuine blockers: unresolved user decisions, manual-handling requirements, unfixable verification failures, or user interruption.

## Procedure

### Step 1: Extract Task Info

1. Task name: use the argument if provided; otherwise derive a short kebab-case name from the task description. Max 4-5 words.
2. Task description: use the user's message. If missing, ask once for it.
3. Project root: run `git rev-parse --show-toplevel 2><null-device> || pwd`.
4. Output directory: `<project-root>/tasks/<task-name>/`.
5. If the output directory already contains `spec.md`, `todo.md`, `progress.md`, or phase TODOs, read those files first and update them in place. Treat `/plan-doc @existing-task-dir` as a plan refresh, not a duplicate-plan request; preserve completed structure where possible and add new decisions/scope/tasks explicitly.

### Step 2: Gather Context

1. Read project context files (`AGENTS.md`, `CLAUDE.md`, relevant app/package docs) if present.
2. Note user-provided logs, code snippets, error messages, and constraints.
3. Inspect likely touched files with `search_files` + `read_file` so the plan is grounded in code, not guesses.
   - If the user asks to plan fixes after a completed smoke/dogfood pass, first read the existing smoke log, screenshots/artifacts list, and any out-of-scope issue files. Treat those logged findings as the evidence source of truth; do not re-run destructive or state-mutating browser paths unless the log is missing a required claim. Keep the plan in planning mode only: no code edits, no fixture cleanup beyond what the smoke task already recorded, and explicitly cite the evidence files in `spec.md`.
   - If the user references an out-of-workspace context path that is missing or appears in a context warning, do not ignore it. Try to resolve the intended nearby/sibling path when accessible, record the corrected path and any uncertainty in `spec.md`, and ask only if the missing context cannot be recovered.
   - For Buffdemy Article ACL / comment-gating/public-preview plans, see `references/article-acl-comment-gating.md` for the known backend data-shape contract, public preview migration notes, SSR-preserving frontend touchpoints, and spec questions to ask when effective viewer permission is not exposed.
   - For Buffdemy subscription/billing frontend-view plans, see `references/buffdemy-subscription-billing-views.md` for known route choices, model/API areas, internal-payment UX boundaries, and pagination pitfalls.
   - For Buffdemy subscription checkout/profile CTA/Stripe return-page plans, see `references/buffdemy-subscription-checkout-flow.md` for checkout-session contract constraints, optional Stripe URL handling, relation-id matching, pending-context rules, modal/navigation guards, and verification checklist items.
   - For Buffdemy frontend plans involving backend `user.role` / feature gates, see `references/buffdemy-user-role-feature-gates.md` for the role matrix, feature-forbidden handling, parallelization pitfalls, and E2E user/context decision gates.
   - For Buffdemy notification frontend plans, see `references/buffdemy-notification-frontend.md` for REST-only v1 boundaries, backend route dependencies, feature-flag/disabled-route behavior, i18n registration, shared mock fixture, and final build verification checklist items.
   - For Buffdemy main content feed frontend plans, see `references/buffdemy-main-content-feed.md` for backend `GET /feed` V1 boundaries, no-WebSocket/no-client-composition rules, `feed.score` cursor behavior, metadata preservation, proxy validation, pagination stop behavior, and test checklist items.
   - For Buffdemy Tag List / tag feed / tag-combination follow frontend plans, see `references/buffdemy-tag-list-feed.md` for canonical `/tags` + `/tags/feed` + `/api/tags` + `/api/tag-follow` route shapes, backend contract gates, tag identity/combination normalization, filtered-feed no-client-composition rules, cache/auth safety, navigation affordance choices, i18n namespace wiring, and tests.
   - For Buffdemy API auth/cache/header plans, see `references/buffdemy-v1-auth-cache-policy.md` before deciding an endpoint should be public. V1 defaults app data APIs to auth-required; anonymous public caching is limited to individual published article responses; backend app code should not add caching logic; backend header tests/docs should preserve no-store/no-cache behavior for strict-auth endpoints.
   - For Buffdemy follow/unfollow frontend plans, see `references/buffdemy-follow-unfollow-frontend.md` for the user-follow app route/backend contract, strict mutation proxy requirements, profile sidebar UI touchpoints, dedicated E2E expectations, Feed backfill separation, and common pitfalls.
   - For Buffdemy E2E test-only Article fixture/seeding plans, see `references/buffdemy-e2e-article-fixtures.md` for the gate/auth/cleanup safety checklist and common planning pitfalls.
   - For existing-task plan refreshes, context-compaction continuations, or requests that may map to an already-created `tasks/<task-name>/` directory, see `references/plan-refresh-existing-task.md` for the reload/status/update-in-place workflow.
4. For React/client-component plans, also inspect the surrounding update paths: `React.memo` comparators, hook dependency arrays, prop sanitization, event lifecycles, and stale async callback guards. If the task changes behavior driven by a prop or external resource URL, explicitly include these update-path touchpoints in the plan so implementation does not only handle first render.
5. For test-only fixture/helper plans, inspect existing gated test-only routes, fixture helpers, target spec setup/cleanup paths, auth storage-state usage, and backend schema enums before writing the plan. If adding a destructive cleanup helper, make the fixture-scope proof explicit (for example: known fixture owner AND deterministic route-controlled markers) and explicitly plan migration of each affected spec's cleanup path, not just setup.

### Step 3: Blocking Decision and Manual-Handling Gate

Before writing files, identify:

- Open engineering decisions: library/framework choice, architecture pattern, data model/schema, public API shape, error policy, performance/resource trade-off, UX-visible behavior, scope boundary, migration/backward-compatibility shape.
- Manual-handling needs: repros, credentials, production state, UI visual checks, external services, hardware, load/perf checks, security/compliance judgement.

If project rules or existing code already settle a choice, do not ask. If genuine ambiguity remains, ask in one batched `clarify` round when possible. Present 2-4 concrete options with trade-offs.

If the user explicitly requests incremental questioning (for example "keep asking until you have enough data" or "ask one question at a time"), do not batch questions. Ask exactly one blocking question per `clarify` call, incorporate the answer, then decide whether another single question is still needed before drafting.

When the user proposes removing validation/sanity checks to simplify a flow, evaluate and document the boundary explicitly before planning implementation:
- separate security/authorization invariants from cosmetic/data-quality guarantees;
- preserve server-side security with authoritative ownership/permission checks and guarded write filters, not frontend assumptions;
- allow cosmetic misses only when wrong/missing data cannot modify unauthorized resources or violate durable invariants;
- record the decision provenance in `## Decisions`, including which checks are intentionally removed and which guards remain;
- require a concise inline ADR-style comment at the implementation point for intentional no-validation/no-sanity-check behavior, so future agents do not reintroduce over-defensive guards as mistaken hardening.

If the user explicitly says "just decide" / "use your judgment", decide and record each decision in `spec.md` tagged `(no user input — Hermes call)`.

### Step 4: Choose Document Structure and Parallelization Model

Use small structure for focused 1-3 phase tasks:
- `spec.md`
- `todo.md`

Use large structure for 4+ phases, multi-system changes, or long plans:
- `spec.md`
- `progress.md`
- `todo-phase-N.md` per phase

When unsure, prefer large.

Before writing TODOs, evaluate whether phases/tasks can be executed in parallel:
- Build a simple dependency graph from shared files, data migrations/schema changes, API contracts, generated artifacts, test fixtures, and review/verification dependencies.
- Group tasks that touch disjoint files or have one-way contract dependencies that can be mocked/stabilized safely.
- Mark tasks as **parallelizable** only when simultaneous implementation will not cause file conflicts, semantic drift, or duplicated review/verification work.
- For parallel groups with a shared helper, shared translation keys, or shared test fixture assumptions, define the exact mini-contract before dispatching workstreams. Examples: helper signature, i18n key names, auth refresh API shape, fixture user roles, and which test project/auth state owns each assertion.
- If parallel work is safe, write explicit instructions to run those groups simultaneously (for example with `delegate_task(tasks=[...])`) and then reconcile/review the merged result before moving on.
- If work must be serial, record the blocking dependency so `plan-code` does not waste time re-evaluating obvious sequencing.

### Step 5: Write `spec.md`

Save to `tasks/<task-name>/spec.md`.

Required sections:

```markdown
# <Task Title>

## Goal
<What this achieves and why.>

## Scope

### In Scope
- <item>

### Out of Scope
- <item>

## Decisions
<Only if decisions were captured. Include Q -> A and provenance.>

## Manual-Handling Notes
<Only if the user must act/provide context/verify manually.>

## Technical Approach
<Specific implementation approach, grounded in inspected code.>

## Expected File Changes

| File | Change | Description |
|------|--------|-------------|
| `path` | Create / Modify / Delete | reason |

## Dependency & Parallelization Plan
<Identify which phases/tasks are sequential vs independent. If any can run in parallel, explicitly say so and describe the safe parallel execution groups. If none can, explain the dependency that forces serial execution.>
```

For large plans, also include `## Implementation Rules` and `## Implementation Workflow` in `spec.md`. For small plans, put them in `todo.md`.

Implementation workflow must preserve this sequence:

1. Implement a serial phase or a documented parallel batch.
2. Run `simplify` on changed files and apply worthwhile simplifications.
3. Build one immutable review bundle, then run Codex-style review and Claude Code default Opus 4.8 (`claude-i`) review against that same bundle in parallel when safe.
4. Fix critical or worth-addressing warnings.
5. Repeat simplify -> review until clean or documented as intentionally ignored.
6. Run build/tests using project-appropriate commands.

### Step 6: Write TODO Documents

Small plan: `tasks/<task-name>/todo.md`

```markdown
# <Task Title> — TODO

## Phase 1: <Phase Name>
- [ ] <specific actionable step>

## Verification
- [ ] All tasks above completed
- [ ] Per-phase simplify -> default parallel Codex + Claude Code default Opus 4.8 (`claude-i`) review passes
- [ ] Holistic simplify -> default parallel Codex + Claude Code default Opus 4.8 (`claude-i`) review passes (skip if single-phase)
- [ ] Project build/test verification passes

---

## Implementation Rules
- Orchestrator uses Hermes in this session.
- Mandatory out-of-scope issue tracking is active: when warnings, issues, code smells, bugs, skipped items, follow-ups, or potential problems are encountered outside this task scope, do not silently ignore them and do not fix them inline unless explicitly requested. Before creating a new file, check for an existing matching issue and update it instead of duplicating it. Otherwise log each finding as `tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md`, or `tasks/out-of-scope-issues/<priority>/manual/<YYYYMMDD>_<short-kebab>.md` when human investigation/intervention is required. `<priority>` must be one of `critical`, `high`, `medium`, `low`, `proposal`, `other`. Each file must contain these sections in this order: **Issue**, **Location**, **Severity**, **Context**, **Suggested Fix**. Mention logged out-of-scope issues in the wrap-up.
- Evaluate phases/tasks for safe parallel execution before implementation. If phases/tasks are independent, execute them simultaneously (prefer `delegate_task` batch calls with complete, non-overlapping context) and reconcile their outputs before shared review/verification. If they are not independent, follow the documented serial dependency order.
- Use `delegate_task` for non-trivial code changes when helpful.
- Use `/goal` for execution: keep advancing through every task, phase, simplify/review loop, and verification step until the whole plan is complete. Do not pause between phases or ask whether to continue unless there is a genuine blocker: unresolved user decision, manual-handling requirement, unfixable verification failure, or user interruption.
- Add a completion-enforcement checklist to the plan: implementation is not complete until all task files have no unchecked executable items, progress docs match the code state, holistic simplify/review has run after the final code changes, final verification has passed or an external blocker is documented, and requested task-file cleanup has been performed.
- Add a resource-limit/resume protocol for long plans: after every phase or parallel batch, update task files immediately; before final review/verification, audit all TODO files for unchecked items; if Hermes is interrupted by context/tool-call limits, the next run must reload the task files and continue from unchecked items rather than accepting the previous progress summary as completion.
- No migration/backward-compatibility code unless explicitly requested.
- Prefer concise, elegant, production-ready solutions.

## Implementation Workflow
<same sequence from Step 5>

## Completion Enforcement
- [ ] The generated plan tells `/plan-code` to use `plan-code` reference `references/end-to-end-phase-execution.md` for completion/resume guardrails when executing multi-phase work.
- [ ] Every planned phase/task has been implemented or explicitly marked blocked by an unresolved user/manual/external decision.
- [ ] All `todo.md` / `todo-phase-N.md` files have been audited for unchecked executable items after the final code change.
- [ ] `progress.md` (if present) matches the task files and current code state.
- [ ] Per-phase or per-batch simplify -> default parallel Codex + Claude Code default Opus 4.8 (`claude-i`) review gates are complete.
- [ ] Holistic simplify -> default parallel Codex + Claude Code default Opus 4.8 (`claude-i`) review is complete after the last code change.
- [ ] Final project verification commands have passed, or any unfixable external blocker is documented with evidence.
- [ ] Requested task-file cleanup has run only after the completion audit passes.
- [ ] If a resource limit or context compression interrupts execution, the continuation prompt reloads the task files and resumes from unchecked items instead of relying on memory.
```

Large plan:
- `progress.md` lists phases and completion criteria.
- `todo-phase-N.md` contains the atomic tasks for each phase.

### Step 7: Review the Plan Documents

Before reporting completion, run simplification and the default parallel review gate on the plan docs:

1. Use the `simplify` skill to check whether the plan can be narrower, clearer, or less coupled.
2. Build one immutable plan-doc review bundle containing the task docs, relevant current-code context, package/test-script context, `git status --short`, and relevant untracked task files.
3. Run the Codex-style review leg via `requesting-code-review`, Codex, or a fresh `delegate_task` reviewer against that saved bundle.
4. In parallel when safe, run Claude Code through `claude-i` in interactive mode using the configured configured Opus 4.8 @ xhigh effort model. Request and verify Opus 4.8 @ xhigh effort. Verify the Claude Code TUI banner/status line before sending the substantive prompt and record the actual model/effort shown; if Claude Code cannot run, document the deviation/blocker and treat the gate as blocked unless the user waives it.
5. Save separate Codex and Claude Code default Opus 4.8 (`claude-i`) review artifacts plus one aggregate verdict under `tasks/<task-name>/reviews/`. The aggregate artifact must record bundle path, reviewer tool/model, both verdicts, static-scan status if applicable, verification status if applicable, and timestamp.
6. Revise on blocking findings and on non-blocking suggestions that materially improve execution safety, verification, blocker handling, or scope control.
7. If any review-driven doc change is applied, regenerate the bundle and rerun both review legs so the final report is not based on stale review artifacts.
8. If either reviewer times out, wedges, returns an incomplete/unparseable verdict, or cannot inspect the intended scope, treat that leg as failed/blocked; retry with a narrower bundle when practical. Do not claim the plan "passed" review unless both legs pass or the user explicitly waives one.
9. Iterate until clean or explicitly document ignored/waived warnings.

When the user asks for `/plan-doc`-style review after implementation has already happened, treat the saved plan as a completed handoff artifact, not as an active pre-implementation TODO. Update stale plan wording and commands to match the actual implementation, record the actual changed files, dependency/serial-vs-parallel assessment, simplify/review outcomes, final verification commands/results, static-scan result when relevant, and `git diff --check` result. Then rerun a doc-only independent review if those notes changed.

### Step 8: Final Report

Before the final report, especially after context compaction or a long planning session, re-ground the wrap-up from durable artifacts rather than conversation memory: check the task directory contents, read the current `spec.md` / `progress.md` / TODO files as needed, and verify the session TODO state is complete. Do not rely on a compressed summary to claim files, decisions, review status, or blockers.

Tell the user:

1. Files created.
2. Small vs large structure and why.
3. Technical approach summary.
4. Decisions captured (`Q -> A`) and provenance.
5. Manual-handling notes.
6. Dependency & parallelization assessment, including parallel groups or serial dependency rationale.
- Confirmation that plan docs passed simplify + default parallel Codex + Claude Code default Opus 4.8 (`claude-i`) review, including the aggregate review artifact path, or a concise note that a required review leg was blocked/waived.

### Step 9: Emit Kickoff Prompt

End every ready-plan `/plan-doc` response with a copy-pasteable prompt. This applies not only to the initial plan creation, but also to follow-up plan refreshes, backend-contract updates, independent/Claude/Codex review requests, or any later `/plan-doc`-related turn where the plan remains ready for implementation. If a follow-up changes or re-approves the plan, re-emit the kickoff prompt in the final answer.

End with a copy-pasteable prompt:

```text
/goal Complete tasks/<task-name> end-to-end: execute every unchecked task/phase, run any documented independent phases/tasks in parallel, run simplify and the default parallel Codex + Claude Code default Opus 4.8 (`claude-i`) review gates, fix worth-addressing findings, run verification, and clean up requested task files. Keep pushing forward without pausing between phases; stop only for unresolved user decisions, manual-handling requirements, unfixable verification failures, user interruption, or an infrastructure resource limit that prevents further tool calls.

/plan-code @tasks/<task-name>

- Evaluate the plan's Dependency & Parallelization Plan before coding; when tasks/phases are independent, implement them simultaneously and reconcile before shared review/verification.
- Automatically start next steps/phases/tasks unless a captured user decision or manual-handling step blocks progress.
- After every phase or parallel batch, immediately update the task TODO/progress files and session TODO state.
- Before final review, final verification, and cleanup, audit all task files for unchecked executable items; continue until none remain.
- If context compression or tool-call limits interrupt execution, the next run must reload `tasks/<task-name>/spec.md`, `progress.md`, and all TODO files, then resume from unchecked items.
- Push through to final completion of all planned work, simplify/review loops, default parallel Codex + Claude Code default Opus 4.8 (`claude-i`) review gates, verification, and requested cleanup under the `/goal` above.
- Remove the task files after completing the task.
- Do not create migration/backward-compatibility code unless explicitly requested.
```

Do not start implementation in `plan-doc`.

## Common Pitfalls

- Writing a plan without inspecting source files.
- Planning tests that only cover the surface symptom instead of the exact failure mode. If the suspected bug involves omitted optional fields being passed as explicit `undefined`, stale state, retry re-entry, serialization, or another subtle mechanism, require at least one regression test that exercises that mechanism directly; a happy-path partial update that would pass before the fix is not sufficient.
- Writing multi-command verification blocks that are not copy-paste safe. When commands change directories across packages/apps, use subshells like `(cd packages/foo && bun run build)` / `(cd apps/api && bun run build)` or explicitly reset to the repo root between commands; avoid sequential `cd a && ...` then `cd b && ...` blocks that fail because the shell remains in `a`.
- Planning only the happy-path file edit while missing update-path mechanics around it (for example React memo comparators, hook dependency arrays, prop sanitization, stale async callbacks, or library-managed DOM state).
- Silently choosing an architectural/API decision that should be surfaced.
- Treating missing Codex CLI or Claude Code default Opus 4.8 review as permission to skip the default parallel review stack.
- Putting vague TODOs like "fix errors" instead of atomic file/function-level tasks.
- Starting code implementation after writing the plan.
