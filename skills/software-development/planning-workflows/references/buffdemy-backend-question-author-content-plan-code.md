# Buffdemy backend Question author-content required plan-code execution

Use this when executing a Buffdemy backend plan-code task that removes caller `Question.title`, restores required author content, or replaces title-only/optional-content behavior with a rendered-text minimum.

## Implementation contract

- Remove `title` from `POST /question` and `PUT /question/:question` write schemas and handlers; reject caller `title` explicitly (`additionalProperties: false` and/or `t.Never()` is acceptable).
- Keep persisted/display/search `Question.title` only as a derived compatibility field unless the task explicitly expands to response/search/frontend removal.
- Derive title from normalized rendered content, not caller input.
- Enforce the minimum at author write boundaries before any parent/content/outbox/stale-derived side effects.
- Scope the author minimum outside universal ready-row reads and machine/manual derived rows. Do not add global `.min(16)`-style constraints to shared ready-row schemas used for hydration/read paths.
- Partial content update schemas must stay partial and must not default omitted body/papers into destructive empty updates.

## Rendered-text minimum details

- Extract rendered/editor text through the same family of helpers used by paper/body derivation, not via `JSON.stringify(bodyNodes)`.
- Normalize whitespace before counting if frontend/editor behavior treats internal whitespace/newline runs as one visible separator.
- Count Unicode code points (`Array.from(normalized).length`) rather than UTF-16 code units.
- Pin the chosen normalization with tests. A useful regression is two papers whose persisted body joins with `\n\n`: one case where normalized visible text is 14 and must reject, and one where normalized visible text is exactly 16 and must pass.
- Media-only or missing-media-only content does not satisfy a text-required Question contract unless the product explicitly changes that rule.

## Tests to update or add

- API schema tests proving `title` is not accepted and content/papers are structurally required.
- API route tests for valid exactly-16 content and invalid omitted/empty/contentless/rendered-short payloads, plus no parent/content/outbox side effects on rejection.
- Repository create/update tests for direct-call rejection, exactly-16 acceptance, emoji/code-point boundaries, normalized multi-paper whitespace, and preservation of existing rows/version on rejected update.
- QuestionContent author-row tests proving author ready rows below the minimum reject while derived/manual/machine ready rows and ready-row reads remain unaffected.
- Downstream fixture/service tests that previously supplied caller title: API route fixtures, test-only ACL fixtures, outboxProcessor, unifiedConsumer, and cronWorker.

## Verification and review pattern

- Prefer focused API/mongo/service checks over broad noisy suites, but still run broad package checks when feasible and document unrelated deviations with evidence.
- If a Bun test command with several files fails from `mock.module` suite-order leakage, split the files into isolated groups and verify the exported runtime symbol directly when relevant; record the combined-run limitation instead of expanding mocks with unrelated exports.
- For mandatory final review bundles, include untracked helper/task files explicitly; plain `git diff` omits them.
- Exclude historical plan-review bundles and superseded raw review artifacts from active implementation review scope, or reviewers will correctly flag stale old contract text.
- If a final implementation bundle is over the Hermes `read_file` safety limit, either shrink it or instruct delegate reviewers to read it in ranges. If the delegate completes despite the initial read error, recover the child session verdict from logs/session history and save the recovered parseable JSON artifact.
- For interactive Claude review of a large bundle, if it stalls after reading the bundle, interrupt and request a no-tools verdict based only on context already read. Save the raw pane including the interruption/recovery and only count it if it returns an explicit verdict.

## Final artifact consistency

Before claiming completion:

- Parse final JSON review artifacts.
- Verify final aggregate `passed: true` and both review legs have no blocking findings.
- Scan live `todo.md` for real `[ ]`, `[~]`, or `[!]` rows, ignoring only legend examples.
- Check the active final bundle for truncation/cache placeholders.
- Run `git diff --check` after all task-doc/review-artifact edits.
- Write a self-excluded `final-artifact-consistency.json` if review artifacts or final docs were written after implementation review approval.
