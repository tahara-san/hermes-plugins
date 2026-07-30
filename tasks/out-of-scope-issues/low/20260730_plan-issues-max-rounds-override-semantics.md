# Plan-issues max-rounds override semantics are ambiguous

**Issue**

The workflow publishes six ordinary dual-lane rounds as the default checkpoint, but initialization and legacy adoption accept explicit `max_rounds` values above six. It is not mechanically or textually clear whether such a value is an authorized operator override or an invalid bypass of the stop-before-round-seven policy.

**Location**

- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:447`
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:2236`
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:2320`
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:2327`
- Six-round policy surfaces under `skills/software-development/planning-workflows/`

**Severity**

low

**Context**

The mandatory review initially classified `max_rounds=7` as blocking, then withdrew that finding during same-digest reconciliation because the configured value can be interpreted as the operator checkpoint itself and the default remains six. The current behavior is fail-closed at the configured cap and does not affect default invocations, but callers cannot tell from the contract whether values above six require separate authorization.

**Suggested Fix**

Make one explicit policy decision and enforce it consistently. Either reject values above six in initialization, legacy adoption, and CLI parsing, or define a distinct explicit override mechanism that records operator authorization while keeping the ordinary default at six. Add positive and negative tests for the selected contract and synchronize all public workflow references.
