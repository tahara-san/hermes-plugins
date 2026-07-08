# Completed plan-code artifact staging pitfalls

Use this during `plan-commit` for a completed `plan-code` task whose task directory contains generated review bundles, raw verification logs, and stale/superseded review markers.

## Stale pending markers after recovered reviews

If a mandatory async/delegate review was once pending but later returned and was saved as a final artifact:

1. Save the returned verdict under the canonical final path, e.g. `reviews/codex-implementation-review-final.json`.
2. Update the aggregate review (`reviews/final-review.json`) and live TODO/final report to reference the final artifact.
3. Remove or clearly supersede the old pending marker before staging. A stale `*-pending.json` with `passed: null`, `not complete`, or `review has not returned` wording is misleading commit content once the final verdict exists.
4. If a replacement review was dispatched only because the first rerun was late, and both eventually return passing, save the replacement as supplemental evidence instead of reopening the gate. Update the replacement pending marker and aggregate review with a `supplemental_reviews`-style entry, then run lightweight JSON/marker validation. Do not rerun implementation verification or reviews unless the supplemental result reports a blocker/current-risk issue.
5. Run a pre-commit artifact-consistency check that verifies no real `[ ]` / `[~]` TODO rows remain outside the status legend and that final review artifacts exist and pass.

## Ignored verification logs referenced by committed artifacts

Task final reports and aggregate reviews sometimes point to `reviews/logs/*.log`, while repo ignore rules may ignore `*.log` or nested log directories. Before committing:

- run `git status --short --ignored -- tasks/<slug>` to detect ignored logs;
- if the final report/review references those logs, force-add exactly those intended logs with `git add -f tasks/<slug>/reviews/logs/*.log`;
- do not force-add unrelated logs or broad ignored directories.

## Generated bundle whitespace normalization

Large generated Markdown bundles can fail `git diff --cached --check` with trailing whitespace from embedded diffs/logs. Normalize only generated task artifacts, restage, then run:

```bash
git diff --cached --check
```

Because normalization occurs after the implementation review, save a narrow post-normalization consistency artifact that states:

- normalization scope;
- no source/test behavior changed;
- `git diff --cached --check` passed;
- the consistency artifact excludes itself from its own reviewed scope.

This does not require rerunning the full implementation review when the only post-review change is generated-artifact whitespace normalization, but the final commit response should name the post-normalization check.
