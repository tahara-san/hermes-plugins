---
name: plan-code
description: Use when the user wants Hermes to execute an existing implementation plan (Claude Code /plan-code style). Loads tasks/<task-name> plan docs or an in-context plan, evaluates serial vs parallel execution, implements safe independent batches simultaneously, enforces decision gates, runs simplify before the default parallel Codex-style Hermes delegate + Claude Code Opus 4.8 @ xhigh effort (`claude-i`) review gate, verifies builds/tests, updates progress, and reports completion. Includes guidance for E2E fixture prerequisite gating in references/e2e-fixture-prerequisite-gating.md.
version: 1.1.1
author: Hermes Agent (migrated from Claude Code planner plugin)
license: MIT
metadata:
  hermes:
    tags: [implementation, planning, review-gates, claude-code-migration]
    related_skills: [plan-doc, simplify, requesting-code-review, subagent-driven-development, claude-i]
---

# plan-code

Execute a task plan phase-by-phase with strict review discipline. This is the Hermes adaptation of Claude Code `/plan-code`.

## When to Use

Use when the user says or implies:
- `/plan-code @tasks/<task-name>`
- "implement this plan"
- "start coding the plan"
- "execute the phases"

Works with either plan files under `tasks/<task-name>/` or an in-context plan.

## Enforcement Rule

Reference: `references/end-to-end-phase-execution.md` captures the completion/resume guardrails for multi-phase plans, context compression, E2E decision gates, final verification, and requested cleanup. For near-complete tasks, also use `references/last-mile-verification-invalidation.md` to avoid making small final edits after a passing gate without rerunning the affected verification/review. When a phase or batch has multiple mandatory reviewers, use `references/phase-review-loop-discipline.md`: a single concrete worth-addressing finding from any mandatory reviewer keeps the phase open until fixed, verified, and re-reviewed (or explicitly documented as accepted/ignored). When a frontend plan depends on backend APIs or explicitly forbids mocks/local approximations, also use `references/frontend-backend-contract-gating.md` before coding.

Every numbered step and every unchecked `- [ ]` item in the plan is a blocking requirement unless the user explicitly changes scope. Use `/goal` as the standing completion contract when it is present: keep pushing through every task, phase, simplify/review loop, fix, and verification gate until the whole plan is done. If the user invokes `/plan-code` without an explicit `/goal`, internally adopt the same goal-driven behavior instead of stopping after a phase summary. Before implementing, evaluate whether phases/tasks can safely execute in parallel; when they can, implement them simultaneously and then reconcile/review the combined result. Do not skip `simplify`. Do not run the default parallel Codex-style Hermes delegate + Claude Code Opus 4.8 @ xhigh effort (`claude-i`) review gate before `simplify` has run on the same changed files.

### Resource-Limit Rule

Tool-call, context, and session-compression ceilings are infrastructure limits, not valid plan stopping points. Since they cannot always be prevented, run long plans with a resumable execution discipline:
- Minimize tool calls by batching independent reads/searches/checks with `multi_tool_use`, `execute_code`, or narrow scripts when safe.
- After each phase or parallel batch, immediately update task TODO/progress files and the session `todo` state before starting optional exploration, so compression or interruption never loses the true phase state.
- Before starting any holistic review or final verification on a large diff, perform a quick remaining-work audit of all plan TODO files; do not rely only on the in-session TODO list.
- If remaining work is still executable, do not end with a progress-only summary. Either continue executing it, or, if the infrastructure has already refused more tool calls, explicitly report that the stop was resource-limit forced and include a copy-pasteable continuation prompt that reloads the task files and resumes from unchecked items.
- When the user explicitly asks for a final response because the maximum tool-calling iteration limit was reached, give a handoff-quality status summary instead of trying to continue. Separate: completed implementation, verified commands with real pass/fail results, known blockers/deferred decisions, and exact remaining executable steps. Do **not** imply the plan is complete when simplify/review/final cleanup or task-file reconciliation still remain.
- If a tool safety/confirmation guard refuses an action required to satisfy an executable checklist item and explicitly says not to retry or route around it, treat that as a hard infrastructure/safety blocker: document the exact blocked requirement in the task docs and session TODO, do not attempt the same outcome through another tool, and stop instead of marking the phase complete.
- If you ask the user to override or consent to a safety-guarded write/action and the clarification times out with a generic "use your best judgement" response, do **not** infer consent. Choose the safest non-action path: leave the blocker documented, preserve unchecked/blocked task state, and stop cleanly.
- After context compression/compaction or any handoff summary, treat in-memory state as suspect. The first substantive action must reload `tasks/<task-name>/spec.md`, `progress.md` if present, and every TODO file, then reconcile them against `git status`/the current diff before implementing or reporting completion.
- Treat "maximum tool-calling iterations reached" as an external interruption. It explains why work stopped, but it does not make the phase complete.

## Hermes Tool Mapping

- Use `read_file` / `search_files` to load plans and source.
- Use `write_file` / `patch` for edits.
- Use `terminal` for git/build/test commands.
- Use `delegate_task` for non-trivial implementation or fresh independent review.
- Use `clarify` only for unresolved blocking decisions.
- Use `todo` to track plan phases in the current Hermes session.

## Procedure

### Step 1: Load the Plan

For audit/inventory plans, also follow the checklist in `references/audit-inventory-checkpoints.md` to keep grep commands, exclusions, row counts, and classification labels internally consistent.

When the user names a plan-code reference such as `references/end-to-end-phase-execution.md`, treat it as a linked file inside this skill unless the repo visibly contains that path. Load it with `skill_view(name='plan-code', file_path='references/...')` rather than first trying to read `<workspace>/references/...`; many project workspaces intentionally do not have a top-level `references/` directory.

From files:
1. Read `tasks/<task-name>/spec.md`.
2. Read `todo.md`, or `progress.md` plus all `todo-phase-N.md` files.
3. Extract phases, tasks, verification requirements, implementation rules, manual-handling notes, decisions, dependency/parallelization instructions, and any mandatory out-of-scope issue tracking rules.
4. If the plan omits out-of-scope tracking details, still apply the project/user policy: when warnings, issues, code smells, bugs, skipped items, follow-ups, or potential problems are outside the current task scope, do not silently ignore them and do not fix them inline unless the user explicitly asks. Before creating a new file, check for an existing matching issue and update it instead of duplicating it. Log each non-exempt finding as a separate markdown file at `tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md`, or `tasks/out-of-scope-issues/<priority>/manual/<YYYYMMDD>_<short-kebab>.md` when human investigation/intervention is required. `<priority>` is one of `critical`, `high`, `medium`, `low`, `proposal`, or `other`. Each file contains these sections in order: **Issue**, **Location**, **Severity**, **Context**, **Suggested Fix**. Mention logged out-of-scope issues in the wrap-up. **Exception:** do not create or update an issue file solely for GitHub Dependabot alerts or security-advisory counts; mention them briefly in the wrap-up only when relevant, or use GitHub/`gh`/`npm audit` to triage or fix them only when the user explicitly asks.

From context:
1. Extract phases and tasks from the user's plan.
2. If phases are not explicit, organize them into logical phases and confirm only if the breakdown changes scope.

Create a Hermes `todo` list for the phases/tasks. If the invocation included an active `/goal`, copy its completion conditions into the session TODO framing. If no `/goal` is active or visible, synthesize this internal standing goal: complete every unchecked task/phase, all mandatory simplify/review iterations, final verification, and any requested task-file cleanup; stop only for unresolved user decisions, manual-handling requirements, unfixable verification failures, or user interruption.

Before coding, evaluate the plan for safe parallel execution even if the plan did not include an explicit Dependency & Parallelization Plan:
- Build a dependency graph from changed files, public contracts, schemas/migrations, shared generated artifacts, fixture setup/cleanup, and verification/review gates.
- Identify independent phases/tasks with disjoint write sets or stable one-way contracts.
- Group independent work into simultaneous implementation batches; prefer `delegate_task(tasks=[...])` for non-trivial batches, giving each worker complete context, explicit file ownership boundaries, out-of-scope logging rules, and instructions not to edit outside its assigned scope.
- Do **not** parallelize tasks that touch the same files, depend on unimplemented contracts, alter shared schemas consumed by other pending tasks, or would make review findings hard to attribute.
- Record the chosen execution model in the session `todo` framing or task progress docs when docs exist: either `parallel batch: <items>` or `serial because: <dependency>`.

### Step 2: Execute Phases/Tasks (Serial or Parallel)

Auto-advance between phases/tasks under the active `/goal`/internal standing goal. Do not pause for "ready to continue?" after a phase completes, do not end the turn with only a progress summary when executable plan work remains, and do not ask whether to proceed to the next unchecked item. Stop only for a blocking decision/manual-handling gate, failed verification that cannot be resolved with available tools, or user interruption.

If the parallelization evaluation found independent work, execute each independent batch simultaneously:
- Launch the batch with `delegate_task(tasks=[...])` when the work is non-trivial and file ownership can be cleanly divided.
- Keep each worker's scope narrow: assigned phase/task, allowed files, required tests/checks, project rules, and out-of-scope issue policy.
- Require each worker to return verifiable handles: files changed, commands run, status, and unresolved findings.
- After all workers return, inspect the combined diff, resolve integration conflicts, update shared TODO/progress docs, then run simplify and independent review over the combined batch before starting dependent work.
- If a worker reports a dependency conflict or writes outside its assigned scope, stop parallel execution for that batch, reconcile manually, and continue serially if needed.

For each serial phase or parallel batch:

#### 2a. Decision Gate

Before and during implementation, stop and ask when the plan does not settle a non-trivial choice:
- library/framework, architecture, schema/data model, API shape, error policy, performance trade-off, UX behavior, scope boundary, migration/backward-compatibility, or manual-handling need.

Do not ask for mechanical choices already dictated by project conventions or nearby code.

If the user explicitly says "just decide" for this task, decide and record the choice under `## Decisions` in `spec.md` tagged `(no user input — Hermes call)`.

If the user asks for "fresh eyes", "review the plan", or similar before implementation, dispatch an independent reviewer before coding. Give the reviewer the proposed implementation shape, relevant current code, project rules, and specific questions. Incorporate the review into the plan or out-of-scope issue before proceeding; do not treat the original plan as approved if the reviewer finds semantic changes or missing edge cases.

If the user explicitly says "just decide" for this task, decide and record the choice under `## Decisions` in `spec.md` tagged `(no user input — Hermes call)`.

When implementing a plan that intentionally removes validation/sanity guards, preserve the documented security/data-integrity boundary instead of reintroducing broad defensive checks. If the plan calls for an inline ADR-style comment explaining best-effort/no-validation behavior, add it near the relevant code path so future agents and reviewers do not re-flag the intentional absence of guards as accidental.

#### 2b. Implement

Follow the plan exactly. For non-trivial code changes, prefer `delegate_task` with complete task context; use batch delegation for independent tasks that the parallelization evaluation marked safe to run simultaneously. Keep edits scoped. Do not create migration or backward-compatibility code unless explicitly requested.

For this Buffdemy backend project, obey AGENTS.md rules: one async error container per await/catch, `AppError` uses `err`, `debugHelper` over console logging, `type` over `interface`, no `any`, singular kebab-case API route segments, and per-package Bun build commands.

#### 2c. Simplify (mandatory)

Run the `simplify` skill on this phase's or batch's changed files. Apply simplifications that reduce complexity or better match project conventions while preserving behavior. If no changes are needed, record that result.

#### 2d. Default Parallel Review Stack (mandatory)

After simplify, review all files changed in this phase or batch with the default two-reviewer gate:

1. Build one immutable review bundle that includes the implementation diff, relevant untracked files, task docs, verification evidence available so far, static-scan results, and the intended behavior contract.
2. Run the Codex-style leg via a fresh Hermes `delegate_task` reviewer using the `requesting-code-review` contract. This lane must use GPT 5.6 Sol @ xhigh effort; record the actual reviewer model/effort and fail closed on an unavailable or mismatched lane unless the user explicitly waives or approves a substitution. Never call a local Codex binary.
3. In parallel when safe, run Claude Code through `claude-i` in interactive mode using the configured configured Opus 4.8 @ xhigh effort model. Request and verify Opus 4.8 @ xhigh effort. Verify the Claude Code TUI banner/status line before sending the substantive prompt and record the actual model/effort shown; if Claude Code cannot run, document the deviation/blocker and treat the gate as blocked unless the user waives it.
4. Save separate Codex-style Hermes delegate and Claude Code Opus 4.8 @ xhigh effort (`claude-i`) artifacts plus an aggregate verdict for the phase/batch review when the plan requires durable review artifacts. The aggregate verdict must record bundle path, reviewer tool/model, both verdicts, static-scan status, verification status, and timestamp.

If a holistic review or either review leg times out on a large diff, do not treat the timeout as a pass and do not abandon review. Retry with smaller scoped review batches divided by concern/write set (for example setup/config, helpers/specs, issue logs), then reconcile findings across the batches before completion.

Treat reviewer output as evidence, not final truth. If a reviewer reports a surprising failure or out-of-scope issue, verify it directly when practical before changing scope, logging a durable issue, or reporting the warning as still active. If later verification disproves or resolves a reviewer-reported issue, remove the transient issue file instead of preserving stale noise.

Fix CRITICAL findings and worth-addressing WARNINGs from any mandatory reviewer, then re-run the affected verification plus `simplify` and both review legs on a regenerated final bundle. Treat the review gate as a union of findings across simplify, Codex-style review, and Claude Code Opus 4.8 @ xhigh effort review: one concrete unresolved worth-addressing finding means the phase/batch is still in progress even if the other reviewers approved. Iterate until clean or the user explicitly accepts documented ignored warnings.

When the user explicitly requires Claude Code review for every `/plan-code` review gate, run it after each phase or parallel batch in addition to `simplify` and independent/Codex-style review, and run a holistic Claude Code review before final verification/cleanup. Do not treat an earlier phase Claude Code review as satisfying the holistic gate, and do not move to the next phase after patching Claude findings until affected verification plus the required review set have been rerun.

When a mandatory Claude Code review prompt needs substantial context, write the prompt/context to a temporary file and invoke Claude with stdin or a short file-referencing prompt instead of embedding the full diff/context in shell arguments. If Claude exits due to `Argument list too long`, `error_max_turns`, timeout, or another resource ceiling, that is not a review pass: retry with a shorter file-based prompt or split the review by concern/write set, then reconcile findings before marking the gate complete.

#### 2e. Update Progress

Check off completed items in `todo.md` or `todo-phase-N.md`. If a large plan has `progress.md`, mark phase or batch status there too. Update the session `todo` list.

Progress updates are mandatory before moving to the next phase or optional review loop:
- Re-read or search the relevant task file to confirm no unchecked item remains in the just-completed phase.
- If implementation work for a later phase was pulled forward, mark that later phase's concrete checklist items too; do not leave task docs stale just because the code is already done.
- If a planned item is intentionally blocked by an external prerequisite or user decision, mark it in the task file as blocked/skipped with the exact blocker and verification substitute, not as silently pending.
- Do not bulk-convert every unchecked checkbox to checked just to make the final audit pass. Executable completed items may be checked; external/manual/E2E/live-service items should remain visibly documented as blocked/skipped (or use the plan's explicit blocked marker) with evidence, so progress files distinguish implemented work from unavailable verification.
- If review or verification produces any code/doc changes after a task file already says holistic review or final verification is complete, immediately reset the affected review/verification/cleanup checkboxes and progress text to pending/in-progress before rerunning gates. Do not leave optimistic “passed/complete” wording in `progress.md` or phase TODOs while the post-fix review loop is still active.
- If task docs include both a main checklist and a completion-enforcement checklist, keep them consistent at every stage. It is acceptable for both to show pending while gates are rerunning; it is not acceptable for one section to claim completion while another says final verification is pending.
- Do not pre-check future cleanup or final-audit items with wording like "to be satisfied after cleanup." A checked box means the action already happened. If the next required action is cleanup, leave that checkbox pending until the guarded deletion/audit actually runs; otherwise a later resource-limit stop can leave task docs falsely claiming completion.
3. If task cleanup was requested, do not perform cleanup until this audit shows every required item is complete or explicitly blocked by a user/manual decision.
4. If the plan has a separate completion-enforcement checklist (often in `progress.md`), close that checklist with evidence before cleanup. A phase TODO audit alone is not enough; the cleanup guard should check both per-phase TODOs and completion criteria. Cleanup-related criteria should be checked only after the cleanup action has actually completed.

### Step 3: Holistic Review

For multi-phase plans, after all phases:
1. Run `simplify` on all files changed across all phases.
2. Run the default parallel Codex-style Hermes delegate + Claude Code Opus 4.8 @ xhigh effort (`claude-i`) review stack on all changed files together, using one saved final bundle when safe.
3. Fix -> simplify -> review until clean.
4. Document intentionally ignored warnings in `tasks/<task-name>/ignored-warnings.md`.

Skip only for single-phase plans.

### Step 4: Build/Test Verification

Run the project-appropriate final verification. Use plan-specified commands if present. Otherwise infer from the repo.

If the user explicitly scopes out E2E/live backend verification because a backend or external dependency is not ready, do not block completion on E2E. Instead, verify with the strongest available non-E2E gates (targeted unit/component tests, TypeScript, lint/i18n checks, and production build) and clearly report that E2E was intentionally skipped by user instruction.

When a repository-wide test command fails with broad harness/environment failures that appear unrelated to the task, distinguish regression from baseline before treating it as blocking. Use `references/baseline-verification-comparison.md`: capture status first, run a guarded stash/pop baseline probe (including untracked task files when necessary), compare the clean-baseline command output, and verify the worktree was restored. If the baseline fails the same way, log/update an out-of-scope issue and rely on targeted passing tests plus other relevant gates for this task; if the failure is new, fix it before completion.

For Buffdemy backend, avoid root `bun run build` because of the known Bun workspace filter ENOENT regression. Use per-package build commands, and in Docker run app commands in the matching service container so bind-mounted files and package scripts are current:
- API: `docker compose exec -w <container-workdir>/apps/api api bun run build` and `docker compose exec -w <container-workdir>/apps/api api bun test`
- Outbox processor: `docker compose exec -w <container-workdir>/apps/outboxProcessor outbox-processor bun run build` and `docker compose exec -w <container-workdir>/apps/outboxProcessor outbox-processor bun test`
- Unified consumer: `docker compose exec -w <container-workdir>/apps/unifiedConsumer unified-consumer bun run build` and `docker compose exec -w <container-workdir>/apps/unifiedConsumer unified-consumer bun test`
- Shared packages mounted in the API container can use `docker compose exec -w <container-workdir>/packages/<pkg> api bun run build` / `bun test`.

For Buffdemy backend Mongo/repository tests, prefer the same containerized verification path when the test needs the compose MongoDB/replica-set environment. If a host-side `bun test` fails before assertions with minimal output or Mongo connectivity symptoms, rerun the focused test inside `docker compose exec -w /app/packages/<pkg> api ...` before treating it as a code regression. Capture the passing in-container command in the verification summary instead of preserving host connection details or secrets.

When refactoring MongoDB repository methods that combine optional `ClientSession` with multiple writes, consult `references/buffdemy-mongodb-session-bulk-write.md` for the session-safe bulk-write checklist.

When a Buffdemy backend plan performs a clean-slate schema split (for example moving Article/Comment canonical content into `{parent, language}` content-row collections with no legacy tolerance), consult `references/buffdemy-clean-slate-schema-split.md`. In particular: stored document schemas must require the new fields while create schemas provide defaults, update schemas must derive from default-free bases, source-kind row replacement must clear stale optional metadata, and broad stale tests must be updated in the same phase. For route/test migration and downstream caller details around parent content fields, test factories, response media population, delete responses, feed language filtering, outbox/search payloads, and graph/search props schemas, also consult `references/buffdemy-content-row-route-migration.md`.

For Buffdemy frontend/media-player work, prefer narrow imports that avoid pulling server-/Node-oriented barrel side effects into jsdom/browser tests. For example, if a browser-facing file only needs `AppError`, import from `~/libs/appError` rather than a broad `~/libs` barrel unless the targeted Vitest suite proves the barrel is safe in that context.

For Buffdemy React 19 component tests, if `@testing-library/react` render fails with `TypeError: React.act is not a function`, follow the existing local pattern used by nearby tests: create a DOM container, render with `createRoot` from `react-dom/client`, wrap `root.render()` and `root.unmount()` in `flushSync` from `react-dom`, and clean up containers in `afterEach`. Do not change global test setup or production imports just to work around this per-suite compatibility issue.

When directly unit-testing Buffdemy client components that call `useTranslations`, mock `~/components/common/useTranslations` in the test instead of requiring a full `next-intl` provider. Prefer narrow production imports from `~/components/common/useTranslations` rather than the broad `~/components/common` barrel in browser/jsdom-facing components when the barrel pulls Node/server-adjacent modules into tests.

For Buffdemy frontend pages that add EN/JA translation keys, run a final changed-component scan for hardcoded visible English copy (`/ month`, `subscribers`, button/dialog labels, empty states, notices) after the first i18n pass. Reviewers will fail closed if any user-visible copy remains hardcoded in Japanese-capable UI. Avoid deriving translated dialog titles from English button labels (for example `buttonLabel.toLowerCase()`); use dedicated translation keys or localized action labels. When translation strings interpolate values, use next-intl ICU placeholders (`{name}`), not Handlebars-style double braces (`{{name}}`); add or run a real-message `createTranslator` regression test plus `check:i18n` guard for touched keys. See `references/buffdemy-next-intl-placeholders.md` for the proven pattern.

For Buffdemy Playwright/E2E helpers, do not import constants from React component barrels when a test-only copy is sufficient. Component barrels can pull client/server model trees and trigger `server-only` import failures during Playwright test discovery. Put stable test IDs or fixture constants in `src/tests/e2e/helpers/*` (or another test-only module) and import from there instead.

When drafting Buffdemy Playwright/E2E specs before the backend or fixture routes are ready, consult `references/buffdemy-draft-e2e-before-backend.md`. Gate the suite with an explicit env var so it is skipped by default, run static checks only, document the future test-only fixture contract in a helper, use regex request interception for query-string failure paths, scope status assertions to the mutated card, and require paginated fixture cardinality to exceed the page size before load-more assertions.

When implementing Buffdemy frontend ACL/privilege gating, consult `references/buffdemy-frontend-acl-gating.md`. In particular: update API source schemas as well as UI/domain model schemas, cover permalink/deep-link comment paths separately from normal article rendering, test readable-but-not-creatable comment states, and verify new AppError-code toast mappings plus EN/JA translation parity.

When migrating Buffdemy frontend pure-read Server Actions to REST/App Route GET boundaries, consult `references/buffdemy-rest-server-action-boundaries.md`. Cover the new App Routes and client callers, add/extend static boundary enforcement for both `src/client/**` and shared client-used `src/models/**`, search/delete stale GET Server Action exports, and watch for unsupported `api.fetch` cache hints plus stale schema shims.

When implementing Buffdemy article/comment ACL E2E coverage that needs server-side fixture setup, also consult `references/buffdemy-article-comment-acl-e2e-fixtures.md`. Use narrow gated test-only fixture routes, stable email-based ownership checks, fail-closed cleanup identity checks, server-side privilege verification before UI assertions, and separate normal-rendering vs permalink/deep-link coverage.

When implementing Buffdemy owner comment/reply privilege E2E coverage, also consult `references/buffdemy-owner-comment-privilege-e2e.md`. Preserve the fail-closed backend precondition that `article.privileges.comment.create === true` is authoritative for owners even when raw comment ACL is closed or deny-lists the owner; if the local backend returns `false`, log/update an out-of-scope backend contract issue rather than weakening frontend expectations or adding client-side ACL fallbacks.

When adding or debugging Buffdemy article/comment ACL fixture routes that mutate article ACL, also consult `references/buffdemy-e2e-acl-fixture-write-shape.md`. In particular: backend article updates need ACL write-shape rules (`allowedAudiences` plus `users.allow/deny`), restricted-read fixtures should derive creator allow-lists from the created article owner id, cleanup ownership checks should use exact email or exact owner/session id rather than display names, and user2 Playwright specs that seed with user1 storage need both setup dependencies.

When migrating Buffdemy article/comment Playwright suites from editor-driven setup to API-based article seeding, consult `references/buffdemy-e2e-api-article-seeding.md`. Preserve UI-driven comment/reaction behavior under test, gate fixture routes with `TEST_E2E_AUTH_HARDENING`, add route unit coverage, and verify cleanup ownership by email when available.

When verifying Buffdemy test-only E2E fixture routes, remember that a 404 from `/api/test-only/*` usually means the running app process lacks the opt-in gate env (`TEST_E2E_AUTH_HARDENING=1`) even if the source code and unit tests are correct. Verify against the same already-authenticated base URL/process whenever possible; changing to a new port/server can invalidate Playwright auth setup or reuse stale storage state. Prefer restarting the actual E2E app/container with the gate enabled and then regenerating auth state via the normal setup project, instead of mixing `--no-deps` with an alternate base URL.

When frontend E2E fixture routes proxy to backend `/test-only/*` endpoints, consult `references/buffdemy-frontend-test-only-proxy-routes.md`. In particular: if a frontend `/api/test-only/*` call returns JSON whose `content.path` is the backend `/test-only/*` path, the frontend proxy likely resolved and the missing route/env is in the backend process; verify the backend endpoint before continuing to debug App Router route discovery. Before calling a backend feature “missing”, inspect the backend docs and route registry/source to distinguish production endpoint availability from a missing deterministic test-only fixture route. If production routes exist but fixture scenarios require states public APIs cannot create (bulk synthetic users, arbitrary immutable billing statuses, cleanup), report that narrower fixture/support gap and provide a backend handoff prompt rather than implying the production structure is absent.

For Buffdemy model/schema-only Vitest files that import model classes or server-adjacent aliases, add `// @vitest-environment node` at the top when the repo default jsdom environment pulls in incompatible browser/runtime shims (for example `ERR_UNKNOWN_BUILTIN_MODULE: No such built-in module: node:`). Prefer the narrowest per-file environment override over changing global Vitest config or weakening imports in production code.

When implementing Buffdemy subscription/billing views or models, consult `references/buffdemy-subscription-billing-views.md`. In particular: preserve the creator/subscriber/billing route taxonomy, distinguish visible “disable” wording from deferred backend disable semantics, keep API-source schemas in backend wire shape and instance schemas in runtime shape, transform nested date fields (not just top-level dates), avoid schema defaults that mask required backend fields such as subscription stats, and regression-test both runtime parsing and `getInitProps()` serialization.

When implementing Buffdemy backend test-only subscription/billing fixtures, consult `references/buffdemy-test-only-subscription-billing-fixtures.md`. Use fail-closed production/env gating, strict auth limited to the default E2E user1, repository-backed deterministic tier/subscription/billing setup, explicit cleanup-boundary comments for default E2E users, stat repair, and targeted route tests plus per-app Docker build verification.

When a completed Buffdemy backend `/plan-code` task has been externally merged and the user wants the local checkout/dev stack updated, consult `references/buffdemy-post-merge-dev-deploy.md`: fetch/prune, fast-forward local `develop`, verify clean/ahead-behind `0 0`, recreate the Compose stack with explicit `NODE_ENV=development`, smoke `/health`, and leave local feature-branch cleanup alone unless requested.

If verification fails:
1. Fix the failure.
2. Run `simplify` on the fix.
3. Run the default parallel Codex-style Hermes delegate + Claude Code Opus 4.8 @ xhigh effort (`claude-i`) review stack on the fix.
4. Re-run verification.
5. Repeat until passing or blocked by a real external dependency.

### Step 5: Completion

1. Run a final task-file audit before claiming completion:
   - Read `tasks/<task-name>/spec.md` plus `todo.md`, or `progress.md` and every `todo-phase-N.md`.
   - Search for unchecked boxes (`- [ ]`), in-progress markers, TODO/FIXME-style placeholders, unresolved decision/manual-handling notes, and blocked verification items.
   - Resolve any executable item immediately; ask the user only for genuine unresolved decisions/manual work; document external blockers explicitly.
2. Mark all plan completion criteria checked and ensure the `/goal`/internal standing goal is satisfied. Do not report final completion while any planned task, review loop, verification gate, or requested cleanup step remains executable.
3. If the kickoff requested cleanup, remove completed task files/directories only after verifying they are inside `<project-root>/tasks/` and the plan is complete. Prefer a small Python `Path.resolve()` + `shutil.rmtree()` cleanup over shell `rm -rf`; it is easier to audit, avoids shell quoting/race mistakes, and still gives an explicit inside-`tasks/` guard.
4. Report:
   - phases completed
   - parallel batches executed, or why execution was serial
   - decisions surfaced and answers
   - warnings ignored and rationale
   - verification result
   - number of simplify and review iterations, plus the final aggregate review artifact path and verdict for Codex-style Hermes delegate + Claude Code Opus 4.8 @ xhigh effort (`claude-i`)
   - files changed
   - out-of-scope issues logged or updated (or state that none were found)

## Common Pitfalls

- Treating a reviewer JSON field like `passed: true` as the whole review result. If `worth_addressing` contains concrete code-quality or correctness findings, either fix them and rerun the affected gates or explicitly document why they are accepted/ignored before moving on to Claude/final verification.
- Running review before simplify, or running only one leg of the default Codex-style Hermes delegate + Claude Code Opus 4.8 @ xhigh effort (`claude-i`) stack when both are required.
- Treating a general "don't ask questions" preference as a per-task "just decide" decision bypass.
- Moving to the next phase while TODO/progress files still show unchecked phase items.
- Using a stale review result after fixing findings.
- Letting a clarification timeout override an explicit user-signoff/manual checkpoint.
- Building audit inventories with a broader cross-check command than the scoped command used to generate rows.
- Running a Docker app build/test from the wrong service container (for example, outbox/unified commands in the `api` container); this may read stale image files instead of the app's live bind mount, so rerun in the matching service before treating it as a code failure.
- Misclassifying inline `.catch` rows as `bare-array`/`built-variable`, or double-counting nested Promise.all* style violations on the outer row.
- Deleting task files before final verification passes.
- Treating task-doc reconciliation as a durable deliverable when the kickoff explicitly requested task cleanup. In cleanup-bound `/plan-code` runs, update `spec.md`/`progress.md`/phase TODOs first so the audit has accurate evidence, run the guarded audit, then delete the task directory; do not expect those reconciled docs to remain in the final commit unless the user asked to preserve them.
- Letting cleanup audits search for bare words like `TODO` in headings, historical instructions, or already-checked lines and then block on false positives. For cleanup guards, treat unresolved work as unchecked/in-progress checkboxes at line start (for example `- [ ]`, `- [>]`) plus explicit `TODO:`/`FIXME:` placeholders; do not count task-file titles or completed checklist text as unresolved.
- Forgetting to close a separate `progress.md` completion-enforcement checklist before deleting task files. If cleanup is requested, mark those criteria complete with evidence first, then rerun the guarded audit and remove the task directory.
- Blocking cleanup on its own intentionally-unchecked cleanup checkbox. In cleanup-bound plans, the final pre-delete audit may find only cleanup-action checkboxes (for example “remove `tasks/<name>/` after audit” and “requested cleanup has run after audit”). Treat those as the allowed next action, not unresolved implementation work; then delete with an inside-`tasks/` path guard and verify the directory is gone.
- Building frontend UI against assumed backend behavior when the plan requires confirmed contracts. Confirm and document production search/popular/stats/follow semantics first; if required support is missing, stop rather than inventing local mocks or speculative fallbacks. See `references/frontend-backend-contract-gating.md`.
- Treating a safety/confirmation tool refusal as a normal transient failure. If the refusal explicitly says not to retry or use another tool, preserve the blocker in task docs and stop; do not mark tests or phase work complete by approximation.
- Making "small" final edits after a passing focused test/review gate without rerunning that gate. Test assertion hardening, import cleanup, or review-suggestion tweaks still invalidate the last verification; if execution budget is tight, update phase docs for the verified state first and leave optional hardening for the next run. See `references/last-mile-verification-invalidation.md`.
- After context compression, answering from a reconstructed mental summary plus `git diff` alone. For `/plan-code`, the task files are the source of truth; reload and audit them before claiming completion, especially when cleanup was requested.
- Letting an inherited shell `NODE_ENV=production` leak into Buffdemy dev-stack deployment. Force `NODE_ENV=development` for Docker/compose dev refreshes unless the user explicitly requests production.
- Treating a barrel-import cleanup as harmless during simplify/review. If targeted browser/jsdom tests fail after changing a direct submodule import to a broad barrel import, restore the direct import; barrels may pull unrelated Node/server-only code into client test bundles.
