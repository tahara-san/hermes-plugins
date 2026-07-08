# Plan-code review-driven data-integrity loops

Use this reference when a large backend `plan-code` task keeps passing typechecks/tests but independent review finds live-path data-integrity defects in asynchronous propagation, reconciliation, indexes, or transactional side effects.

## Pattern

1. **Treat reviewer blockers as live contract tests, not comments.** If a reviewer identifies a concrete propagation/reconciliation/index mismatch, fix the smallest live path and rerun the relevant build/test slice before rerunning review.
2. **Search for the exact stale pattern after each fix.** Examples: stale stat deltas such as `buffCount: 1` in update handlers, accidental root aggregate writes such as `answerLikeWeight` from Buff events, missing root IDs in delete payloads, or old unique index names.
3. **Align event semantics with reconciliation semantics.** If reconciliation counts active reaction documents, update events must not increment count fields for repeated top-ups; they should adjust weight only. If counts are intended to mean purchase events, reconciliation must aggregate the ledger instead. Do not let live outbox deltas and cron reconciliation encode different meanings.
4. **Propagate root aggregate context on delete/update, not only create.** For child-target reactions/list items, include enough root context in outbox payloads (or fetch it inside the transaction) so delete/update handlers can reverse derived parent stats immediately. Reconciliation is safety net, not the only correctness path.
5. **Guard invalid deltas at both route and repository levels.** Route validation is not enough when repositories are reused internally; repository mutation methods should fail closed on no-existing-row negative/zero free reaction deltas so bad rows cannot be created by alternate callers.
6. **Index changes need stale-conflict removal.** When replacing a unique index with a broader key (for example adding `type`), add an idempotent stale-index drop before creating the new index and make verification aware of the new required index.
7. **Regenerate the review bundle after every source/test/doc change.** The passing review must be against the exact final diff. If reviewers fail multiple times, save prior artifacts as superseded or overwrite a canonical final-review artifact only after the final pass.

## Useful final recheck prompts

Ask the final reviewer to focus narrowly on previously failed blockers, e.g.:

- free Like zero/negative creation abuse
- repeated paid Buff update count/weight semantics
- child-target Buffs accidentally updating root Like aggregates
- child-target Like DELETE root stat propagation
- stale unique indexes blocking new coexistence rules
- static-scan findings

## Stop conditions

If fixes start broadening beyond the documented task scope, stop and report a fail-closed handoff with passing verification so far, remaining reviewer blockers, and the exact files/patterns still implicated. Do not claim completion until a final focused review passes after the last code change.
