# Pre-existing failure: plan-issues reround cap test asserts 3 failed rounds but helper records 4

**Issue**: `tests/test_plan_issues_workflow.py::test_reround_cap_stops_after_fourth_failed_review_and_requires_user_decision` fails with `assert 4 == 3`. The test drives four failed review rounds and then asserts `status["tasks"]["alpha"]["failed_rounds"] == 3`, but `scripts/plan_issues_workflow.py` records `4`. Commit `bed3eb0` ("fix: allow four plan-issues review rounds") raised the cap from three to four rounds without updating this assertion, so the repository test suite has been red on `main` since that commit.

**Location**:
- `tests/test_plan_issues_workflow.py:410` (the `assert entry["failed_rounds"] == 3` assertion)
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py` (the `failed_rounds` accounting that now reaches 4)

**Severity**: High

**Context**: Found while running `python3 -m pytest` as the verification step for the plan-doc/plan-code review-finding-materiality refactor. Confirmed pre-existing by checking out `HEAD` (`37b7722`) into a clean throwaway worktree and running the same suite: it failed identically there, and the materiality refactor changed only Markdown and YAML files. Historical full-suite result in both trees: `1 failed, 92 passed`.

Disposition on 2026-07-30: superseded by the approved six-ordinary-round contract. The replacement test now drives six failed ordinary dual-lane rounds, asserts `failed_rounds == 6`, verifies meta-reviews do not increment the count, and confirms round seven is blocked pending a user decision. The repository suite passed after that change.

**Suggested Fix**: No separate four-versus-three fix remains. Keep this record as historical evidence until an explicitly authorized issue-cleanup pass removes resolved records; use the current six-round tests and canonical workflow policy as the active contract.
