---
name: plan-issues
description: "Use when you need the plan-issues workflow. Convert out-of-scope issue logs into implementation task plans without fixing them inline."
version: 1.0.0
author: Hermes Agent + tahara-san
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, issues, out-of-scope, triage]
    related_skills: [planning-workflows]
---

# plan-issues

## Overview

This is a stable public entrypoint for the `plan-issues` workflow. The canonical workflow details live in `planning-workflows` at:

```text
references/plan-issues/plan-issues.md
```

Load and follow `planning-workflows` when you need the complete umbrella context.

## When to Use

Convert out-of-scope issue logs into implementation task plans without fixing them inline.

## Required Behavior

1. Treat `plan-issues` as a workflow contract, not a suggestion.
2. Load or consult `planning-workflows` and its `plan-issues/plan-issues.md` reference when details matter.
3. Fail closed if a required artifact, blocker gate, review, or verification step cannot be completed.
4. Report exact files changed, verification commands/results, review artifacts, and deviations.

## Invocation

Preferred form:

```text
/skill plan-issues <request>
```

If your Hermes surface supports direct skill commands, `/`-style invocation may also be available.

## Common Pitfalls

- Treating this wrapper as a separate source of truth from `planning-workflows`.
- Skipping required gates because the request looked small.
- Reporting success without durable artifacts or real verification output.
