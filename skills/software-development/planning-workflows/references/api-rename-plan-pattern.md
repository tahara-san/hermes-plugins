# API Rename Plan Pattern

Use this reference when writing a `tasks/<task-name>/` plan for renaming a public API concept while preserving existing behavior.

## Durable pattern

1. Separate public contract naming from internal implementation naming.
   - Example: expose a new canonical API value while keeping older Redis/database/key namespaces unchanged as internal implementation details.
2. Prefer a compatibility alias unless the user explicitly approves a breaking cleanup.
   - Accepted request values can include both the new canonical value and the old alias during migration.
3. Return canonical metadata in successful responses.
   - Even when a legacy alias is accepted on input, response metadata should advertise the new canonical value so clients converge.
4. Keep behavior-preserving rename scope tight.
   - Do not add new ranking, merging, provenance, migration, or feed/source semantics unless explicitly in scope.
5. Document the unsupported-value error contract.
   - `supportedTypes` or equivalent error content should advertise canonical names, with deprecated aliases separated if useful.
6. Update docs and tests before or alongside code.
   - Include default behavior, canonical explicit request, legacy alias request, response metadata, and unsupported-value tests.
7. Preserve review-gate overrides from the user.
   - If the user says to skip a normally expected review step but keep another, record that in the plan's review gates and final-report checklist.

## Task-doc sections worth including

- Goal and target public contract.
- In-scope vs out-of-scope behavior changes.
- Current source-grounded context with exact files and current constants/metadata.
- Target API contract: accepted requests, response metadata, unsupported-value behavior.
- Technical approach with a normalization boundary between public values and internal implementation.
- Expected file changes.
- Acceptance criteria.
- Verification commands.
- Review gates and explicit skipped gates.
- Risks and mitigations.

## Execution checklist for compatibility-safe enum/feed renames

Use this as a concrete TDD sequence when executing an API rename plan, not only when writing it:

1. Add focused route/API tests first for the new default, explicit canonical value, legacy alias value, canonical response metadata, and unsupported-value error shape. Confirm they fail against the old implementation before production edits.
2. Implement the smallest route-boundary normalization function that maps omitted/canonical/legacy input to the canonical public value and rejects anything else.
3. Keep old internal readers, stores, queues, Redis keys, or DB enum names untouched when the task is explicitly public-contract-only. Add a short inline comment if old internal naming (for example `feed:main:*`) remains intentionally visible in implementation code.
4. Build response metadata from the normalized public value, not from the internal storage key or legacy reader name.
5. Update public docs/examples/types/cache-key guidance so clients converge on the canonical value, while documenting legacy aliases only as compatibility input.
6. Run the focused test command and the narrow package/app build requested by the plan. Avoid root builds or generated file edits when project guidance prohibits them.
7. In the final scope check, prove no forbidden internal migration or adjacent feature slipped in (for example no new storage namespace, no tag/combined/ranking/provenance changes) and name any intentionally unchanged internal package.
