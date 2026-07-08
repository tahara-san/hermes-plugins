# Buffdemy backend: stale `docs/` authority pitfall

Use this when a Buffdemy backend plan/review/test-fix task cites files under `docs/` as evidence for an API contract, implementation goal, or expected error code.

## Durable lesson

For Buffdemy backend, files under `docs/` can be transient instruction/spec notes and may be stale. They are context only unless the user explicitly says a particular doc is the source of truth.

Do not let a reviewer blocker stand solely because a `docs/...` file disagrees with live source/tests/product instructions. Reclassify that as a stale-doc authority question and patch the task docs/review bundle before implementation.

## How to apply in `plan-doc`

1. If a plan decision relies on `docs/`, label the authority level explicitly:
   - `authoritative`: only when the user explicitly elevates the doc for this task.
   - `context only`: default for Buffdemy backend `docs/` files.
2. Build review bundles with this note so external reviewers do not treat `docs/` matches as contract evidence by default.
3. If a reviewer cites a `docs/` match as a blocker, check whether the user elevated that doc. If not, save the review as superseded, patch the plan, regenerate the bundle, and rerun the review.
4. Prefer live `apps/` and `packages/` source, tests, route schemas, and explicit user instructions for contract decisions.

## How to apply in `plan-code`

When aligning tests to implementation after a backend refactor:

1. Search live source/package references first, excluding review artifacts. Example:

   ```bash
   git grep -nE '<old_code>|<new_code>' -- apps packages ':!tasks/<slug>/reviews/*'
   ```

2. Search `docs/` only as non-authoritative context unless explicitly elevated.
3. If live source/package search supports the current route contract and `docs/` disagrees, treat the docs match as stale and update tests/docs accordingly.
4. Record the source/package search result in `todo.md` or the review bundle so final reviewers can verify the authority decision.

## Review-bundle wording

Add a short reviewer instruction such as:

> Important: Buffdemy backend `docs/` files are non-authoritative stale/transient context unless the user explicitly elevated one for this task. Review source/package/test contracts in `apps/` and `packages/` first; do not fail the plan solely because a `docs/` file names an older API contract.
