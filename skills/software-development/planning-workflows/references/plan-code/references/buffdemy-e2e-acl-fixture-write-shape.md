# Buffdemy E2E ACL Fixture Write-Shape Notes

Use this when adding or debugging `src/app/api/test-only/*` fixture routes for article/comment ACL coverage.

## Backend ACL mutation payloads

Article create/read responses expose a public ACL shape, but article update endpoints expect the editor/write shape.

- Public/read shape commonly includes flags such as `hasUserAllowList`, `hasUserDenyList`, and `version`.
- Write/update shape should be:
  - `allowedAudiences`
  - `users: { allow, deny }`

When a fixture route fetches an article and then updates its ACL, convert public ACL rules back to write shape before calling the backend `PUT /article/:id` route. Do not pass public ACL flags back into the mutation payload.

## Restricted-read fixture pattern

For fixtures that lock `read` after article creation but still need creator cleanup:

1. Create the article as the fixture owner first.
2. Derive the read allow-list from the created article owner id, e.g. `article.ownedBy?._id ? [article.ownedBy._id] : []`.
3. Mutate the article ACL to `read.allowedAudiences = []` plus the owner allow-list.
4. Verify as the restricted viewer that:
   - `privileges.read === false`
   - public metadata remains present
   - only the first public-preview paper is present
   - protected later papers are absent.

Avoid a separate session-id lookup when the created article already contains the owner id; using the article owner keeps the allow-list aligned with the actual resource.

## Cleanup and ownership safety

Fixture cleanup/mutation routes should fail closed before touching data:

- Require the fixture title/prefix and fixture tags.
- Require exact ownership by owner email when present, or exact owner `_id` matching the current session user id.
- Avoid name-only fallback checks for cleanup safety; display names are not durable authorization identifiers.

## E2E setup dependency

If a user2 Playwright project seeds data through user1 storage state, make that project depend on both setup projects (`setup-user1` and `setup-user2`). Otherwise the user1 storage state may be missing even though the test itself runs as user2.

## Helper behavior

Prefer shared fixture request helpers that surface non-2xx response bodies. Cleanup failures are much faster to diagnose when helpers throw the fixture route JSON error (for example `article_fixture_scope_violation`) instead of only a generic HTTP status.