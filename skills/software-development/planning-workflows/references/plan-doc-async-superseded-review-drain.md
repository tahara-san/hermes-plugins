# Plan-doc async superseded review drain

Use when old async `delegate_task` / Codex-style plan-doc reviews return after the live task docs have moved on to a newer bundle version.

## Pattern

1. **Classify the returned review by bundle version.** Compare the delegation id and reviewed bundle path in the async result to the current canonical bundle/pending artifact. If it is older, it is superseded evidence, not current approval.
2. **Do not count stale approvals.** A passing review for `bundle-vN` does not satisfy the review gate for `bundle-vN+1` or later.
3. **Disposition every concrete finding against the current docs.** For each blocker or non-blocking suggestion:
   - If current docs already address it, record that in the superseded artifact reason.
   - If it exposes a real current-risk footgun, patch only the task docs needed to remove the ambiguity.
   - If it is optional polish or intentionally out of scope, record why no live patch is needed.
4. **Save the old result durably.** Write `tasks/<slug>/reviews/codex-plan-doc-review-vN-superseded.json` or equivalent with:
   - reviewer/delegation id
   - reviewed bundle path
   - raw verdict JSON
   - `superseded: true`
   - disposition / superseded reason
5. **Update the current pending aggregate history.** Add the superseded artifact path to the active `plan-review-pending-vM.json` so future agents can reconstruct review history.
6. **If live docs changed, regenerate and rerun.** Any patch to `spec.md`, `todo.md`, or intended plan artifacts makes the current bundle stale. Regenerate the next `plan-doc-review-bundle-vM+1.md` and rerun both required review legs against that bundle. Also write a new `plan-review-pending-vM+1.json` that explicitly supersedes the previous pending artifact, because any not-yet-returned reviewer for the old bundle is now stale even if it later passes.
7. **If a stale final reviewer returns after the bundle advanced, still drain it as stale.** Even when the returned delegation was formerly the “final pending” review, once current docs moved to a later bundle its verdict cannot satisfy the gate. Save it as `codex-plan-doc-review-vN-superseded.json`, disposition its findings against the current docs, and keep waiting for the current bundle’s delegation.
8. **If live docs did not change, keep the active pending gate unchanged.** Run a scoped artifact check such as `git diff --check -- tasks/<slug>` and report that the current required review remains pending.

## High-churn drain checklist

When many old async reviews return after a plan-doc bundle has already advanced through several versions:

1. Keep one explicit **current canonical bundle** and one **current pending aggregate**. Older pending artifacts stay as history only.
2. For each stale result, save `codex-plan-doc-review-vN-superseded.json` and add it to the current pending artifact's `superseded_reviews`; do not copy stale approvals into the current verdict fields.
3. Disposition stale findings against the current docs in the superseded artifact reason. If the finding is already fixed, say so; if it is optional polish, say no live patch was made and why.
4. If a stale or current review exposes a concrete test/acceptance footgun that still applies, patch only `spec.md`/`todo.md`, mark the now-current review artifacts stale/superseded, regenerate `plan-doc-review-bundle-vN+1.md`, and rerun both the Codex-style and Claude/default-model legs.
5. Do not write the final aggregate `plan-review.json` until both reviewer artifacts name the same final bundle version and no post-review doc edits have occurred.

## Current delegate finalization checklist

When the active/current async delegate finally returns after one or more stale delegates have been drained:

1. Save the current delegate verdict as its own parseable artifact (for example `codex-plan-doc-review-<delegation-id>.json`) before writing the aggregate.
2. Prove it reviewed the current bundle, not a stale one: compare the active pending artifact's delegation id, the canonical bundle path/hash, and core task-doc mtimes against the delegate dispatch time when available. If the core docs or bundle changed after dispatch, classify the verdict as stale and rerun both required review legs.
3. If the current delegate passes and the companion Claude/default-model artifact for the same bundle is already saved, write the aggregate `plan-review.json` and update the pending artifact to `COMPLETED_BY_PLAN_REVIEW` (or equivalent) instead of leaving a stale `PENDING_REQUIRED_REVIEW` file.
4. Review artifacts written after reviewer verdicts normally should not stale the plan-doc bundle. Record a self-exclusion note in the aggregate: the reviewed product is the task docs plus source/context bundle, while post-verdict raw/aggregate artifacts are evidence about the review.
5. Record non-blocking suggestions without churn unless they identify a concrete current-bundle footgun. If you patch `spec.md`, `todo.md`, `kickoff-prompt.md`, `notes.md`, or regenerate the bundle after a suggestion, all prior approvals are stale and both review legs must rerun.
6. After writing the verdict and aggregate artifacts, run a scoped hygiene check such as `git diff --check -- tasks/<slug> <converted-issue-path>` plus any issue-removal/status checks, and include that real output in the final response.

## Pitfalls

- Do not overwrite the current pending artifact with an older review's passing verdict.
- Do not create the aggregate `plan-review.json` until the required Codex-style verdict for the current canonical bundle is saved and the Claude/default-model leg for that same bundle is also saved or explicitly waived.
- Avoid self-referential bundle churn: exclude review artifacts from the reviewed scope, or clearly document their exclusion.
- If multiple stale async reviews return, drain them one by one, saving each as superseded evidence and patching/rerunning only when a finding still applies to the current docs.
- If the final current-bundle review passes but names a concrete coverage gap (for example duplicate-submit prevention, whitespace-only input, selected-state assertions), treat it as a footgun, not optional polish: patch the plan and rerun the full pair instead of aggregating immediately.
- Do not leave an active pending artifact saying `pending` after the aggregate has been saved; update it to point at the aggregate and the saved current reviewer artifacts.

## Final response shape

Report:

- saved superseded artifact path(s)
- whether live docs were patched
- current canonical bundle path
- current required review status/delegation id
- real scoped verification output
