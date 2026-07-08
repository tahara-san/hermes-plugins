# E2E fixture prerequisite gating for plan-code work

Use this when an implementation plan asks for E2E coverage that depends on a fixture identity, account state, external billing/subscription state, or another prerequisite that is not already present and explicitly approved.

## Durable pattern

1. Treat fixture identity/state as a prerequisite, not as something to invent opportunistically.
2. Search existing docs/code/fixtures before declaring a blocker or adding a new fixture dependency.
3. If the required fixture is absent and user approval is needed, do not add a new E2E user or mutate fixture roles silently.
4. Split coverage:
   - keep runnable E2E coverage for paths that existing fixtures can prove;
   - gate prerequisite-dependent specs behind an explicit env var or documented skip;
   - document that the gated specs are not final proof until the prerequisite is satisfied.
5. In final verification, do not cite a gated/skipped E2E path as proof of the protected functionality.
6. If the user later provides the missing approved fixture identity before commit/push, treat it as new task-relevant context, not a future note: update the test constants, auth/bootstrap helpers, fixture schemas, and prerequisite-dependent specs to use that identity, then rerun targeted verification before committing. Keep any broader env gate that still represents a real external readiness condition (for example, backend deterministic fixture availability), but make the gated path use the approved role when enabled.
7. For frontend proxy/API boundary work, distinguish:
   - frontend UX/request-shape/session validation;
   - backend authoritative permission enforcement;
   - cosmetic/business-sanity validation.
   Add concise ADR-style comments where intentional no-validation/proxy-only paths could look like omissions.

## Example

For subscription-tier management that requires a `paidContentCreator` E2E identity, existing `creator` and `user` fixtures can cover creator/user UI gates and consumer subscription flows. Management-dashboard mutation E2E should remain skipped/gated (for example with `PAID_CONTENT_CREATOR_E2E_READY`) until an explicitly approved paidContentCreator identity exists. Do not assume or create another user, and do not use subscription/billing consumer E2E as final proof for paidContentCreator management.

When an approved paidContentCreator identity is provided, wire it through every layer the E2E path touches instead of only changing the spec body:
- test constants and any saved-storage/auth setup typing;
- test-only session/bootstrap route allowlists and role/email assignment;
- frontend fixture proxy request schemas/helper union types;
- specs that need the role, preferably via a helper such as `withPaidContentCreatorPage`;
- route/unit tests proving the new identity maps to `paidContentCreator`.

For buffdemy2-web specifically, `test03@test.com` / `testuser3` is the approved `paidContentCreator` E2E identity. Use it for paidContentCreator-required coverage instead of adding another account or silently promoting `testuser1`.
