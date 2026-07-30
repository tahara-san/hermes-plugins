# Plan-issues accepts empty meta-review finding strings

**Issue**

Meta-review records require a nonempty opinion but can persist empty or whitespace-only entries in the optional `findings` list.

**Location**

- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:1863`
- Meta-review record validation in `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py`

**Severity**

low

**Context**

The finding list is converted with `str(finding)` without trimming or rejecting empty values. This does not alter verdict transitions, round accounting, or approval finality, and findings are optional, so the mandatory review classified it as input-hardening rather than a blocker. Empty entries can nevertheless reduce evidence quality and complicate consumers that expect every stored finding to contain text.

**Suggested Fix**

Normalize finding entries with trimming and either reject empty values or omit them according to one documented contract. Revalidate persisted meta-review records with the same rule and add focused tests for empty strings, whitespace-only strings, non-string inputs, and a genuinely empty optional list.
