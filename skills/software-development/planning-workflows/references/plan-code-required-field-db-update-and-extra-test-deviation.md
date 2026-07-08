# Plan-code: required-field data reset and extra-test deviation

Use this when a `plan-code` task adds a new required canonical field (especially in Buffdemy backend/frontend cross-repo schema work) and the plan allows pre-service/no-compat data reset.

## Pattern

1. **TDD first**: add schema/model/response tests that fail because the new required field is missing, then implement the smallest schema/create/response/model changes.
2. **Local/dev DB check is part of execution** when existing persisted rows could violate the new required schema:
   - Query the target dev DB through the app/container environment that already has the correct config.
   - Prefer a one-off inline command over a committed migration script when the plan allows disposable reset/update.
   - Record before/after counts, e.g. `total`, `missing`, `matched`, `modified`, `missing_after`.
   - Confirm no migration script/file remains in `git status`.
3. **Fixture sweep**: search for typed API/model fixtures that construct the changed shape outside the originally documented focused tests. Update obvious canonical fixtures even if they are only typechecked.
4. **Extra test deviation handling**:
   - If an additional non-required test for a touched fixture is blocked by a pre-existing environment/request-scope issue, do not broaden the task into fixing that test harness unless the plan requires it.
   - Re-run the documented focused verification plus typecheck/lint after the fixture change.
   - Document the extra test command, exact blocker, and why the canonical fixture is still covered (for example by `tsc` and lint) as a deviation in the TODO/review bundle.
5. **Review bundle**: include the DB update evidence, fixture sweep, documented required verification results, and the extra-test deviation. Ask reviewers to judge whether the deviation is truthful and non-introduced.

## Pitfalls

- Do not leave a disposable migration script behind just to prove the update happened; the command output is the artifact.
- Do not treat an environment-blocked extra test as satisfying the required verification matrix. It is separate evidence/deviation.
- Do not implement write endpoints/UI just because a new field exists when the plan made write support conditional on explicit user confirmation.
- If task docs are edited after implementation review to record final artifacts, run a final artifact-consistency review excluding the consistency artifact itself or using a placeholder pattern.
