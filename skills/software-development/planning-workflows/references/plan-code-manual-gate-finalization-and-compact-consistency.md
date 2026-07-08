# Plan-code manual-gate finalization and compact consistency retry

Use when a `plan-code` task is functionally complete except for human/manual gates, then the user completes those gates interactively and final artifact consistency must be rerun.

## Pattern

1. Guide manual gates one action at a time.
   - Ask for the smallest observable confirmation needed next.
   - Do not ask for secrets or one-time Stripe/Connect URLs; record only non-secret facts.
   - Distinguish user-observed dashboard/browser facts from agent-verified live state.
2. When a manual gate completes, save a durable evidence artifact such as `manual-gates-confirmed-YYYYMMDD.md`.
   - Include user-confirmed dashboard/browser observations.
   - Include agent read-only live-state probes when available.
   - Explicitly say no real `.env` / `.env.*` files were read if that constraint applies.
3. Patch live task docs/checklists to point at the manual-gate evidence, but do not mark the whole phase complete until a post-update artifact-consistency review passes.
4. Before building the consistency bundle, scan every artifact you intend to include as active evidence for stale present-tense blocker phrases.
   - Common offenders are diagnostic/simplify artifacts that were true when written but later superseded, e.g. `Phase remains incomplete until manual gates are confirmed`, `remaining blocker`, or `real-card success path remains open`.
   - Patch those sections to `Historical note` / `superseded on <date>` wording if the artifact remains active evidence.
   - Alternatively exclude broad historical artifacts from the active bundle and reference them as historical only.
5. If a final consistency review fails on stale artifact wording, save the failed verdict, patch only the named stale sections, regenerate the bundle, and rerun.
6. If a broad consistency bundle times out, save the timeout as an incomplete gate and retry with a compact active-scope bundle.
   - Include current live task-doc snippets, current manual-gate evidence, stale-phrase scan output, and disposition of failed/timeout reviews.
   - Do not embed large historical bundles or raw reviewer prose unless they are the subject of the check.
   - State self-exclusions for the pending marker and the not-yet-existing verdict artifact.
7. Treat all delayed async results by bundle authority.
   - Passed verdicts for prior bundles become superseded evidence after task docs/review artifacts change.
   - Timeouts are not approval.
   - Failed verdicts remain historical blocker evidence after their blockers are patched.

## Verification checklist

- Manual-gate evidence artifact exists and contains no secrets/one-time URLs.
- Live task docs reflect manual gates as confirmed but final consistency as pending until review passes.
- Active stale-phrase scan is clean for included active artifacts.
- New bundle has no truncation/cache placeholder markers.
- Pending marker JSON validates.
- Scoped `git diff --check` passes after artifact edits.
- Only after the final consistency verdict passes: canonicalize the verdict, update pending marker to passed, mark the phase complete, validate JSON, and rerun scoped `git diff --check`.

## Pitfalls

- Do not include old diagnostic or simplify notes as active evidence without updating stale present-tense caveats; reviewers will correctly fail the bundle.
- Do not let a large historical evidence bundle cause repeated timeouts. Compact artifact-consistency reviews are valid when implementation logic has already passed review and only final docs/evidence changed.
- Do not count a dispatch, timeout, or superseded pass as a current approval.
