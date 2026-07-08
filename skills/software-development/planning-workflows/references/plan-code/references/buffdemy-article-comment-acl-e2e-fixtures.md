# Buffdemy Article Comment ACL E2E Fixtures

Use this reference when implementing frontend E2E coverage for article/comment ACL behavior in Buffdemy plans. For owner-specific closed/deny-listed comment ACL coverage, also consult `references/buffdemy-owner-comment-privilege-e2e.md`.

## Durable fixture pattern

- Prefer a narrow test-only API route over broad generic seeders when the test needs server-side state that normal UI flows cannot reliably create.
- Gate the route behind the existing E2E hardening flag (`isE2EHardeningEnabled()` or the project-equivalent) and return `404` when disabled so it is invisible outside hardened E2E runs.
- Restrict fixture ownership to the expected seeded account by stable identifier (email), not display name.
- Keep scenario names explicit and finite (for example: readable-but-comment-denied, existing-denied-thread, restricted-read) rather than accepting arbitrary payload mutation.
- Do not create migration/backward-compatibility paths for fixture routes unless the task explicitly asks for them.

## Fixture identity and cleanup safety

Before mutating or cleaning up article fixtures, verify all available scope markers, not just a title prefix:

- deterministic title prefix;
- expected test tags (for example `e2e` and `acl`);
- expected fixture owner email;
- expected fixture/source marker if the model supports one.

Cleanup should fail closed if the article cannot be fetched or positively identified as a fixture. Avoid best-effort deletion of production-shaped data.

## E2E assertion pattern

- For stale-submit paths, prefer fixed action-specific fixture mutations over caller-selected payloads when the safe mutation has only one intended value (for example `denyCommentCreate` should hard-code an empty comment-create audience list, and `markDeleted` should hard-code the deleted status). This keeps the test-only route narrower than a generic ACL/status mutation API.
- Create and mutate the fixture with a user1-authenticated helper/context, then fetch it as the target viewer (for example user2) before UI navigation to verify effective server privileges.
- If an owner-override E2E suite uses conditional skips for missing backend owner privileges, treat “green with skipped owner browser tests” as a documented backend blocker, not a completed owner UI verification. Do not remove task files or mark final owner verification complete until the suite actually runs the owner assertions.
- Before asking the user to enable/apply a backend owner-comment contract, gather enough evidence to distinguish backend API behavior from frontend Next proxy/session issues:
  - create a temporary diagnostic spec/helper if needed, then remove it;
  - print or assert fixture owner id/name, viewer-fetched owner id/name, `privileges.write`, public `acl.comment.create`, and `privileges.comment.create`;
  - inspect the Next `/api/article` path (`Article.fetchInitProps` → `api.fetch('/article/')`) to confirm whether Next forwards backend `content` rather than recomputing privileges;
  - if `privileges.write === true` but `privileges.comment.create === false`, auth mismatch is unlikely, so investigate backend `/article/` privilege computation, fixture ACL semantics, or stale/wrong `SERVER_API_*` target.
- If a user2-authenticated Playwright project creates fixtures through user1 state, make that project depend on both auth setup projects (for example `setup-user1` and `setup-user2`) so the storage state exists before the spec runs.
- Assert both normal article rendering and deep-link/permalink comment paths. Permalink reply UI can differ from standard article comment rendering.
- For readable-but-not-creatable states, assert existing top-level comments/replies remain visible while composer placeholders, reply buttons, or submit affordances are absent.
- For restricted-read preview states, assert the server payload first: `privileges.read === false`, real public metadata is present, first preview paper is present, and later papers/body content are absent before asserting UI visibility.
- Cover stale-submit paths separately when possible: revoke comment creation or article commentability after the page is loaded, then assert the expected AppError-code toast/translation path.

## Backend write-shape ACL from frontend fixture routes

When a Next.js test-only fixture route calls backend article mutation endpoints, do not send the public/read ACL shape back to the backend. Public article payloads may contain read-shape fields like `hasUserAllowList`, `hasUserDenyList`, and `version`, but update payloads expect write-shape rules:

```ts
type ArticleAclRuleWritePayload = {
  allowedAudiences: ContentAclAudienceType[];
  users: { allow: string[]; deny: string[] };
};
```

Use a small converter from fetched article ACL to write ACL before `PUT /article/:id`, and keep test-only scenario builders finite rather than exposing arbitrary ACL mutation.

## Restricted-read fixture owner access

For fixtures that intentionally make `read.allowedAudiences = []`, preserve cleanup/mutation access for the creator by adding the created article owner id to `read.users.allow`. Prefer deriving this from the created article (`article.ownedBy?._id`) instead of a separate session lookup, because it guarantees the allow-list matches the actual owner identity returned by the backend.

## Helper error handling

Route helpers should funnel create/mutate/cleanup calls through one `postFixture` helper that throws response status plus body. This makes fixture-stage failures (for example `finalize_acl: invalid_update_payload` or `article_fixture_scope_violation`) visible in Playwright output instead of hiding them behind `expect(response.ok()).toBe(true)`.

## Review pitfalls

- A reviewer may flag fixture cleanup as dangerous if identity checks rely only on title. Strengthen scope checks instead of documenting the risk away.
- Name-based fixture owner checks are brittle; use seeded email or exact session/user id; only fall back to names as a temporary diagnostic, not as final cleanup authorization.
- If restricted preview payloads omit owner email, solve identity safety with exact owner id/session id checks rather than weakening to display/name checks.
- Keep helper imports narrow in browser/jsdom-facing tests to avoid pulling server-only barrel side effects into Playwright/Vitest contexts.
