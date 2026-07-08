# Post-feedback correction commit readiness

Use this pattern when a plan-code task was previously marked complete/reviewed, then user/manual verification exposes a real integration bug and the task is corrected before `plan-commit`.

## Pattern

1. Treat all prior implementation/final review artifacts as stale for completion once source, tests, or task docs change after approval.
2. Add a RED regression for the user-reported boundary before changing production code, then make the smallest fail-closed correction.
3. Rerun proportional verification for the corrected boundary.
4. Update task docs so the corrected live contract is explicit. In particular, reconcile both checked rows **and their nested child bullets**; stale child bullets like “review pending” under a checked parent still fail commit-readiness.
5. Save new correction review artifacts. If a non-blocking review suggestion is adopted afterward, regenerate the bundle and run a narrow final consistency review instead of relying on the older approval.
6. Before staging, run a pre-commit artifact-consistency bundle over live `todo.md`, `final-report.md`, notes/spec, and final review JSONs. Exclude the future pre-commit verdict artifact from its own bundle to avoid self-reference.
7. Stage only intended implementation files plus the task directory; leave unrelated dirty files unstaged.
8. Run `git diff --cached --check`. Generated review bundles often contain trailing whitespace from embedded diffs/panes; normalize only intended generated task Markdown artifacts, restage, and rerun the check.
9. If normalization happens after the pre-commit consistency verdict, run one final post-normalization consistency review over the exact staged state before committing.

## Useful scans

```bash
grep -n '^- \[ \]\|^- \[~\]' tasks/<slug>/todo.md || true
grep -n 'pending as `deleg_\|review is pending\|blocked until' tasks/<slug>/todo.md tasks/<slug>/final-report.md || true
git diff --cached --check
```

## Do not overlearn

Do not record the original backend/API failure as a general tool or environment limitation. The durable lesson is the workflow: user/manual gate failures after review stale the review, and pre-commit artifact consistency must inspect nested notes and generated-bundle whitespace before committing.
