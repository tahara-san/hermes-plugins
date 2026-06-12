---
name: plan-code
description: "Use when you need the plan-code workflow. Execute existing task planning documents with progress updates, simplify/review gates, and verification."
version: 1.0.0
author: Hermes Agent + tahara-san
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [implementation, planning, review-gates]
    related_skills: [planning-workflows]
---

# plan-code

## Overview

This is a stable public entrypoint for the `plan-code` workflow. The canonical workflow details live in `planning-workflows` at:

```text
references/plan-code/plan-code.md
```

Load and follow `planning-workflows` when you need the complete umbrella context.

## When to Use

Execute existing task planning documents with progress updates, simplify/review gates, and verification.

## Required Behavior

1. Treat `plan-code` as a workflow contract, not a suggestion.
2. Load or consult `planning-workflows` and its `plan-code/plan-code.md` reference when details matter.
3. Fail closed if a required artifact, blocker gate, review, or verification step cannot be completed.
4. Report exact files changed, verification commands/results, review artifacts, and deviations.

## Invocation

Preferred form:

```text
/skill plan-code <request>
```

If your Hermes surface supports direct skill commands, `/`-style invocation may also be available.

## Common Pitfalls

- Treating this wrapper as a separate source of truth from `planning-workflows`.
- Skipping required gates because the request looked small.
- Reporting success without durable artifacts or real verification output.
