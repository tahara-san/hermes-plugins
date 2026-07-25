# Review Finding Disposition and Convergence

Use this reference for every `plan-doc`, `plan-code`, `plan-issues`, and review-related `plan-commit` gate that produces reviewer findings. It defines when a finding is a blocker, what happens to every other finding, and how a gate reaches a bounded terminal state.

The intended endpoint is **controlled residual risk with auditable disposition**, not a literal zero-findings verdict. A stronger reviewer can always find another worthwhile improvement; without a materiality threshold, stable finding identity, and a round budget, the workflow converts every newly surfaced detail into a mandatory local objective and loses the task-level goal.

This reference does not weaken any existing guarantee. Exact-byte bundle identity, digest checks, model/effort attestation, raw pane capture, normalized verdicts, read-only scope, parallel lane launch, task-scoped cleanup, and the fail-closed rule that **any mandatory non-PASS lane blocks the gate** all remain in force.

## 1. Two independent dimensions

Never collapse these into one axis.

### 1a. Lane/process state

- `QUALIFYING` — the lane ran with the required tool, model, effort, scope, and bundle identity, and emitted a parseable verdict.
- `BLOCKED_PROCESS` — the lane could not produce a qualifying review.

Process failures include: wrong model or effort, missing or mismatched model/effort attestation, bad or absent bundle digest, malformed output, a preamble before the verdict block, an unparseable or schema-invalid verdict, missing required coverage, missing raw pane evidence, unavailable or unauthenticated CLI, and review outside the authorized read-only scope.

**Process failures are never parked findings.** They remain fail-closed. Do not reclassify a `BLOCKED_PROCESS` lane as advisory, do not aggregate around it, and do not treat a companion lane's PASS as compensation.

### 1b. Substantive finding materiality

Each substantive reviewer item gets exactly one materiality label:

- `BLOCKING`
- `ADVISORY`
- `INSIGNIFICANT`
- `UNSUPPORTED`
- `DUPLICATE`
- `OUT_OF_SCOPE`

## 2. Blocker predicate

A finding is `BLOCKING` only when **all four** are true:

1. **Grounded** — it cites evidence inside the allowed review scope, or a source-grounded fact the workflow permits the orchestrator to verify.
2. **Concrete** — it identifies a reproducible or logically specific failure mode, not a preference or a generalized possibility.
3. **Contract-relevant** — it violates at least one explicit user requirement, acceptance criterion, repository rule, supported-target contract, or required verification guarantee.
4. **Material before release/approval** — leaving it unresolved can affect at least one of:
   - correctness or executability;
   - security, privacy, authorization, or secret handling;
   - data loss, corruption, durable inconsistency, or financial integrity;
   - concurrency, retry, idempotency, transaction, lifecycle, or ownership safety;
   - public API/schema/compatibility requirements that are actually in scope;
   - required build/test/static verification;
   - target-environment production operability, or rollback/cleanup safety;
   - a missing plan decision that would force the implementer to invent material behavior.

A **low-severity** issue can still block when it violates an explicit acceptance criterion. A **high-severity label** without grounded evidence and a concrete failure mode is not sufficient — severity is the reviewer's opinion; the predicate is the gate.

## 3. Findings that are not blockers by default

Unless a finding satisfies the predicate in section 2, classify it as advisory, insignificant, unsupported, duplicate, or out of scope:

- cosmetic wording, formatting, naming, or style preferences;
- optional readability improvements with no behavioral ambiguity;
- additional test hardening beyond already adequate acceptance/invariant coverage;
- speculative concerns without an evidenced failure path;
- portability for unsupported environments;
- broad refactors or abstractions not required by the task;
- evidence/provenance polish that does not affect bundle identity, attestation, coverage, or verdict validity;
- unrelated pre-existing defects;
- repeated or rephrased versions of an already dispositioned finding.

**Wording exception:** a documentation or plan wording defect remains blocking when it can cause unsafe implementation, incorrect commands, wrong authorization behavior, data loss, or another material contract failure.

## 4. Dispositions

Every substantive reviewer item must receive exactly one recorded disposition:

| Disposition | Meaning |
|---|---|
| `remediate-now` | Confirmed blocker. Fix, rerun affected verification, rerun the affected review scope on fresh exact bytes. |
| `park-follow-up` | Real future work, not blocking this gate. Deduplicate into the repository's issue-tracking policy. |
| `accept-no-action` | No worthwhile follow-up exists. Preserve only the audit rationale and residual risk. |
| `reject-unsupported` | Evidence contradicts the claim or cannot support it. Record why. |
| `duplicate` | Same defect as an already dispositioned finding. Reference the canonical finding ID. |
| `out-of-scope` | Real but outside the active task contract. Route through the sanctioned issue path; do not expand the active task. |

### Finding record fields

Record each item in the round's disposition ledger with:

```text
finding_id
review_round
review_lane
reviewer_verdict
summary
materiality
severity
confidence
evidence
failure_mode
contract_or_invariant
relation_to_changed_bytes
disposition
disposition_rationale
residual_risk
follow_up_destination
requires_user_authorization
```

### Stable finding identity

Assign a stable `finding_id` on first appearance and reuse it across rounds and lanes. **Rewording does not create a new finding.** A rephrased repeat is `duplicate` against the canonical ID and does not increment the novel-finding count or the remediation-round count.

## 5. Parking behavior

- `park-follow-up` logs deduplicated future work through the repository's existing out-of-scope issue policy when that policy applies (for this repository: `tasks/out-of-scope-issues/<priority>/…` with the required **Issue / Location / Severity / Context / Suggested Fix** sections). Search all priority subdirectories including `manual/` before creating a new file.
- `accept-no-action` creates no backlog entry. Record the rationale and residual risk in the disposition ledger only.
- `reject-unsupported` records the evidence that contradicts or fails to support the claim.
- `duplicate` references the canonical finding ID and nothing else.
- `out-of-scope` uses the sanctioned issue path and must not expand the active task's scope, acceptance criteria, or verification set.

**Do not edit judged task/code bytes solely to write a parking disposition.** The ledger lives in the review-evidence plane (section 8).

### Authorization boundary

- User approval is **not** required to park a finding that objectively fails the blocker predicate.
- User approval **is** required to waive a confirmed blocker, or to waive a mandatory review lane.
- Review approval is never authorization to implement, commit, push, start services, mutate data, deploy, or activate behavior. Those remain separate explicit authorizations.

## 6. Reviewer verdict semantics

Keep the existing top-level verdict names so parsers and saved artifacts stay compatible:

- **`PASS`** — no blocking substantive findings. `NON_BLOCKING` and `TESTING_GAPS` may be non-empty. A PASS with advisories is a complete, qualifying pass.
- **`CHANGES_REQUIRED`** — at least one finding satisfies the blocker predicate. Every listed blocker must include grounded evidence, a concrete failure mode, the affected contract/invariant, and the required correction. `CHANGES_REQUIRED` with an empty or structurally incomplete blocker list is schema-invalid and is treated as `BLOCKED_PROCESS`, not as a content verdict.
- **`BLOCKED`** — the reviewer could not complete a qualifying review because of a process, tool, scope, or input failure. It is **not** a content-severity label.

Do not introduce a `PASS_WITH_FINDINGS` state. `PASS` plus a non-empty advisory list already expresses that outcome, and adding a state would break existing parsers and saved artifacts for no behavioral gain.

### Required prompt contract additions

Every reviewer prompt (Codex interactive TUI lane and Claude Code `claude-i` lane) must state:

- Do not turn style, formatting, naming, optional hardening, speculation, or preference into blockers.
- A testing gap blocks only when an explicit acceptance criterion or material invariant has no adequate verification path.
- Classify findings against the task's explicit supported scope, not an imagined ideal system.
- `PASS` is correct when only advisories or testing gaps remain.
- Blockers must carry evidence, failure mode, and the violated contract/invariant.

Advisories are preserved in the artifact but must not cause judged-byte mutation or a gate rerun.

## 7. Preserving mandatory PASS without endless churn

The orchestrator must **never** override a mandatory lane's `CHANGES_REQUIRED` in the aggregate artifact. When a required lane appears to have misclassified a non-blocking finding as a blocker:

1. Verify the claim against the allowed bundle/source evidence.
2. Save a disposition explaining precisely which element of the blocker predicate fails.
3. **Do not change judged bytes.**
4. Launch **one** fresh, bounded, same-byte clarification rerun of that required lane, citing the policy and the source-grounded evidence. Do not negotiate repeatedly inside the old reviewer session; the old session is stale context, not an adjudication forum.
5. Require a fresh qualifying `PASS` from that lane against the unchanged bundle.
6. Keep the companion lane's existing `PASS` current, because the reviewed bytes did not change.
7. If the lane still returns `CHANGES_REQUIRED`, **stop and escalate to the user**. Do not negotiate indefinitely and do not silently override.

A same-byte clarification rerun is not a remediation round (section 10).

## 8. Judged-product plane vs review-evidence plane

### Judged-product plane

Code, tests, fixtures, migrations, task docs, executable commands/contracts, intended snapshots and generated artifacts, and any final report whose content is part of the task contract.

Any change to these bytes stales the affected approval and requires the existing full/delta exact-byte rerun policy.

### Review-evidence plane

Launch provenance, raw panes, normalized verdicts, disposition ledgers, gate JSON, cleanup evidence, supersession records, and sanctioned follow-up issue files created solely to park reviewer advisories.

Adding or updating review-evidence files does not mutate the reviewed product and **must not** trigger another substantive dual-lane review. Validate this plane deterministically instead:

- schema validation;
- referenced file existence;
- digest/size verification;
- model/effort and bundle-identity consistency;
- secret scan;
- no pending placeholders left behind;
- task-scoped cleanup/session checks.

This replaces the self-referential "review the review artifact that records the review" loop while preserving immutable evidence.

### Guardrail

The evidence plane must not be used to smuggle a behavior, command, acceptance criterion, or contract change around exact-byte review. Such content belongs in the judged-product plane.

A parked follow-up issue is evidence-plane by default: it records future work, must reference the orchestrator's source-grounded adjudication, and must pass deterministic format, deduplication, path, and secret checks — but it does not stale the active task's product approval. If the active task's acceptance criteria, implementation instructions, or completion claim depend on that issue's content, classify it as judged product **before** the freeze instead.

## 9. Convergence controls

### 9a. Bundle-mutating remediation budget

Default to **no more than three bundle-mutating remediation rounds per gate** before entering convergence mode. The budget is not auto-approval and never waives a real blocker.

**Convergence mode:**

- stop applying optional improvements;
- disable broad unrelated simplify edits;
- deduplicate by stable finding ID;
- review only blocker fixes and semantically affected scope under the existing delta protocol;
- require any new late blocker to state its concrete material failure plus its relation to changed bytes, an explicit task/repository contract, or a material safety invariant inside the reviewed scope;
- park new low-materiality findings automatically under this policy;
- if a material blocker remains, fix it and review it;
- if the gate cannot converge after **one** bounded additional blocker round, stop with an explicit user escalation instead of running autonomously for days.

A late **critical** finding is still blocking. The budget never suppresses a real security, data-integrity, or correctness failure.

### 9b. Process retries are counted separately

Same-byte schema recovery and process retries are **not** bundle-mutating remediation rounds. Default to one fresh retry after the initial failed attempt per lane/bundle; a second failure stops for explicit resume/override rather than starting an autonomous retry loop.

### 9c. Review scope freeze after round 1

Round 1 of each gate remains broad. Later rounds focus on:

- closure of prior blocker IDs;
- changed bytes;
- semantically affected neighbors;
- newly discovered critical/high material defects.

A later reviewer may still report a real material defect outside the delta, but it must meet the blocker predicate. New polish and speculative hardening are parked.

### 9d. Risk-based phase checkpoints for `plan-code`

The holistic final review stays mandatory. A per-phase/batch dual-lane review is **required** when the phase affects a high-risk boundary:

- security, auth, or privacy;
- schema, data, or financial integrity;
- transactions, retries, idempotency, concurrency, ownership, or lifecycle;
- public contracts;
- irreversible or provider-side effects;
- foundational shared primitives;
- an explicit plan or user requirement for a phase gate.

Low-risk phases with adequate focused verification may be grouped into **one stable milestone review** instead of running a full dual-lane gate after every small phase and then again holistically. Record the grouping decision and the risk rationale in the task docs or the gate artifact.

### 9e. Simplify discipline

- Run broad simplify **before** the first review freeze.
- After review, simplify only the blocker fix and its affected scope.
- Do not apply unrelated nice-to-have simplify edits after a passing gate.
- Record optional simplify suggestions through the same disposition policy as reviewer findings.

### 9f. Bundle hygiene

- Exclude historical raw review outputs from substantive product bundles unless artifact consistency is the explicit review target.
- Do not embed repeated full prior bundles.
- Use minimal source-grounding excerpts or coherent contract shards rather than arbitrary giant bundles.
- Record bundle bytes, line count, and input count; require an explicit sharding decision for abnormally large bundles.
- Preserve a full manifest and exact hashes even when reviewers consume contract-scoped shards.

## 10. Convergence accounting

Each gate keeps a round ledger in the review-evidence plane recording, per round:

- `round_id` and `coverage`: `full` | `delta` | `same-byte-clarification` | `process-retry`;
- bundle path, digest, bytes, lines, input count;
- lane states (`QUALIFYING` / `BLOCKED_PROCESS`) and verdicts;
- novel finding IDs vs duplicates;
- dispositions applied;
- whether judged bytes changed (this is what makes a round *bundle-mutating*);
- running `bundle_mutating_remediation_count`;
- convergence-mode status.

Enter convergence mode when `bundle_mutating_remediation_count` reaches the configured budget. Stop and escalate rather than continuing autonomous optional churn.

## 11. Migration behavior

- Existing `ignored-warnings.md` files remain readable as legacy evidence. Do not rewrite them.
- New runs use the structured per-round disposition ledger (for example `tasks/<task-name>/reviews/round-<n>/dispositions.json`) instead of accumulating ignored-warnings prose.
- Existing review artifacts remain historical and must not be rewritten or relabeled.
- In-progress tasks adopt this policy on their **next fresh bundle/round**. Do not retroactively relabel old verdicts.

## 12. Worked example

**Before this policy.** Both lanes return `PASS` with no blocking findings, plus two documentation-accuracy notes. The driver treats the notes as worth-addressing, edits two task docs, stales the exact-byte approval, regenerates a ~500 KB bundle, and reruns both xhigh lanes. The next round blocks on provenance wording, the round after blocks on a truncated delta base, and the gate finally passes on round 5 — four extra rounds with no source change.

**After this policy.** Both lanes return `PASS`. The two notes fail the blocker predicate (not contract-relevant, no material failure mode). They are recorded as `ADVISORY` with disposition `accept-no-action` and `park-follow-up` in `round-1/dispositions.json`, an evidence-plane file. No judged byte changes, so no approval is staled and no lane reruns. The gate closes at round 1 with auditable residual risk.

## Pitfalls

- Treating a reviewer's `worth_addressing` / `NON_BLOCKING` list as a mandatory work queue.
- Converting a `BLOCKED_PROCESS` lane into an advisory or parking it.
- Letting an aggregate artifact declare PASS while a required lane says `CHANGES_REQUIRED`.
- Negotiating with a reviewer inside its old session instead of running one bounded same-byte clarification rerun.
- Editing judged bytes just to write down a parking rationale.
- Re-reviewing generated gate artifacts substantively when no judged byte changed.
- Counting a same-byte clarification or a schema-recovery retry against the bundle-mutating remediation budget.
- Using the budget to suppress a late critical security/data-integrity/correctness finding.
- Creating a new finding ID for a reworded repeat, which inflates the novel-finding count and prevents convergence.
