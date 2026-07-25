# Pre-existing failure: plan-issues reround cap test asserts 3 failed rounds but helper records 4

**Issue**: `tests/test_plan_issues_workflow.py::test_reround_cap_stops_after_fourth_failed_review_and_requires_user_decision` fails with `assert 4 == 3`. The test drives four failed review rounds and then asserts `status["tasks"]["alpha"]["failed_rounds"] == 3`, but `scripts/plan_issues_workflow.py` records `4`. Commit `bed3eb0` ("fix: allow four plan-issues review rounds") raised the cap from three to four rounds without updating this assertion, so the repository test suite has been red on `main` since that commit.

**Location**:
- `tests/test_plan_issues_workflow.py:410` (the `assert entry["failed_rounds"] == 3` assertion)
- `skills/software-development/planning-workflows/scripts/plan_issues_workflow.py` (the `failed_rounds` accounting that now reaches 4)

**Severity**: High

**Context**: Found while running `python3 -m pytest` as the verification step for the plan-doc/plan-code review-finding-materiality refactor. Confirmed pre-existing by checking out `HEAD` (`37b7722`) into a clean throwaway worktree and running the same suite: it fails identically there, and the materiality refactor changed only Markdown and YAML files. Full suite result in both trees: `1 failed, 92 passed`.

**Suggested Fix**: Decide which side is authoritative. If four total rounds (initial + three rerounds) is the intended contract — which is what `bed3eb0` and the current canonical `plan-issues` docs say — update the assertion to `== 4` and rename the test to match the four-round cap. If the ledger should only count *reround* failures rather than all failed rounds, fix the counter in `plan_issues_workflow.py` instead and leave the assertion at `3`. Either way, re-run `python3 -m pytest` so `main` is green again.
