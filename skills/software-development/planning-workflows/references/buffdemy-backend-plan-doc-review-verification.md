# Buffdemy backend plan-doc verification/review pitfalls

Use this reference when creating or reviewing Buffdemy backend `plan-doc` task directories, especially cross-app backend plans that cite many package/app verification commands.

## Copy-pasteable command blocks

When a verification block is meant to be run from the repo root, avoid sequential lines like:

```bash
cd packages/mongo && bun test ...
cd packages/redis && bun run build
```

After the first `cd`, subsequent relative `cd` commands are evaluated from the package directory and can fail. Prefer subshells so every command starts from the repo root:

```bash
(cd packages/mongo && bun test ...)
(cd packages/redis && bun run build)
(cd apps/api && bun run build)
```

This is a review-gate issue for plan-docs because the later implementer should be able to paste the block without rediscovering working directories.

## Bash syntax checks for multiple scripts

When a verification block needs to syntax-check multiple Bash scripts, do **not** write `bash -n script-a script-b`. Bash treats later path arguments as positional parameters for the first script, so only `script-a` is checked and the command can exit 0 even if `script-b` is missing or invalid. Use explicit chained commands or separate bullets instead:

```bash
bash -n scripts/check-dev-mounts && bash -n scripts/up
# or:
bash -n scripts/check-dev-mounts
bash -n scripts/up
```

This is a plan-doc review issue because verification commands must be copy-pasteable and prove the claimed files were checked.

## Cron-worker tests need preload

For Buffdemy backend `apps/cronWorker`, focused `bun test` commands must include the same preload as the package script:

```bash
(cd apps/cronWorker && bun test --preload ./src/test/preload.ts src/test/jobs/<test>.test.ts)
```

Docker-compose equivalents also need the preload:

```bash
docker compose exec -w /app/apps/cronWorker cron-worker bun test --preload ./src/test/preload.ts src/test/jobs/<test>.test.ts
```

## Redis feed verification

If a plan adds Redis feed functionality, include a focused Redis feed test command as well as the build command. In this repo, `packages/redis/__tests__/feed.test.ts` exists and is a sensible target when the plan extends feed member parsing or mixed content types.

## Lifecycle/privilege consistency check

For Q&A-style plans, ensure route privilege rules and repository lifecycle rules say the same thing. Example: if `close` privilege is false after `expiresAt <= now`, the manual-close repository method should also reject after expiry and leave the expiry job to set `closedReason: expired`.

## Stable error-code families

Backend API plans should name stable `AppError` code families for ACL denials, lifecycle conflicts, unsupported reaction target/type combinations, hidden private-resource misses, unsupported query params, and invalid/missing required query values. This keeps later implementation/tests from asserting on messages.

## Query-param contract precision for Buffdemy API plan-docs

When a backend plan-doc defines public/read endpoints with bounded query params, make the validation semantics implementation-proof:

- If the contract says a numeric param is **clamped** (for example `limit=50` returns at most 10), explicitly state that the route schema must accept the broader numeric input and clamp in the handler. Do not leave implementers to copy `t.Numeric({ maximum: 10 })`, which rejects out-of-range values instead of clamping.
- For repeated query params, name the parser strategy explicitly (for example `new URL(request.url).searchParams.getAll('id')`) when order/duplicates matter. Call out Elysia's string-vs-array coercion quirk if the adjacent code already relies on it.
- Distinguish missing required query params from present-but-invalid values in the planned error codes, even if both are client errors.
- If framework schema validation may return 422 while route-level guards return 400, write tests to allow `400 || 422` unless the plan requires one exact status. Existing Buffdemy user-route tests already use this pattern for ObjectId validation.
- Cross-reference every error code named in TODOs from the endpoint behavior section so implementers and reviewers do not have to infer which guard emits which code.

## Frontend-unblocking backend media contract plans

When a Buffdemy frontend `plan-code` task is blocked because the frontend cannot supply a backend identifier, create the companion backend `plan-doc` in `/workspace/dev/buffdemy-backend/tasks/<slug>/` and make the backend contract explicit. For profile avatar/cover delete, prefer the idless authenticated route pattern (`DELETE /user/avatar`, `DELETE /user/cover`) over exposing internal media ids when the frontend only holds `user.<field>.rootKey`. In the plan:

- Preserve existing `/:id` routes unless the user explicitly asks for a breaking contract change.
- Derive the idless target solely from authenticated backend user context; never accept owner/viewer/media ids or root keys from the browser.
- Use the active user-field root key (`user.avatar.rootKey` / `user.cover.rootKey`) as source of truth, not the newest profileMedia row; newer draft uploads can exist while an older image is still displayed.
- Require a narrow lookup by `ownedBy + type + keyRoot` (or an explicitly equivalent helper). Avoid `findByUserAndType` for active-image delete plans because it selects latest, not active.
- Specify data-drift behavior separately from terminal idempotency: absent matching row should be a stable drift error (for example `profile_media_not_found`) unless the product chooses repair; a present-but-deleted row with a dangling user field can be a rootKey-guarded stale-field cleanup without a fresh outbox emit.
- Include tests for success, no-active no-op, delete-twice idempotency, present-but-deleted stale-field cleanup, active-vs-latest, drift/no-mutation/no-outbox, authentication, and client-controlled target data being ignored.
- Give idless routes their own no-params/no-body Elysia schema/detail; do not reuse a `/:id` params schema.

## Bundled handoff authority and stale command reconciliation

When a Buffdemy backend plan-doc includes a frontend handoff or sibling-repo task doc as source context, explicitly classify authority in the backend task bundle:

- Product requirements from the handoff may be authoritative, but command examples and implementation sketches can be stale relative to backend `AGENTS.md` / current package scripts.
- If the handoff contains older root/workspace-filter build commands, state in `spec.md`, `todo.md`, and the kickoff prompt that the backend task's per-package verification commands supersede them. This is especially important in this repo because root `bun run build` / `bun --filter ...` forms are known to fail with Bun workspace-filter ENOENT.
- Do not patch the sibling frontend handoff during a backend-only plan-doc unless the user asked for cross-repo doc edits; reconcile the conflict inside the backend task docs and review bundle instead.
- Review bundles should include a scope note saying handoff examples are context-only where contradicted by backend task docs.

## Unique-index plan-doc fixture conflicts

When a Buffdemy backend plan-doc adds a unique or partial-unique MongoDB index, inspect existing tests for deliberate duplicate/corrupt-data fixtures before finalizing the plan. If a new index makes an existing fixture unconstructible, the plan must name the affected test and decide its fate:

- remove or rewrite obsolete duplicate fixtures when the new contract makes duplicates unsupported;
- repurpose a fixture as a legacy corruption/integrity-conflict test using direct collection setup;
- never weaken a requested unique-index contract just to keep an old duplicate-creating repository helper path working.

For corruption tests under a new unique index, specify a constructible seeding strategy: temporarily drop the specific index for that isolated test, insert duplicate rows directly, assert the integrity-conflict path, and rely on normal `beforeEach` index setup to restore the baseline. Also verify the planned `partialFilterExpression` is legal for the target MongoDB version; for active-status partial indexes, prefer explicit active statuses such as `$in: ['draft', 'published']` over unsupported/non-portable `$ne` filters.

## Shared guard carve-outs in lifecycle plans

When a backend plan carves out a lifecycle exception in a shared route guard (for example allowing question-answer unpublish from `closed/all_answered` roots), require the plan to state the carve-out is opt-in at the specific call site and transition. Add negative tests for adjacent shared call sites that must remain blocked (for example POST, draft→published, or DELETE) so implementers do not accidentally broaden permissions through the shared helper.

## Media quota/provider-metadata plan-doc pitfalls

When a Buffdemy backend plan-doc designs media usage quotas around Cloudflare uploads:

- Distinguish presign/request claims from provider-confirmed facts. In particular, `POST /media` `size` is client-claimed until upload completion; require either a provider-confirmed overwrite plus authority marker (for example `sizeSource: 'provider'`) or an explicit limitation that the value remains client-sourced and is not authoritative.
- If quotas are scoped by post type, require an explicit request/model context field (`postType: 'article'`, etc.) rather than silently inferring from the generic media route.
- For unknown Stream duration at presign time, document the tolerated-overflow policy and the concurrency guard. A robust V1 plan allows at most one pending unknown-duration reservation and rejects additional pending uploads to prevent multiplying the overflow.
- Make stale non-terminal reservation semantics deterministic. Prefer counting `created`/`uploaded` reservations until terminalized instead of leaving expired pending rows as an implementation choice, unless the plan also adds verified cleanup guarantees.
- Include webhook and cron fallback completion paths in the same acceptance criteria whenever adding provider-confirmed media metadata such as `durationSeconds`, dimensions, size, or authority markers.

## Validation-relaxation plan-doc pitfalls

When a Buffdemy backend plan-doc relaxes validation from required/non-empty content to optional/empty content (for example allowing title-only Question content with `body: ''` and `papers: []`):

- Trace every enforcement point, not just the public route schema: route TypeBox schemas, repository input types, pre-normalization helpers that filter empty payloads, create/update guards such as `!validated.length`, Zod create/document/ready schemas, response resolvers, and projection/search serializers.
- Explicitly name existing negative tests that are expected to flip or be removed. If an old test asserts “empty ready content rejects,” the plan should say whether the new contract makes that row valid, whether only the canonical write path (`[]`) is valid, or whether a malformed/minimal placeholder should still reject.
- Do not make downstream projection tests conditional only on editing projection source when the data-shape change will flow through projection at runtime. Either add a focused serializer/projection regression for the empty shape or record verified evidence that the existing serializer is empty-safe.
- Prefer canonical empty storage (`body: ''`, `papers: []`) over fabricated minimal paper payloads unless a verified downstream dependency requires the placeholder; if so, document the dependency and keep the placeholder shape centralized.

## QuestionAnswer/schema-extension plan-doc pitfalls

When planning Buffdemy backend schema extensions that also affect frontend models (for example adding a required nullable field to `QuestionAnswer`):

- If the new field may later need a write route/UI, gate that phase on **explicit user confirmation**. Do not use wording like “if an existing product caller exists” for a brand-new field; it is subjective/dead criteria and can accidentally broaden a schema-only task.
- If the repository class forbids inherited raw mutations, require a dedicated repository method for any new write path (for example `setQuestionOwnerFeedback()`), and state that route code must not bypass repository raw-mutation guards.
- When a frontend API schema makes a previously absent field required, add a full frontend type-check command (for example `npx tsc --noEmit`) in addition to focused tests/lint, because scattered typed fixtures and model literals outside the focused tests can break.
- For frontend model hydration, distinguish API/init/source props from instance props: serialized nested content should remain Paper/source props, while instance schemas/classes hydrate to `Paper`; `getInitProps()` must serialize nested hydrated objects back with `getInitProps()` and preserve `null`.
- For final plan-doc review bundles, label source excerpts as context-only and verify they are not empty (`Total lines: None`, empty sections) before dispatch when they are needed as review evidence. If an already-reviewed bundle has cosmetic missing context that does not affect plan-doc readiness, record it as non-blocking rather than editing artifacts after final approval.

## Mongo transaction/outbox refactor plan-doc pitfalls

When writing Buffdemy backend plan-docs for Mongo repository performance, transaction trimming, or outbox route refactors:

- Restate the root `CLAUDE.md` one-container-per-async-call rule anywhere the plan edits `withTransaction` or `withOutboxTransaction` callback bodies. The implementer must keep each awaited async call's error container freshly declared inside the callback so Mongo transaction retry re-entry cannot reuse stale outer error state.
- Be explicit that shrinking transaction bodies is not the same as removing event semantics. For reaction/refcount-style plans, say route code may still branch on an atomic mutation result to select the correct outbox event (`CREATED`, `UPDATED`, `DELETED`, or no-op); only the extra read-before-write branch is being removed.
- Keep phase numbering aligned across `spec.md`, `todo.md`, and `kickoff-prompt.md`. If one doc splits verification and review into separate phases, update the others too; reviewers treat mismatched numbering as avoidable implementer confusion.
- For plan-doc reviews, save any first-pass approval with useful non-blocking suggestions as `*-initial-superseded` before patching docs. Regenerate the bundle and rerun all required review legs on the patched docs before claiming final approval.
- Exclude `reviews/` artifacts from the reviewed plan-doc bundle scope, or state the exclusion explicitly, then save an aggregate verdict afterward. This avoids self-referential stale-review loops where the act of writing review artifacts changes the reviewed bundle.
- If final reviewers return only trivial wording polish after all substantive fixes, record the suggestions and intentionally leave them unedited rather than creating another stale review cycle.
