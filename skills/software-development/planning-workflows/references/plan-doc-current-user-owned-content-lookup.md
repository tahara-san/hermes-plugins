# Plan-doc: Current-user-owned child content lookup gates

Use this reference when a plan-doc involves loading or editing the current user's existing child content under a parent resource, especially Q&A answers, comments, drafts, or submissions where the product contract says "one item per user per parent".

## Lesson

Do not let a frontend plan satisfy "load my existing item" by filtering a capped public list unless the API contract proves the list is exhaustive for that user. A public list endpoint with `limit`/pagination can miss the current user's item and cause duplicate creation or stale editor state.

## Required plan-doc gates

- Identify the authoritative lookup for the current user's existing item.
- Prefer a backend/session-derived lookup such as `mine=true`, `/me`, or an owner derived from auth/session, not a browser-supplied user id.
- If using a paginated public list fallback, require explicit exhaustive pagination, duplicate-safe behavior, and a performance ceiling before shipping.
- Pair lookup with a backend uniqueness/data-integrity gate when the product contract is one item per user/parent.
- Include negative acceptance criteria/tests: the implementation must not use capped public-list filtering as the shipping lookup.
- If backend support is missing, create/update backend instructions and stop before shipping a misleading frontend-only implementation.

## Review pitfall

Plan reviewers should fail a plan that says "fetch published items and filter by current user" when the included endpoint has a capped `limit` and no guarantee that all matching published items are returned.