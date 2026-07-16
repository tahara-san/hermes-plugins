# Superseded async review adjudication

Use this during `plan-code` or mandatory-review workflows when a background review result arrives after source, task docs, or the review bundle has already changed.

## Core rule

A superseded review is not approval for the current tree, but a superseded **failure** may still contain valid current-tree findings. Do not dismiss it solely because its bundle is stale.

## Procedure

1. **Identify authority**
   - Compare delegation id, dispatch time, and bundle path with the current pending/final bundle.
   - Label the result as `SUPERSEDED_APPROVED_REVIEW`, `SUPERSEDED_FAILED_REVIEW`, or `CURRENT_CANONICAL_REVIEW`.
2. **Save the result**
   - Persist raw/structured reviewer output under `tasks/<task>/reviews/`.
   - Include the reviewed bundle path and why it is superseded.
3. **Adjudicate concrete findings against the live tree**
   - Stale-only: line/path gone, claim fixed, or no longer applies.
   - Valid current risk: invariant, race, missing verification, stale contract, or test gap still exists.
4. **If a finding is valid**
   - Fix the smallest source/test/doc scope.
   - Add or update a regression that would have caught it.
   - Rerun impacted verification with real output.
   - Regenerate the review bundle from the new tree.
   - Mark every review dispatched before the fix as superseded.
   - Rerun all mandatory review lanes against the refreshed bundle.
5. **If findings are stale/invalid**
   - Save an adjudication artifact explaining why.
   - Include that artifact in the next bundle if it prevents reviewer confusion.

## Testing-only findings from stale reviews

A superseded review can still expose a **coverage gap** even when the source bug it named has already been fixed. Treat missing-regression findings as potentially blocking when the task TODO/spec explicitly required that coverage.

Pattern:
- Adjudicate each stale finding independently: `already fixed`, `still valid source defect`, `still valid coverage gap`, or `stale/invalid`.
- If a valid coverage gap remains, add the smallest regression at the boundary named by the task docs, not merely at an adjacent lower layer. Example: if a Buffdemy backend phase says API outbox coverage is required, repository/cron/outboxProcessor tests are not enough; add an API-level outbox test that exercises the live route and asserts the emitted outbox payload.
- Even test-only fixes stale every pending/passed review from the old bundle because tests/task docs are commit-intended artifacts. Save supersession artifacts, rerun focused verification, regenerate the bundle, and rerun mandatory review lanes.
- Prefer live endpoint regressions for API/outbox requirements: use the route that triggers the terminal transition (`POST /question-answer` for all-answered close, `POST /question/:question/cancel` for inquirer cancel) instead of calling repository helpers from an API test.

## Bundle hygiene after adjudication

- Exclude raw old review outputs from implementation-source scopes unless the gate is explicitly artifact consistency.
- Include superseded-review adjudication artifacts as context, not active findings.
- Update task TODO/progress files to name which delegation ids are superseded vs current.
- A companion approval does not satisfy a missing or superseded mandatory review leg.
- If fixing a stale review's valid finding changes source/tests/task docs, stale **all** review activity based on the pre-fix tree, including newer pending delegates and companion approvals that had passed. Save `SUPERSEDED_PENDING_REVIEW` artifacts for pending handles before dispatching the next bundle.
- Do not let repeated out-of-order completions produce review churn without evidence: each stale result must be adjudicated finding-by-finding. Only valid current-tree risks justify another code change and full rerun; stale/invalid findings get a saved disposition and no source churn.
- Treat late **approved** reviews with the same authority discipline as failed reviews. A stale pass is useful evidence, but not approval for a newer bundle; save it as `SUPERSEDED_APPROVED_REVIEW`, adjudicate non-blocking notes against the live tree, and keep the current gate fail-closed.
- If saving any late superseded review artifact (approved, failed, or pending disposition) changes the active artifact set after a newer consistency review was already dispatched, that newer review may no longer cover the full artifact set. Mark the newer pending review as superseded, regenerate the bundle including the late-result adjudication, and dispatch one replacement review against the current bundle. This applies even when the late result passed and only added bookkeeping.
- For artifact-consistency bundles that run stale-phrase scans, do not embed raw historical reviewer text that contains the exact stale phrases being scanned unless the review explicitly wants to judge those quotes. Preserve the finding in the saved superseded artifact, but rewrite quoted stale phrases into neutral descriptions (for example “treated real-card status as unresolved”) so future scans do not false-positive on historical evidence. If raw reviewer JSON must be saved, neutralize only the quoted stale phrases while preserving the verdict, bundle path, and adjudication.
- When a mandatory reviewer is explicitly model-overridden (for example Claude Code latest available Opus @ xhigh effort instead of the workflow default), every rerun must re-verify the model/banner before submitting the prompt and save the raw verdict separately from the structured JSON.

## Out-of-order multi-rerun pattern

A common failure mode in large `plan-code` tasks is a chain of async review results returning after later fixes have already produced a new bundle:

1. `deleg_A` returns failed against bundle 0 after bundle 1 exists.
2. A valid finding from `deleg_A` is fixed, creating bundle 2 and staling bundle-1 reviewers.
3. `deleg_B` later returns failed against bundle 1; one of its findings was already fixed by step 2, but another still applies.
4. Fixing the remaining finding creates bundle 3 and stales any bundle-2 pending/approved reviewers.

Handle this as a deterministic queue, not as a debate between reviewers:

- Save each stale result under a name that includes the delegation id and original bundle, e.g. `phase-2-codex-superseded-deleg_<id>.json`.
- Record `already_fixed_before_result_arrived`, `valid_current_findings`, and `stale_or_invalid_findings` explicitly.
- For each valid finding, make the smallest behavior-preserving fix and add a regression at the failing primitive boundary.
- Rerun the full phase verification when the finding affects financial/data-integrity primitives, even if a focused test passed.
- Generate a new bundle version after the final fix in that wave; do not reuse an older bundle just because one reviewer had already approved it.
- Dispatch fresh mandatory review lanes only after docs and pending/superseded artifacts truthfully identify the current bundle authority.

## Financial/data-integrity primitive loops

When stale async reviews repeatedly find financial or lifecycle primitive issues (payment state machines, ledger invariants, settlement distributions, idempotency, or compare-and-set races), handle each finding at the primitive boundary before moving to later phases:

- Treat reviewer-found money/state-machine warnings as worth-addressing unless a product decision is genuinely required. Fix the smallest repository/service primitive instead of deferring to later webhook/cron phases.
- Add a regression that proves persisted state, not just the returned value: failed→succeeded retry clears failure fields, terminal-state retry returns `null` without counters changing, invalid distributions do not persist, partial ledger updates leave prior amounts intact.
- Prefer atomic predicates/compare-and-set filters over read-validate-write-by-id for money tuples and settlement distributions. Include the fields that were validated in the update filter when a concurrent writer could invalidate the candidate.
- Validate the full candidate shape before persistence when a partial method writes strict-schema documents; post-write validation is too late for ledgers/settlements.
- After each such fix, rerun the full phase verification gate (not only the focused regression) and regenerate the bundle. Financial primitive fixes often affect downstream API/build surfaces and must stale every pending reviewer on the old bundle.
- Keep the user-facing status fail-closed: “phase gated on current review leg,” not “done except for review,” until all current verdicts are saved.

## Layered guard / exception findings

A stale reviewer can find a real current bug where an outer API/route guard shadows a narrower repository/service exception. This is common after adding lifecycle freezes or capability-boundary checks: the repository may correctly allow one safe exception, but the route rejects before the repository can enforce the nuance.

When adjudicating this class of finding:

- Trace both layers before deciding: route/API guard, repository/service guard, and any direct non-route callers.
- Preserve the durable invariant at the lower layer. The route should only avoid over-blocking; it should not become the only place that enforces the exception boundary.
- Use persisted markers for “has ever been in the sensitive state” when the current status is ambiguous. Example pattern: a `draft` answer with `publishedAt` set is a formerly-published draft, not a never-published draft, so terminal-root edit exceptions must continue to reject it.
- Make the route exception exact and positive rather than broad. Example shape: allow only `existing.status === 'draft' && !existing.publishedAt && requestedStatus === 'draft'`; keep publish, unpublish, published-answer edits, soft-delete, and formerly-published drafts frozen.
- Add regressions at both layers: one positive route + repository test for the allowed exception, and one negative route + repository test for the closest forbidden lookalike.
- After the fix, stale every pending/approved review lane that saw the pre-fix tree, regenerate the bundle, and rerun all mandatory review lanes. A companion approval that missed the layered-guard bug does not override the concrete stale-review finding.

## Example artifact

```json
{
  "review": "phase-n-codex-superseded-deleg_<id>",
  "status": "SUPERSEDED_FAILED_REVIEW",
  "passed": false,
  "bundle_path": "tasks/<task>/reviews/<old-bundle>.md",
  "superseded_reason": "Source changed after dispatch.",
  "current_tree_adjudication": {
    "valid_current_findings": ["finding still true"],
    "already_fixed_before_result_arrived": ["finding fixed by later work"]
  },
  "required_action": "Fix valid findings, rerun verification, regenerate bundle, rerun review lanes."
}
```
