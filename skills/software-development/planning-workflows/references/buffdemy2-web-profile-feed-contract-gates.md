# Buffdemy2-web profile feed API contract gates

Use when executing or reviewing a `plan-code` task that adds profile-level feeds in `buffdemy2-web`, especially feeds modeled after the Article feed but backed by Question / QuestionAnswer APIs.

## Pattern

Profile feed work can look frontend-only, but Phase 1 must prove the generic list API supports the feed's owner/cursor contract before UI finalization.

Required checks before deep UI work:

1. Verify the viewed profile user id from the live app/backend, not a guessed username string.
2. Probe the exact generic list query through the frontend proxy that the component will use.
3. Confirm the backend accepts every required query key and that the response passes the current frontend schema.
4. Browser-smoke the new route after schema/proxy changes, not only unit tests.
5. If a required generic query is missing, stop fail-closed and update task docs with the exact backend validator evidence.

## Question feed example

A generic question profile feed needs support for:

```text
/api/question?ownedBy=<profileUserId>&limit=20&status=published&sortBy=publishedAt&sortDirection=desc
```

If the backend list response is a smaller projection than the detail schema, add a focused schema regression before relying on it. In one captured case the backend question list returned sparse `stats` and an object-shaped `reward`; the frontend schema needed to default missing stat counters and normalize object reward to the numeric value consumed by current UI.

## Answer feed blocker pattern

Do not fake an answer profile feed by filtering visible question-thread answers in the frontend. The contract is answer-author ownership, not root-question ownership.

A generic answer profile feed needs a backend/API contract equivalent to:

```text
/api/question-answer?ownedBy=<profileUserId>&limit=20&status=published&olderThan=<cursor>&sortBy=publishedAt&sortDirection=desc
```

If the backend validator requires `question` and only allows per-question listing keys such as `question`, `status`, `limit`, `skip`, and `mine`, the Answer feed is blocked. Save the validator output in task notes and stop before claiming implementation completion or running final review gates.

## Documentation update on blocker

When the gate blocks:

- Save a `tasks/<slug>/notes.md` entry with command, observed error code, allowed query keys, and why it fails the product contract.
- Mark Phase 1 answer-owner/cursor/hydration TODO items as `[!]` blocked.
- Mark final simplify/review gates as not run rather than creating fake approvals.
- Report partial frontend work as incomplete and uncommitted.
