# Out-of-Scope Issue Cleanup Audit

Use when the user asks to clean or triage `tasks/out-of-scope-issues/` without immediately implementing or deleting anything.

## Audit / cleanup sequence

1. Treat the request as a conservative dry-run audit unless the user explicitly authorizes edits/removals. If the user does authorize removal in the initial request (for example “verify and remove fixed/obsolete issues”), perform verification first, then delete only proven fixed/obsolete files in the same turn.
2. Enumerate every `*.md` issue file under `tasks/out-of-scope-issues/`, including nested `manual/` folders.
3. Check `git status --short -- tasks/out-of-scope-issues` first so the report can distinguish tracked cleanup candidates from unrelated or user-owned dirty work. Do not absorb or revert unrelated dirty issue edits unless they are the exact cleanup target.
4. Read each issue file in full and extract: issue, location, severity, context, and suggested fix.
5. Verify each issue against current source/tests/docs using the exact paths and symbols named in the issue. Do not rely on checklist wording alone.
6. Also inspect recent commits and task artifacts when the user says recent work should have resolved old issues. A completed task’s final report/spec/TODO can prove an old issue is superseded, but still cross-check at least one current source/test path when local code owns the behavior.
7. Classify each issue as one of:
   - **Already fixed** — current source clearly implements the suggested fix or removes the obsolete condition.
   - **Obsolete / superseded duplicate** — another current tracker or authoritative source has replaced it.
   - **Partial / stale-as-written** — some work landed, but a narrower residual issue remains.
   - **Still active** — current source still matches the reported problem.
   - **Manual/source-of-truth external** — local repo cannot prove resolution; inspect the authoritative external source when accessible.
8. For external-source issues, prefer the source of truth over local stale prose. Example: Dependabot alert counts should be checked through GitHub Dependabot/API if credentials allow; local push-banner notes are stale trackers, not truth.
9. If removals were authorized, delete only **Already fixed** and **Obsolete / superseded duplicate** files. Keep **Partial / stale-as-written** files unless the residual is fully covered by a newer tracker or the user explicitly accepts the remaining risk as deferred elsewhere.
10. If removals were not authorized, report cleanup candidates only; do not remove files, patch docs, or implement fixes until the user approves.

## Evidence patterns

- For fixed code issues, cite the current file/symbol that now implements the missing behavior.
- For fixed test-infra issues, prefer focused test/helper source plus a real focused verification command when practical.
- For still-active issues, cite the current file/symbol that still shows the stale behavior.
- For duplicate/stale trackers, cite both the local stale value and the current authoritative value or replacement tracker.
- For broad baseline trackers, remove them only when a newer task/artifact or newer issue set captures the current baseline and remaining failures at equal or better granularity.
- For partial issues, separate completed pieces from residual work so the user can decide whether to refresh or remove the file. If a task final report explicitly says “do not remove yet” or “partially resolved,” keep the issue unless newer evidence proves the residual root cause is gone too.
- For order-dependent E2E trackers, run both the normal mitigated project/directory command and a stricter historical-order repro when cheap: refresh auth/setup, run the suspected poisoning specs first, then run the victim spec. If both pass and current source has a capability/isolation fix, the tracker can be classified as stale/resolved.

## Cleanup details

When removing a resolved issue file, search for source comments or docs that link to that exact tracker path. If a source comment still points to the soon-to-be-deleted file, patch it to describe the current invariant in plain terms or remove the stale claim before staging the deletion. Run a narrow grep/readback to prove no stale path references remain.

## Pitfalls

- Do not mark a broad proposal resolved just because its original concrete example was fixed; preserve or narrow the broader audit if still useful.
- Do not mark manual issues resolved from local code when their authoritative state lives in GitHub, Stripe, cloud dashboards, or another external system.
- Do not let unrelated dirty work under `tasks/` get staged or absorbed into the cleanup.
- Cleanup is conservative: ambiguity means keep or ask, not delete.
