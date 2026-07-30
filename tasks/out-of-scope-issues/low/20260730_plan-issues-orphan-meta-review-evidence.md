# Plan-issues can leave orphan meta-review evidence after validation failure

**Issue**

`record_meta_review()` writes the normalized meta-review result file immediately before aggregate storage and final evidence revalidation. If that later step fails, the newly written file can remain on disk without being referenced by the authoritative status or aggregate.

**Location**

- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:1959`
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:1960`
- Aggregate storage and validation in `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py`

**Severity**

low

**Context**

The authoritative chain reads status- and aggregate-referenced records, so an orphan file cannot approve a bundle or corrupt round accounting; the failure remains fail-closed. The mandatory review therefore classified this as cleanup/transactional hardening. The leftover file can still confuse operators or later tooling that enumerates the evidence directory without following authoritative references.

**Suggested Fix**

Validate the complete candidate transition before persisting the result, or write through a temporary file and commit the result plus aggregate/status in a recoverable sequence. If full atomicity is impractical, remove the candidate file on downstream validation failure and add a regression proving failed meta-review persistence leaves no unreferenced evidence.
