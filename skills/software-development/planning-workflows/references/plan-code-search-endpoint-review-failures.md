# Plan-code search endpoint review failures

Use when executing or reviewing a `plan-code` task that adds Elasticsearch-backed API search endpoints or rewrites search projections.

## Durable lessons

1. **Fail closed on missing ES responses, not just thrown errors.** Some search helpers catch client failures and return `null`; route-level `.catch()` blocks will not run in that case. Add an explicit `if (!response) throw ...` path in the model or route and test it.
2. **Keep the reviewed query scope identical to the contract.** If the endpoint contract says `/user/search` searches `name`, `displayName`, and `bio`, remove or gate broader legacy `contentTags` / `userTags` nested clauses. Otherwise candidates can match only tags even when boosts are correct.
3. **Reviewers should inspect both API routes and underlying ES model helpers.** Route tests can pass while model helpers silently broaden query scope or convert backend outages to empty results.
4. **Full-replacement search upserts need every producer audited.** Fixing a props-changed path is not enough; user-created, email-verification activation, and any future role-update paths must send fields needed by the full replacement document (`role`, `createdAt`, tags, status) or explicitly rely on a documented backfill/reset.
5. **Untracked implementation files must be in the final bundle.** New route directories and new tests are invisible to `git diff`; include `git ls-files --others --exclude-standard` and the full contents of intended untracked files in the review bundle.
6. **Review suggestions can reveal missing regression tests.** Add focused tests for fail-closed ES null responses, exact ES field boosts/scope, full payload fields, and changed-prop triggers before rerunning the review gate.

## Suggested verification additions

- ES model unit test: assert exact `multi_match.fields`, assert disallowed legacy fields are absent, and assert `null` search response throws.
- API route test: mock `SearchArticle.search()` or the model helper to return `null`/throw and assert 500 rather than `{ success: true, content: [] }`.
- Outbox tests: assert created/activation payloads include `userRole` and `userCreatedAt`; assert userTags-only profile changes emit a USER_PROPS_CHANGED outbox payload that survives schema validation.
- Bundle validation: grep the saved review bundle for truncation/dedup placeholders and make sure all intended untracked files are embedded before dispatching reviewers.
