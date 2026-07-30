**Issue**

The plan-issues helper accepts only `claude-opus-4-8` attestations, while the active planning-review policy requires interactive Claude Code Fable 5 at xhigh effort with an explicit fresh-session Opus fallback. A correctly documented Fable review is therefore rejected fail-closed.

**Location**

- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:54-58`
- Active Fable/Opus policy surfaces under `skills/software-development/planning-workflows/` and `skills/autonomous-ai-agents/claude-i/`

**Severity**

high

**Context**

The mismatch predates the two-lane `UPHOLD` / `OBJECT` reconciliation change and was independently identified during the mandatory Fable 5/xhigh review. The helper's `_REVIEW_ATTESTATIONS["claude"]` requires `claude-opus-4-8`, but the repository's current reviewer instructions launch `claude --model fable --effort xhigh` and permit Opus only as an explicitly recorded fallback. Changing accepted model identities is a separate reviewer-contract decision, so it was not folded into the reconciliation/round-limit change.

**Suggested Fix**

Define one canonical Claude attestation contract shared by helper, CLI documentation, and tests. Either accept the exact documented Fable identity plus an explicitly represented Opus-fallback identity, or revise the published model policy intentionally. Add positive and negative tests for both primary and fallback attestations, then rerun the complete two-lane policy suite.
