# Plan-issues helper uses legacy typing collection imports

**Issue**

Ruff reports `UP035`: `Iterable`, `Mapping`, and `Sequence` are imported from `typing` instead of `collections.abc`.

**Location**

`skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:20`

**Severity**

Low

**Context**

The imports predate the two-lane meta-review changes. They are valid on the repository's supported Python versions and do not affect runtime behavior or current tests, but they conflict with Ruff's modernization rule.

**Suggested Fix**

Move `Iterable`, `Mapping`, and `Sequence` to `collections.abc` in a dedicated hygiene change, then run the full repository suite. If Ruff is intended to be authoritative, add a checked-in Ruff configuration or CI command so the convention is explicit.
