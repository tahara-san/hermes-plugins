# Plan-Code Delta Review Rerounds

Use this reference when an explicit `plan-code` workflow has already completed a clean full review round, then fixes review findings, build failures, verification failures, or small final-doc/artifact issues. The goal is to reduce repeat review work without weakening the gate.

## Core Contract

- **Round 1 of each gate is full coverage.** Per-phase and holistic implementation review gates begin by reviewing the whole gate scope with every required lane.
- **Clean baselines are explicit.** A verdict can be carried forward only for content that has a saved clean baseline: round id, reviewer artifact path(s), reviewed file/chunk list, and the current state hash (`git diff` hash, blob hash, or equivalent bundle hash).
- **Delta rerounds are allowed only after a clean baseline exists.** A failed full round creates no carry-forward baseline for failed content. Non-flagged files/chunks gain carry-forward baselines only when the reviewer verdict or aggregate artifact explicitly records them as clean at a hash/state. The next reround is full for any file/chunk without a clean baseline.
- **Under-scoped deltas fail closed.** If the semantic impact boundary is uncertain, rerun the full gate instead of guessing.

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
- explicit statement that unchanged carried-forward files were not fully re-reviewed in this round.

## Pitfalls

- Calling a reround "delta" without baseline hashes or artifact paths.
- Carrying forward a verdict for a file whose content changed after the clean round.
- Reviewing only the edited file when a signature/schema/index/config change affects neighbors.
- Letting optional suggestion churn invalidate approvals repeatedly; record low-value suggestions instead of implementing them unless they materially reduce correctness or security risk.
- Using a delta reround after a CRITICAL finding without an explicit full-rerun decision.
