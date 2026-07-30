# Plan-Code Delta Review Rerounds

Use this reference when an explicit `plan-code` workflow has already completed a clean full review round, then fixes review findings, build failures, verification failures, or small final-doc/artifact issues. The goal is to reduce repeat review work without weakening the gate.

## Core Contract

- **Round 1 of each gate is full coverage.** Per-phase and holistic implementation review gates begin by reviewing the whole gate scope with every required lane.
- **Clean baselines are explicit.** A verdict can be carried forward only for content that has a saved clean baseline: round id, reviewer artifact path(s), reviewed file/chunk list, and the current state hash (`git diff` hash, blob hash, or equivalent bundle hash).
- **Delta rerounds are allowed only after a clean baseline exists.** A failed full round creates no carry-forward baseline for failed content. Non-flagged files/chunks gain carry-forward baselines only when the reviewer verdict or aggregate artifact explicitly records them as clean at a hash/state. The next reround is full for any file/chunk without a clean baseline.
- **Under-scoped deltas fail closed.** If the semantic impact boundary is uncertain, rerun the full gate instead of guessing.
- **Only judged-product changes create a reround.** Code, tests, fixtures, migrations, task docs, executable commands/contracts, intended commit artifacts, and contract-bearing final reports stale approvals. Review-evidence writes — raw panes, normalized verdicts, disposition ledgers, gate JSON, cleanup evidence, supersession records, parked-advisory issue files — do not, and are validated deterministically instead. See `review-finding-disposition-and-convergence.md`.
- **Only confirmed blockers justify the fix that creates the reround.** An advisory finding is dispositioned, not implemented; an advisory-only round is terminal.

## Scope Freeze After Round 1

Round 1 of each gate is broad. Every later round narrows to:

1. closure of prior blocker IDs;
2. changed bytes;
3. semantically affected neighbors;
4. newly discovered critical/high material defects.

A later reviewer may still raise a real material defect outside the delta, but it must satisfy the blocker predicate. New polish and speculative hardening surfaced in later rounds are parked, not folded into the reround.

## Ordinary dual-lane round budget

Count every complete ordinary dual-lane review pair, whether full or delta. Limit each gate to **six dual-lane review rounds**. Same-digest meta-reviews and process retries that produce no substantive pair are separate event types and do not consume the ordinary-round budget.

After an unresolved ordinary round:

- stop applying optional improvements and disable broad unrelated simplify edits;
- deduplicate findings by stable ID so a reworded repeat cannot restart the loop;
- review only blocker fixes and semantically affected scope under this delta protocol;
- carry compact unresolved meta-review opinions/findings into the next ordinary round;
- keep any new material defect blocking;
- if round six does not approve the gate, stop before round seven and ask the user to decide instead of continuing autonomously.

The limit is not auto-approval. A late critical security, data-integrity, or correctness finding remains blocking regardless of the round count.

## Delta Scope

A delta reround reviews exactly these pieces:

1. Files changed since their last clean baseline.
2. Unchanged files semantically affected by the fix: callers/consumers of changed exports, query/index users, config-driven behavior, generated artifacts, schemas, fixtures, docs that define the contract, and any cross-repo companion surface named by the task.
3. Files or chunks with no clean baseline.
4. One small **delta-interactions** chunk explaining what changed, why it changed, what prior finding it addresses, and which unchanged baselines are being carried forward.

Before launching the reround, write the delta scope list into task notes, progress, or the review artifact: changed files, affected unchanged files, no-baseline files, carried-forward baseline ids, and the reason a full rerun is not required.

## Coupled-Artifact Batching

Before any reround, batch obvious coupled artifacts into the fix or record a one-line rationale for excluding them:

- index definitions for query/sort changes;
- config and feature flags for behavior changes;
- callers/consumers of changed signatures or payloads;
- fixtures, generated schemas, and snapshots;
- task docs, TODOs, review bundles, and final-report text that describe the behavior;
- companion repo surfaces when the task explicitly spans repos.

This prevents review loops where each reround discovers the next mechanically coupled artifact.

## Tiered Rerun Rules

Classify behavior first, then choose ceremony:

1. **Behavior-affecting or uncertain fix** → rerun impacted verification, run simplify on changed/affected code, then run every mandatory review lane on the delta scope.
2. **Confirmed non-behavioral doc-only fix** → no code verification is required unless the docs encode executable commands/contracts; run a focused simplify/doc-consistency pass, then a single focused reviewer check is acceptable if the workflow’s other lane already has a clean baseline and the artifact records this tier rationale.
3. **Confirmed non-behavioral ≤5-line mechanical code fix** → run a narrow simplify pass on the edited file(s), rerun impacted static/type/build checks when relevant, then every mandatory review lane on the delta scope.
4. **New files or new scope** → treat the new content as round 1: full review of the new content plus semantically affected neighbors; previously clean unaffected files may carry their baselines forward.
5. **CRITICAL/security/data-integrity finding** → full rerun after the fix unless the task owner explicitly waives with a written rationale.

## Plan-Doc vs Plan-Code

- `plan-doc` review reruns are normally full dual-lane reviews because task docs are small and final text is the product.
- `plan-code` implementation reruns should use this delta protocol once a clean baseline exists. Do not re-review byte-identical, unaffected files just because a small fix landed elsewhere.

## Required Artifact Fields

A delta review artifact should include:

- `coverage: "delta"` or equivalent wording;
- prior clean baseline id(s) and artifact path(s);
- changed files;
- semantically affected unchanged files;
- no-baseline files/chunks;
- carried-forward files/chunks;
- verification commands rerun for the delta;
- reviewer verdicts for the delta scope;
- round coverage type: `full`, `delta`, `meta-review`, or `process-retry`;
- running ordinary dual-lane review-round count, reconciliation state, and meta-review event count;
- novel finding IDs vs duplicates, and the disposition ledger path;
- explicit statement that unchanged carried-forward files were not fully re-reviewed in this round.

## Pitfalls

- Calling a reround "delta" without baseline hashes or artifact paths.
- Carrying forward a verdict for a file whose content changed after the clean round.
- Reviewing only the edited file when a signature/schema/index/config change affects neighbors.
- Letting optional suggestion churn invalidate approvals repeatedly; record low-value suggestions instead of implementing them unless they satisfy the blocker predicate.
- Starting a reround at all when the round's only findings were advisory. An advisory-only round is terminal.
- Rerounding because a disposition ledger, raw pane, or gate JSON was written. Those are review-evidence, not judged product.
- Assigning a new finding ID to a reworded repeat, which inflates the novel-finding count and prevents convergence.
- Counting a same-digest meta-review or schema-recovery retry as an ordinary dual-lane review round.
- Using a delta reround after a CRITICAL finding without an explicit full-rerun decision.
