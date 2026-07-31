# Phase review loop discipline

Use this when `/plan-code` requires simplify, independent review, and Claude Code review after each phase/batch.

Read it together with `../../review-finding-disposition-and-convergence.md`, which is the canonical authority on which findings block. This file covers how the phase loop consumes those verdicts.

## Lesson

Treat the phase review gate as the union of all mandatory reviewers' **blocking** findings, not as a majority vote and not as the union of every observation. If simplify says approved and Claude says approved, but the independent reviewer reports a finding that satisfies the blocker predicate, the phase is not ready for sign-off unless:

1. Fix the finding.
2. Rerun the affected verification.
3. Rerun the affected mandatory review gate.
4. Only then update task TODO/progress files to complete.

Do not mark a phase complete while a mandatory reviewer has an unresolved **confirmed blocker**, even if another reviewer labels it non-gating. A required lane's `CHANGES_REQUIRED` can never be overridden by the aggregate artifact.

## The symmetric rule

A finding that does **not** satisfy the blocker predicate does **not** keep the phase open. Record its materiality and disposition in the round ledger and move on. Style, naming, optional readability, extra hardening beyond adequate acceptance/invariant coverage, speculation without an evidenced failure path, unsupported-environment portability, unrequested refactors, evidence polish, unrelated pre-existing defects, and rephrased repeats are parked or accepted — not implemented.

Applying an optional suggestion is not free: it mutates judged bytes, stales the exact-byte approval, and sends both xhigh lanes back over the whole bundle. That is how a phase gate turns into a multi-day loop with no source defect in sight.

## Concrete trigger patterns

**Blocking (phase stays open):**

- Phase implementation and targeted tests pass.
- Simplify returns `APPROVED`.
- Claude Code returns `APPROVED` with minor notes.
- The independent reviewer finds a real semantic edge case with a concrete failure mode against an explicit acceptance criterion.
- Correct behavior: stop phase advancement, patch the edge case, rerun targeted checks, then rerun simplify + independent review + Claude Code for the phase.

**Non-blocking (phase closes):**

- Both mandatory lanes return `PASS`.
- One lane adds two documentation-accuracy notes and a suggestion to add another assertion to an already adequately covered path.
- Correct behavior: record both notes as `ADVISORY` with dispositions (`accept-no-action` or `park-follow-up`) in the round ledger, change no judged bytes, and close the phase. Do not regenerate the bundle. Do not rerun either lane.

**Mixed substantive verdict:**

- When exactly one ordinary lane passes, keep judged bytes fixed and launch both independent same-digest cross-assessments before waiting: the **passing lane** reviews the **failing lane** verdict, and the **failing lane** reviews the **passing lane** verdict, each using only `UPHOLD` (agree) or `OBJECT` (dispute).
- Either assessment may finish first. Only passing-lane `OBJECT` plus failing-lane `UPHOLD` shows agreement in the passing direction and approves the same bundle. Any other complete pair preserves the failure for remediation and the **next dual-lane round**.
- Preserve compact meta-review opinions/findings as next-round context when unresolved. Meta-reviews do not count toward the **six dual-lane review rounds**. If round six does not approve the gate, stop before round seven and **ask the user to decide** how to proceed. No aggregate or orchestrator override is allowed.

**Process failure (never parked):**

- Wrong model/effort, bad digest, preamble before the verdict block, unparseable verdict, missing coverage, missing raw pane, unavailable CLI, or review outside the authorized scope.
- Correct behavior: mark the lane `BLOCKED_PROCESS`, fail closed, and run one bounded same-byte process retry. A second failure stops for explicit user resume/override.

## Checkpoint tiering

Not every phase needs its own dual-lane gate. Require a per-phase/batch review when the phase touches security/auth/privacy, schema/data/financial integrity, transactions/retries/idempotency/concurrency/ownership/lifecycle, public contracts, irreversible or provider-side effects, foundational shared primitives, or an explicit plan/user phase gate. Group low-risk phases with adequate focused verification into one milestone review and record the rationale. The holistic final review stays mandatory either way.

## Good status language under tool limits

If a tool-call/resource limit stops the session before the blocker loop is closed, report:

- phase is still `in_progress`, not complete;
- implementation/verification commands that actually passed;
- exact unresolved **blocking** reviewer finding and its stable finding ID;
- parked findings and their dispositions, so the next session does not re-litigate them;
- the ordinary dual-lane round count, meta-review event count, process-retry count, and whether the round-six user-decision checkpoint was reached;
- exact next steps to resume.

Never imply completion just because most gates passed. Equally, never imply a phase is incomplete because an advisory list is non-empty.
