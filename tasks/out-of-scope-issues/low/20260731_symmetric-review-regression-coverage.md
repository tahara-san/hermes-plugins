# Symmetric review regression guards do not cover every surface and arrival order

**Issue**

The symmetric meta-review truth table is covered for all four verdict pairs only when the passing-lane assessment is recorded first. Reverse arrival is covered for the approving pair but not for all three non-approving pairs, and exact/conflicting duplicate behavior is exercised only for the passing-lane stage. The retired-language policy guard also covers only `TWO_LANE_RECONCILIATION_FILES`, omitting three updated policy references, and therefore permits advisory sequential-era wording such as “meta-review chain” outside its exact banned phrases.

**Location**

- `tests/test_plan_issues_workflow.py:324`
- `tests/test_review_lane_policy.py:43`
- `skills/software-development/planning-workflows/references/review-finding-disposition-and-convergence.md:7`
- `skills/software-development/planning-workflows/references/plan-code-opus-review-limit-and-rerun.md`
- `skills/software-development/planning-workflows/references/plan-issues-priority-grouped-conversion.md`
- `skills/software-development/planning-workflows/references/writing-plans/references/out-of-scope-issue-planning.md`

**Severity**

low

**Context**

Both mandatory review rounds found the implementation and current policy snapshots internally symmetric; the final gate approved the unchanged round-2 bundle. These are regression-coverage and terminology-hardening gaps, not evidence of an incorrect state transition. The phrase “meta-review chain” is followed by normative symmetric instructions and does not itself enforce sequential execution, but it can suggest the retired protocol and is not caught by the current policy test surface.

**Suggested Fix**

Parameterize the complete 2×2 verdict matrix across both assessment arrival orders and assert identical state and failed-round accounting. Exercise idempotent and conflicting duplicate submissions for both lane stages. Expand the reconciliation-policy file set to every policy surface that carries the symmetric contract. Replace “meta-review chain” with “cross-assessment pair” or similarly order-neutral wording, and add narrowly targeted retired-language assertions without banning unrelated uses of “chain.”
