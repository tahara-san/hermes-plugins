**Issue**

A delayed old-bundle ordinary verdict arriving while the current task is in a meta-review reconciliation state is rejected before it can be archived as superseded evidence.

**Location**

`skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:1517-1530`

**Severity**

low

**Context**

`record_review()` checks `entry["state"] != "reviewing"` before checking whether `bundle_digest` differs from the current bundle. Existing coverage proves delayed old-digest verdicts are archived while the new bundle is in `reviewing`, but the same late result during `meta_review_pending` or `meta_reconsideration_pending` raises instead. This remains fail-closed and cannot approve stale bytes, so it does not block the active reconciliation/round-limit work, but it loses the documented one-time superseded archival path for an asynchronous completion.

**Suggested Fix**

Validate the raw attestation and current bundle first, then route any non-current digest to the idempotent superseded archive before enforcing the current-state gate for current-digest records. Add regressions for delayed verdicts arriving during both meta-review pending states and verify they cannot alter current reviews, reconciliation, failed-round counts, or final approval.
