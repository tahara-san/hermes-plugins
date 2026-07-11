---
name: simplify
description: Use after code has been written or modified, or when the user says /simplify. Reviews recently changed files for clarity, consistency, and maintainability while preserving exact behavior. Produces or applies narrow simplifications before required independent review.
version: 1.0.0
author: Hermes Agent (migrated from Claude Code code-simplifier agent)
license: MIT
metadata:
  hermes:
    tags: [refactoring, simplification, code-quality, claude-code-migration]
    related_skills: [requesting-code-review, plan-code, subagent-driven-development]
---

# simplify

Simplify and refine code for clarity, consistency, maintainability, and project fit while preserving exact behavior.

## When to Use

Use this skill:
- after a logical chunk of code is written or modified
- before required independent review in the `plan-code` workflow
- when the user says `/simplify` or asks to simplify/refine changed code
- after fixing review findings or build/test failures

In explicit `plan-code` delta rerounds, classify the fix before choosing scope: behavior-affecting or uncertain fixes require simplify on changed and semantically affected code before the delta review; confirmed doc-only non-behavioral fixes may use a focused simplify/doc-consistency pass as the reduced post-fix simplify tier; tiny mechanical code fixes should still get a narrow simplify pass on the edited file(s). Record the tier rationale so reduced ceremony is not mistaken for skipping `/simplify`.

Default scope is recently modified code. Broaden scope when the user requests it. If the user asks for a holistic simplify pass, a code-flow review, or says not to limit the target to git diffs, treat the surrounding feature/class flow as the scope and map entrypoints/providers/mutation boundaries before editing.

## Core Principles

1. Preserve functionality. Do not change behavior, outputs, public API, data shape, error codes, or side effects unless the user explicitly asks.
2. Simplify for clarity, not fewer lines. Explicit readable code beats clever compact code.
3. Follow project conventions over generic style advice.
4. Prefer narrow edits. Avoid broad refactors that increase risk.
5. Remove accidental complexity, duplication, dead code, redundant abstractions, and unnecessary nesting.
6. For endpoint flows, distinguish security/data-integrity guards from cosmetic/business-sanity guards. If the user or plan intentionally makes a path best-effort/no-validation, preserve the security boundary and prefer a concise inline ADR-style comment over reintroducing over-defensive checks.
7. Keep useful abstractions; do not inline everything blindly.

## Procedure

### Step 1: Identify Scope

Determine changed files from the user's list, current plan phase, or git:
- `git status --short`
- `git diff --name-only`

If the user asks for a holistic/code-flow simplify pass, do not use git diff as the boundary. Identify the feature's entrypoints, provider/state boundaries, shared UI controls, mutation/save boundaries, and smoke-critical interaction paths before deciding what to simplify.

If no changed files or flow targets are clear, ask which files or feature path to simplify.

### Step 2: Read Context

Read each target file and nearby project context/rules. For Buffdemy backend, honor AGENTS.md:
- use one fresh async error container per awaited `.catch` call
- `AppError` wraps caught errors with `err`
- use `debugHelper`, not `console.log`
- prefer `type` over `interface`
- no `any` without explicit approval
- preserve route/export/import conventions

### Step 3: Look for Simplification Opportunities

Check for:
- unnecessary branching/nesting or nested ternaries
- duplicated logic that can be safely centralized within the same scope
- overly broad abstractions created for a single use
- unclear names
- redundant comments or commented-out code
- inconsistent error handling or logging
- repeated validation/parsing that should follow existing patterns
- tests that are too brittle, too broad, or do not assert the behavior actually changed
- accidental scope expansion beyond the task
- hidden mutation boundaries where a helper builds a new value but never commits it (for example, missing `actions.set(...)` after array copy/splice)
- limit/guard drift across shared flows: if upload/drop/insert enforce a slot or count limit, copy/duplicate/menu actions should enforce the same limit at both UI and state-helper boundaries
- form-adjacent toolbar/dropdown buttons missing `type="button"`
- nested interactive elements introduced by simplification, especially picker cards wrapping previews that may contain buttons

### Step 4: Decide Apply vs Report

Apply changes directly when they are narrow, behavior-preserving, and clearly beneficial.

Report instead of applying when:
- simplification would change public behavior
- multiple design options are valid
- change crosses module boundaries beyond the current task
- tests/verification impact is unclear
- user asked for review-only output

### Step 5: Verify

After applying simplifications:
1. Re-read the diff.
2. Run targeted tests/build/typecheck when available and proportional.
3. For `buffdemy2-web` small UI/text-only changes, do **not** automatically run lint/tests/build; the user prefers batching verification later unless they explicitly ask for checks.
4. For navigation/app-shell layout restructures, treat the change as more than text-only: run focused i18n checks when labels change, targeted nav/profile tests when available, TypeScript when props/imports changed, and at least one responsive smoke/E2E check when desktop/mobile structure changes. See `references/buffdemy2-web-nav-simplification.md` for a captured verification pattern.
5. For Buffdemy2-web Article/ArticleComment editor-flow simplify passes, see `references/buffdemy2-web-editor-flow-simplification.md`: map entrypoints/providers/mutation boundaries, add focused regression tests for shared state bugs, run lint/typecheck, and re-run independent review after any must-fix.
6. If verification fails, fix only the simplification-caused issue or revert that simplification.

### Step 6: Report

Report:
- files inspected
- changes applied, if any
- notable simplifications intentionally not applied and why
- verification command/result, or why verification was skipped

## Output Style for Review-Only Runs

```text
Simplify review:
- KEEP: <code is already appropriately simple>
- APPLY: <specific change made or recommended>
- DEFER: <bigger refactor not worth doing in this task>
```

## Common Pitfalls

- Changing behavior while calling it simplification.
- Treating a concrete user request that uses the word “simplify” as only a meta code-quality review. If the user specifies a target behavior or UI structure (for example, simplifying a nav column by moving items into one block), implement and verify that requested behavior before doing optional code cleanup.
- When simplifying navigation, preserve intended responsive structure instead of forcing desktop and mobile to share identical containers. It can be correct for desktop to have one main nav block while mobile has top-bar right actions plus a bottom bar; verify each breakpoint against the user’s requested item placement.
- After context compaction or handoff, do not finish stale active-task text from the summary when the latest user message gives a newer or different simplification request. Re-anchor on the latest user message, then inspect current files/diff to determine scope.
- Refactoring beyond changed files and creating review noise when the user asked for a normal diff-scoped simplify pass.
- Under-scoping when the user explicitly asks for a holistic/code-flow review. In that case, inspect the surrounding feature path and shared state helpers, not just changed files.
- Treating independent review findings as optional after a simplify pass. If the review returns a must-fix that affects guards, mutation boundaries, or workflow contracts, apply the narrow fix, add a regression test where practical, and re-review until APPROVE.
- Fixing one path's guard while leaving a shared sibling action unguarded. Slot/count limits and similar invariants should be checked at every mutation entrypoint, including copy/duplicate actions.
- Removing explicit error handling required by project rules.
- Replacing readable conditionals with dense one-liners.
- For visual-only UI tweaks, treat wording like “remove button background color” literally: make the base background transparent and check hover/focus/variant classes do not reintroduce a background unless explicitly desired.
- Skipping verification after edits.
- Leaving incidental investigation changes behind during cleanup. When the user asks to remove a mock/sandbox/spike after deciding not to proceed, revert all artifacts from that investigation unless they explicitly ask to keep a production fix. Before saying cleanup is done, check `git status --short` and explain any remaining diff in plain terms.
- "Simplifying" direct submodule imports into broad barrel imports without checking side effects. In browser/jsdom test contexts, a barrel can pull in unrelated server/Node-only code; keep or restore direct imports when targeted tests prove the barrel import breaks the runtime. Buffdemy2-web example: status constants for Question components should use narrow imports like `~/models/base/question/schema/common` when the schema barrel would pull model code into jsdom mocks.
- Low-level package barrels can also create runtime-only ESM cycles when they eagerly re-export high-level helpers that import back into repositories/classes. If startup fails with a TDZ error like `Cannot access 'BaseRepository' before initialization`, inspect the import graph and prefer lazy public wrapper exports over moving many call sites or broadening imports. See `references/barrel-import-cycle-lazy-exports.md`.
- In Playwright/E2E specs, avoid importing production component/client/server barrels just to reuse constants or selectors. Test files execute in Node during discovery, so a harmless-looking component import can pull `server-only` code through client/server barrels and block the whole project before tests run. Prefer E2E helper constants (for example `src/tests/e2e/helpers/*`) or duplicated selector strings that are verified by browser behavior, then confirm with `npx playwright test --list --project=<affected-project>` before rerunning the focused spec.
- Treat process-global test doubles as complexity, especially Bun `mock.module(...)` in multi-file test runs.
- Treat process-global test doubles as complexity, especially Bun `mock.module(...)` in multi-file test runs. If a route/unit test mock leaks into later files, do not keep expanding the fake module with inert exports; prefer a route factory/dependency-injection seam or narrower local spies, then verify the exact combined-file repro that exposed the leak. For partial config/module mocks where focused tests pass but the full suite fails due to suite-order imports, use `references/bun-mock-module-suite-order-leakage.md`.
