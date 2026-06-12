---
name: simplify
description: "Use after code has been written or modified, or when the user says /simplify. Reviews changed files for clarity, consistency, and maintainability while preserving behavior."
version: 1.0.0
author: Hermes Agent + tahara-san
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [refactoring, simplification, code-quality, review]
    related_skills: [planning-workflows, plan-code, requesting-code-review, subagent-driven-development]
---

# simplify

## Overview

Run a behavior-preserving simplification pass after implementation and before independent review. The goal is not aesthetic churn; the goal is to reduce risk, remove accidental complexity, and make intent obvious.

## When to Use

- After code has been written or modified.
- Before final independent review in `plan-code`.
- When the user explicitly says `/simplify` or asks for cleanup.
- When a diff contains duplicated helpers, broad conditionals, overly defensive wrappers, or unclear control flow.

## Procedure

1. Inspect the current diff and changed files.
2. Identify simplifications that preserve exact behavior.
3. Reject broad refactors that increase risk.
4. Apply only narrow, well-scoped improvements.
5. Rerun focused verification for any changed code.
6. If a mandatory review already ran, treat simplification edits as post-review changes and rerun the relevant review gate.

## Good Targets

- duplicated setup that can be safely centralized;
- confusing names around newly added logic;
- dead branches introduced during iteration;
- tests that can assert the same contract more directly;
- unnecessary compatibility code not requested by the plan.

## Non-Targets

- style-only rewrites;
- large architecture changes;
- speculative abstractions;
- unrelated cleanup;
- behavior changes disguised as simplification.

## Verification Checklist

- [ ] Simplifications are behavior-preserving.
- [ ] No unrelated files were changed.
- [ ] Focused verification ran after edits.
- [ ] Any required review gate was rerun after post-review edits.
