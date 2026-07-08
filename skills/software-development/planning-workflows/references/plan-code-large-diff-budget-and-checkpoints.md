# Large plan-code diffs: budget checkpoints and bounded review recovery

Use this when a `plan-code` implementation has a very large diff, many generated/untracked task artifacts, and repeated post-review fix cycles.

## Durable pattern

1. **Checkpoint before every broad post-review fix round.** If final review uncovers blockers after verification already passed, write down the passing verification counts and the exact failing review findings before editing again. This prevents losing a usable handoff if the session/tool budget ends mid-fix.
2. **Split final review by contract, not by arbitrary file count.** Prefer micro-bundles such as API contract, repository/core lifecycle, feed/Redis, reaction pipeline, and task artifacts. Include only the files, tests, and verification evidence needed to judge that contract.
3. **Rerun only stale impacted review legs.** When a fix is narrowly scoped to one failed micro-bundle, rerun impacted verification plus that failed micro-bundle; do not restart already-passed independent bundles unless shared code or task artifacts changed.
4. **Do not start a broad foundational fix if the remaining budget cannot cover tests/build/review.** If a final review reveals multi-area repository/API lifecycle blockers late in the session, either make a small fully-verifiable fix or stop with a fail-closed handoff listing exact blockers and next verification steps.
5. **Keep reviewer suggestions separate from blockers.** Non-blocking suggestions can be recorded in the final artifact without churn. If you choose to implement one, it makes prior approvals stale.
6. **When forced to stop mid-fix, say “not complete.”** Report which patches are unverified, which gates remain, and the exact next commands/review bundles to run. Never mark TODOs complete or imply final review passed.

## Bundle contents checklist

Each micro-bundle should include:

- current `git status --short`;
- scoped tracked diff;
- scoped untracked files rendered with `git diff --no-index /dev/null <file>`;
- latest focused verification counts;
- static scan and `git diff --check` status;
- the precise contract the reviewer should judge;
- explicit fail-closed JSON verdict schema.

## Warning signs to stop and hand off

- Reviewers uncover a second wave of architectural/lifecycle issues after several green verification runs.
- You are patching repository and route validation at the same time but have not yet written regressions.
- Tool-call or time budget is nearly exhausted and no post-fix build/test has run.
- Task docs/final review artifacts would need another consistency review after your next edit.
