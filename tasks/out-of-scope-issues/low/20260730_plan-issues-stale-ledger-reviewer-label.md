# Plan-issues ledger retains a stale reviewer label

**Issue**

The rendered status ledger labels the Codex result column `Hermes/Codex verdict`, even though the workflow now requires distinct Codex and Claude reviewer lanes and does not use Hermes as a substitute reviewer.

**Location**

`skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:388`

**Severity**

low

**Context**

This is a presentation-only label; the underlying state, lane evidence, and aggregation remain correct. The mandatory review classified it as non-blocking because it cannot affect review execution or finality, but the stale wording may imply that a Hermes verdict can satisfy the external Codex lane.

**Suggested Fix**

Rename the column to `Codex verdict` or another unambiguous lane name, then update any exact ledger snapshots or documentation that relies on the header. Keep the Claude column separate and preserve the prohibition on Hermes reviewer substitution.
