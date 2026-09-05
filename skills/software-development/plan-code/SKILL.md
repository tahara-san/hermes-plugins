---
name: plan-code
description: "Use when you need the plan-code workflow. Execute existing task planning documents with progress updates, simplify/review gates, and verification."
version: 1.1.0
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
3. Require the external **Codex interactive TUI review lane** to start bare `codex` in a managed `tmux` session with **GPT-6 Astra @ xhigh effort**, exactly as defined by `planning-workflows/references/codex-cli-review-lane.md`. Never use noninteractive `codex exec` or `codex review`: those paths cause severe timeout issues. Record the CLI version, tmux session, model/effort banner attestation, bundle identity, raw pane capture, and parseable verdict. Never use a Hermes `delegate_task` reviewer as this lane or its fallback. Fail closed on an unavailable, unauthenticated, mismatched, or unparseable required lane unless the user explicitly waives it. Claude Code remains a separate interactive CLI lane through `claude-i`.
4. Launch every required independent review lane before waiting for, polling, monitoring, adjudicating, or fixing findings from any one lane. Do not run Codex to completion and only then launch Claude Code, or vice versa.
5. Apply `planning-workflows/references/review-finding-disposition-and-convergence.md` to every phase, batch, and holistic review gate. Remediate only findings that satisfy the blocker predicate; record exactly one disposition for every other reviewer item in the review-evidence ledger. Advisory-only output completes the gate without judged-product mutation or rerun. When exactly one ordinary lane passes, launch both independent same-digest cross-assessments before waiting: the passing lane reviews the failing lane's verdict, and the failing lane reviews the passing lane's verdict, each using only `UPHOLD` or `OBJECT`. Approve only for passing-lane `OBJECT` plus failing-lane `UPHOLD`; every other complete pair preserves the failure for the next ordinary round. Process failures stay fail-closed. Limit each gate to six ordinary dual-lane rounds; meta-reviews do not count, and round six escalates to the user instead of starting round seven. Require per-phase dual-lane gates for high-risk boundaries and allow low-risk phases to share one milestone review, with the holistic final review always mandatory.
6. Enforce mandatory out-of-scope issue tracking: do not silently ignore or fix out-of-scope findings inline; deduplicate first, then log each non-exempt finding under `tasks/out-of-scope-issues/<priority>/` (or `<priority>/manual/` for human intervention) with **Issue**, **Location**, **Severity**, **Context**, and **Suggested Fix** sections in that order. Do not create or update an issue file solely for Dependabot alerts/security-advisory counts. Parked reviewer findings route through this same policy.
7. Fail closed if a required artifact, blocker gate, review, or verification step cannot be completed.
8. Report exact files changed, verification commands/results, review artifacts, finding dispositions, convergence accounting, logged out-of-scope issues, and deviations.

## Invocation

Preferred form:

```text
/plan-code <request>
```

In WebUI or any surface where that command is not listed, write `Use the plan-code skill to <request>` instead. Do not use the retired generic dispatcher syntax.

## Common Pitfalls

- Treating this wrapper as a separate source of truth from `planning-workflows`.
- Skipping required gates because the request looked small.
- Reporting success without durable artifacts or real verification output.
