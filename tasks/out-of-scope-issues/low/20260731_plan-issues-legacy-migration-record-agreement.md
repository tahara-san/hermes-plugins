# Plan-issues legacy migration does not validate status/aggregate agreement

**Issue**

`_migrate_legacy_pending_reconciliation()` rejects terminal legacy evidence found in the status entry, but then replaces the loaded aggregate's reconciliation from that status entry without first validating that the two persisted records describe the same non-terminal legacy state. An interrupted legacy persist can therefore leave pending status beside an aggregate containing terminal `failing_reconsideration` evidence, and migration will replace the aggregate copy rather than reject the mismatch. Adjacent fail-closed migration branches and terminal-legacy compatibility outcomes also lack direct regression coverage or explicit documentation.

**Location**

- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:431`
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:452`
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:472`
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:474`
- `tests/test_plan_issues_workflow.py:238`

**Severity**

low

**Context**

The second mandatory review found this crash-window mismatch, while the passing reviewer classified it as non-blocking and the failing reviewer ultimately agreed that classification during same-digest meta-review. The current behavior cannot create a false approval: it leaves the task pending, requires fresh fully attested symmetric assessments, and preserves the raw legacy artifact on disk. It can still obscure a persistence mismatch and discard the aggregate-embedded copy of terminal evidence. Direct coverage is absent for this cross-file disagreement and the existing rejection branches for non-`None` legacy `failing_reconsideration`, conflicting `failing_assessment`, malformed reconciliation, and a missing current bundle. Terminal sequential approvals are intentionally made stale rather than semantically remapped, while unresolved legacy context can omit the retired failing-lane reconsideration opinion; neither compatibility consequence is stated explicitly in migration documentation.

**Suggested Fix**

Before constructing a migrated candidate, validate the original status and aggregate states and reconciliation records for compatible, matching non-terminal legacy evidence. Reject terminal evidence or disagreement in either record without writing status or aggregate files. Add failure-injection regressions that prove both artifacts remain byte-identical after rejection, directly test every fail-closed legacy branch, and document that terminal sequential approvals require fresh symmetric review rather than migration. Decide whether unresolved retired reconsideration opinions should be preserved as compact historical context or explicitly documented as intentionally omitted.
