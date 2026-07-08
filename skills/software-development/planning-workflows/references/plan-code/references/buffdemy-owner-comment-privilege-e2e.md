# Buffdemy Owner Comment Privilege E2E

Use this reference when adding or debugging Buffdemy frontend coverage for the owner-comment privilege contract: article owners can create comments/replies when the server-derived `article.privileges.comment.create` says they can, even if raw `acl.comment.create.allowedAudiences` is closed or the owner appears in a comment-create deny list.

## Scenario shape

- Add finite fixture scenarios rather than arbitrary ACL mutation, for example:
  - `ownerCommentClosed`: `acl.comment.create.allowedAudiences = []`, no user deny list.
  - `ownerCommentExplicitDeny`: `acl.comment.create.allowedAudiences = []`, owner id included in the write payload deny list.
- Seed at least one owner-created top-level comment before finalizing the closed/deny-list ACL so the E2E can exercise reply permalink behavior after the restrictive ACL is active.
- Return public ACL metadata in fixture summaries (`allowedAudiences`, `hasUserDenyList`) plus `privileges`, but do not expose raw `users.allow/deny` lists in the test response.
- Route unit tests should assert both the backend write payload shape (`allowedAudiences` plus `users.allow/deny`) and the public read shape returned to tests.

## Required E2E assertions

Before navigating the UI, fetch the fixture article as the owner and fail closed on backend preconditions:

```ts
expect(article?._id).toBe(fixture.article.id);
expect(article?.status).toBe('published');
expect(article?.privileges.comment.create).toBe(true);
expect(article?.acl?.comment.create.allowedAudiences).toEqual([]);
expect(article?.acl?.comment.create.hasUserDenyList).toBe(expected.hasUserDenyList);
```

Then assert the UI from the server-derived permission, not by reinterpreting raw ACL client-side:

- the closed-comment unavailable copy is absent;
- the comment composer placeholder is visible;
- submitting a top-level comment waits for a real successful server-action `POST` response (for example a `next-action` request with status `< 400`) and then asserts the submitted text appears;
- a seeded top-level comment has a reply link whose `href` is the comment permalink path;
- after navigating to the permalink, the reply-unavailable copy is absent, the composer is visible, and a real reply submission succeeds.

## If local E2E fails the owner privilege precondition

Do not weaken the frontend test and do not add frontend ACL fallback/migration code. The frontend contract is that `privileges.comment.create` is authoritative. If the local/backend environment returns `false` for the owner after a closed or deny-listed comment ACL:

1. Keep targeted route/component/unit coverage that proves frontend behavior for `privileges.comment.create === true`.
2. Log or update an out-of-scope backend/environment issue documenting the failed precondition and the exact E2E command.
3. Report the owner E2E as externally blocked until the backend owner privilege contract/migration is active, while preserving the fail-closed precondition in the spec.

## Pitfalls

- Do not determine owner commentability in the browser from raw `acl.comment.create`; use only server-derived `privileges.comment.create`.
- Do not expose raw ACL user lists from test-only fixture summaries just because the route needs them in write payloads.
- Do not rely on optimistic DOM updates alone; wait for the real server-action submit response so the E2E proves the privilege is honored server-side.
- Do not skip permalink/deep-link reply coverage; owner reply affordances can regress independently from the normal article page composer.
