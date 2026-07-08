# Plan-code: legacy vs live contract evidence

Use this when a `plan-code` task targets a model/path named in an older issue, but current source has a newer live implementation under a different name or route.

## Trigger

During implementation or review, you discover both of these are true:

- The changed code is a legacy/exported stack such as `QuestionComment` / `/question-comment`.
- The actually live UI/backend contract uses a newer sibling such as `QuestionFollowUpComment` / `/question-follow-up-comment`.

## Required handling

1. **Do not overclaim end-to-end coverage.** If backend verification covered the newer live endpoint, do not phrase it as proof that the legacy endpoint consumed by the changed model returns the same field.
2. **Classify the changed stack.** Search for live callers outside its own model/schema/barrels/actions. If no app/component/UI callers exist, record the change as legacy alignment / future-proofing, not the live contract-bearing path.
3. **Check the live path separately.** Verify whether the current live model/schema/tests already carry the target contract. If they do, document that the live path is already covered and avoid duplicating or broadening work.
4. **Keep required fields fail-closed.** If the task is current-contract only, requiring the new canonical field is fine, but record the residual risk: rewiring a legacy endpoint that does not actually return the field will fail at parse time.
5. **Patch task docs before final review if the bundle/docs overclaim.** Reviewer notes like “backend assertions target a different endpoint” are non-blocking only if the docs accurately distinguish legacy alignment from live endpoint proof. If the task docs or bundle imply stronger coverage, regenerate the bundle and rerun required review gates before claiming completion.

## Review prompt add-on

Ask reviewers to check:

- whether the modified frontend path and verified backend route are the same endpoint;
- whether there is a live caller for the modified legacy stack;
- whether task docs distinguish legacy alignment from live-path contract coverage;
- whether `rootQuestion`/canonical fields are required without old-payload fallbacks when the plan says current-contract only.
