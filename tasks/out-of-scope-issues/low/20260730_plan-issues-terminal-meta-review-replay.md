# Plan-issues terminal meta-review replay is not idempotent

**Issue**

An exact replay of the terminal failing-lane meta-review record after that record closes the current task is rejected by current-task validation instead of returning the already finalized aggregate.

**Location**

- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:1805`
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:1888`
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:1960`

**Severity**

low

**Context**

Duplicate meta-review records are idempotent while reconciliation is active. A terminal failing-lane `OBJECT` can approve and advance the workflow, after which `_ensure_current_task()` runs before duplicate detection and rejects an exact retry. The mandatory reviewer withdrew this as a blocker because the behavior remains fail-closed, preserves the approved aggregate and evidence chain, and cannot double-count or falsely approve a round. It remains a retry ergonomics and API-consistency gap.

**Suggested Fix**

Either support validated replay of the exact stored terminal record by looking up finalized same-digest evidence before current-task rejection, or explicitly document that callers must query status/final-review evidence after closure rather than retry the write. Add a regression proving exact replay is safe and conflicting post-closure records remain rejected.
