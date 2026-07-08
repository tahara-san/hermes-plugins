---
name: writing-plans
description: "Write implementation plans: bite-sized tasks, paths, code."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, design, implementation, workflow, documentation]
    related_skills: [subagent-driven-development, test-driven-development, requesting-code-review]
---

# Writing Implementation Plans

## Overview

Write comprehensive implementation plans assuming the implementer has zero context for the codebase and questionable taste. Document everything they need: which files to touch, complete code, testing commands, docs to check, how to verify. Give them bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume the implementer is a skilled developer but knows almost nothing about the toolset or problem domain. Assume they don't know good test design very well.

**Core principle:** A good plan makes implementation obvious. If someone has to guess, the plan is incomplete.

## When to Use

**Always use before:**
- Implementing multi-step features
- Breaking down complex requirements
- Delegating to subagents via subagent-driven-development

**Don't skip when:**
- Feature seems simple (assumptions cause bugs)
- You plan to implement it yourself (future you needs guidance)
- Working alone (documentation matters)

## Bite-Sized Task Granularity

**Each task = 2-5 minutes of focused work.**

Every step is one action:
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

**Too big:**
```markdown
### Task 1: Build authentication system
[50 lines of code across 5 files]
```

**Right size:**
```markdown
### Task 1: Create User model with email field
[10 lines, 1 file]

### Task 2: Add password hash field to User
[8 lines, 1 file]

### Task 3: Create password hashing utility
[15 lines, 1 file]
```

## Plan Document Structure

### Header (Required)

Every plan MUST start with:

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### Task Structure

Each task follows this format:

````markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67` (line numbers if known)
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Planning From Out-of-Scope Issue Logs

When the user asks to convert logged issues into an implementation plan (for example `tasks/out-of-scope-issues/<priority>/` or a Claude Code `/plan-issues` style request):

1. Discover candidate issue files and apply the user's filter exactly.
   - Skip files with a `[skip]` / `skip` prefix when requested.
   - Skip `manual/` tier files; report them as intentionally not planned.
2. Read every included issue, normalize its title, location, severity, context, and suggested fix.
3. Deduplicate overlapping issues before planning; if one issue is a subset of another, group them into one task instead of creating parallel plans.
4. Inspect the target source and nearby tests before drafting; don't plan from the issue text alone.
5. Decide and document grouping, scope, out-of-scope boundaries, proposed files, error codes/API shape, and verification commands.
6. Preserve the user's review workflow in the plan: simplification review first, then Codex-style review, then tests/build. If the exact slash commands are unavailable, keep the same conceptual gates instead of dropping them.
7. Do not remove source issue files unless the user explicitly asks for cleanup behavior.
8. After implementation, distinguish generated task docs from source issue logs:
   - Mark the task `todo.md` complete when the implementation/review/verification steps are done.
   - Leave the original `tasks/out-of-scope-issues/...` files in place by default; they are audit/source records, not the completion marker.
   - If the user asks whether remaining issue files are complete, answer by classifying included vs skipped/manual files and cite the implementation task/commit that resolved the included files.

See `references/out-of-scope-issue-planning.md` for the Claude `/plan-issues` workflow shape and Hermes adaptation notes.

## Plan Review Gates

For plans that will drive code changes, especially issue-fix plans:

- Run a simplification pass before external/independent review: ask whether the implementation can be narrower, clearer, or less coupled without losing correctness.
- Run an independent review of the plan before presenting it as final. Feed the reviewer the plan plus relevant source context, and revise on CRITICAL or worth-addressing WARNING findings.
- Re-review after revisions until the plan is clean or explicitly documents ignored warnings.
- Do not treat missing local setup for a reviewer tool as a reason to skip review; use an available independent-review mechanism while preserving the intended gate.

For high-risk migrations or destructive clean-slate resets:

- Encode the review policy directly in the plan and in every executable phase/TODO file, not only in the chat summary.
- If the user requires a specific reviewer such as Claude Code, make it mandatory for plan-doc review, every `/plan-code` phase/batch review, and the holistic final review. Do not let a generic "independent review" silently substitute for that named reviewer unless the user explicitly allows it.
- Make destructive boundaries explicit: `/plan-code` may plan around collection resets, but it must not run destructive database commands without separate explicit approval.
- If the plan assumes nuked collections or no legacy data, state that it must not create migration, backfill, backward-compatibility, dual-read, or legacy-shape-tolerance code.

## Writing Process

### Step 1: Understand Requirements

Read and understand:
- Feature requirements
- Design documents or user description
- Acceptance criteria
- Constraints

When the user asks to be interviewed for a spec, ask questions one at a time rather than presenting a long questionnaire. Use `clarify` for each question when available, proceed with the user's answer, and only default a decision after a timeout or when the user explicitly asks you to use judgment.

For underspecified product/design plans, interview incrementally instead of dumping a long questionnaire. Ask one high-leverage question at a time, and use `clarify` when available so the user can choose quickly. Continue until the decisions that affect architecture, file boundaries, rollout, and verification are pinned down; then inspect the codebase/reference behavior before drafting the plan.

### Step 2: Explore the Codebase

Use Hermes tools to understand the project:

```python
# Understand project structure
search_files("*.py", target="files", path="src/")

# Look at similar features
search_files("similar_pattern", path="src/", file_glob="*.py")

# Check existing tests
search_files("*.py", target="files", path="tests/")

# Read key files
read_file("src/app.py")
```

For bug-fix plans, do enough read-only inspection to identify the likely failing mechanism before drafting tasks. Trace the user-visible route/component to the smallest shared implementation, read the event/state handlers around the symptom, and name the suspected race/contract violation in the plan. When the symptom involves UI interactions, explicitly plan a regression test for the interaction ordering (for example `pointerdown` before `blur`, keyboard commit vs click commit, stale local state vs parent state) rather than only planning a browser smoke test. Keep the plan scoped to the shared component that owns the behavior unless inspection shows the route-level integration is stale.

When a bug report says stats/counts/discovery did not change after creating or updating records, trace both sides before planning: the stats read path and the record write/update path. Watch for canonicalization splits where the read path lowercases/NFKC-normalizes/dedupes keys but the write path persists raw user input, causing denormalized aggregates to split into multiple buckets. In the plan, distinguish prevention from repair: client-side normalization may prevent new web-originated drift, but backend canonicalization plus recount/backfill is required when existing aggregate rows are already split or non-web clients can write the same data. See `references/canonicalized-aggregate-bug-planning.md`.

### Step 3: Design Approach

Decide:
- Architecture pattern
- File organization
- Dependencies needed
- Testing strategy

For cross-repo data-model/API plans, explicitly separate canonical storage from compatibility/read-model fields, define which fields are authoritative vs derived caches, and include migration phasing. If the plan changes localized/user-authored content storage, use `references/content-i18n-data-model-planning.md` for the proven Article/ArticleComment i18n planning pattern: parent metadata plus per-type content collections, original-language detection metadata, translated/manual override rows, bounded feed filtering, flat public API compatibility, and independent architecture review.

### Step 4: Write Tasks

Create tasks in order:
1. Setup/infrastructure
2. Core functionality (TDD for each)
3. Edge cases
4. Integration
5. Cleanup/documentation

### Step 5: Add Complete Details

For each task, include:
- **Exact file paths** (not "the config file" but `src/config/settings.py`)
- **Complete code examples** (not "add validation" but the actual code)
- **Exact commands** with expected output
- **Verification steps** that prove the task works

### Step 6: Review the Plan

Check:
- [ ] Tasks are sequential and logical
- [ ] Each task is bite-sized (2-5 min)
- [ ] File paths are exact
- [ ] Code examples are complete (copy-pasteable)
- [ ] Commands are exact with expected output
- [ ] No missing context
- [ ] DRY, YAGNI, TDD principles applied

### Step 7: Save the Plan

```bash
mkdir -p docs/plans
# Save plan to docs/plans/YYYY-MM-DD-feature-name.md
git add docs/plans/
git commit -m "docs: add implementation plan for [feature]"
```

## Principles

### DRY (Don't Repeat Yourself)

**Bad:** Copy-paste validation in 3 places
**Good:** Extract validation function, use everywhere

### YAGNI (You Aren't Gonna Need It)

**Bad:** Add "flexibility" for future requirements
**Good:** Implement only what's needed now

```python
# Bad — YAGNI violation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # Not needed yet!
        self.metadata = {}     # Not needed yet!

# Good — YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### TDD (Test-Driven Development)

Every task that produces code should include the full TDD cycle:
1. Write failing test
2. Run to verify failure
3. Write minimal code
4. Run to verify pass

See `test-driven-development` skill for details.

### Frequent Commits

Commit after every task:
```bash
git add [files]
git commit -m "type: description"
```

## Common Mistakes

### Vague Tasks

**Bad:** "Add authentication"
**Good:** "Create User model with email and password_hash fields"

### Incomplete Code

**Bad:** "Step 1: Add validation function"
**Good:** "Step 1: Add validation function" followed by the complete function code

### Missing Verification

**Bad:** "Step 3: Test it works"
**Good:** "Step 3: Run `pytest tests/test_auth.py -v`, expected: 3 passed"

### Missing File Paths

**Bad:** "Create the model file"
**Good:** "Create: `src/models/user.py`"

## Execution Handoff

After saving the plan, offer the execution approach:

**"Plan complete and saved. Ready to execute using subagent-driven-development — I'll dispatch a fresh subagent per task with two-stage review (spec compliance then code quality). Shall I proceed?"**

When executing, use the `subagent-driven-development` skill:
- Fresh `delegate_task` per task with full context
- Spec compliance review after each task
- Code quality review after spec passes
- Proceed only when both reviews approve

## Remember

```
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
```

**A good plan makes implementation obvious.**
