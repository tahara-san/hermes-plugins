# Plan-code late async delegate recovery

Use when a mandatory `plan-code` delegate review was marked pending/superseded or replaced, then the original async completion payload arrives later with a parseable verdict.

## Pattern

1. **Treat the late completion as evidence, not noise.** Match the delegation id, bundle path, and reviewed scope against the active/past pending artifacts.
2. **Verify bundle authority before changing status.** Confirm the returned verdict reviewed the current immutable bundle or that the reviewed source snapshots still match live source/test files. For untracked source files, compare bundle snapshots byte-for-byte to live files; `git diff` alone is insufficient.
3. **If the late verdict is parseable and passing for the current bundle, it can satisfy the original gate.** Save it as the authoritative recovered verdict, including:
   - `delegation_id`
   - `bundle_path`
   - parsed JSON verdict fields
   - how it was received (`WebUI async delegation completion payload`, log recovery, etc.)
   - source snapshot validation result when the scoped files are untracked or bundle freshness is uncertain.
4. **Supersede replacements cleanly.** If a replacement delegate was dispatched only because the original appeared unrecoverable, mark the replacement pending artifact as `SUPERSEDED_*` and say that any later replacement result is evidence only. Do not leave two active pending blockers for the same gate.
5. **Aggregate only after artifacts are durable.** Update the final/aggregate review artifact to cite the recovered original verdict and any companion reviewer artifacts. Preserve older approvals/replacements as superseded evidence, not active gates.
6. **Run final artifact consistency after doc/artifact edits.** If TODO/progress/summary artifacts are changed to mark the gate complete, use the placeholder/self-exclusion pattern and overwrite it with a passing consistency verdict. Do not edit task artifacts afterward unless rerunning consistency.
7. **Keep unrelated gates open.** A recovered implementation review does not unblock environment/manual gates such as frontend E2E auth alignment or real Stripe/browser checks. Document those separately and avoid overclaiming.

## Artifact status examples

- Recovered original verdict: `APPROVED_RECOVERED_ASYNC_PAYLOAD`
- Replacement pending superseded by recovered original: `SUPERSEDED_PENDING_BY_RECOVERED_<ID>`
- Earlier oversized/older-bundle approval: `SUPERSEDED_APPROVED`
- Lost internal completion before late payload arrived: keep as historical only or replace its status with the recovered verdict artifact path.

## Pitfalls

- Do not ignore a late parseable PASS merely because a replacement was dispatched; first check whether it covers the same current bundle.
- Do not count the late PASS if docs/source/tests changed after the reviewed bundle without a valid snapshot/freshness proof.
- Do not let a delayed `Local:` server notification or other background process output become E2E evidence; live-probe process/socket state separately before changing E2E status.
- Do not leave pending placeholders (`passed: null`) in final artifacts after the gate is resolved; mark them superseded or overwrite with a final verdict.
