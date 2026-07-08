# Buffdemy2-web E2E plan-doc completion refresh

Use this when refreshing an existing Buffdemy2-web task plan after an implementation/focused-verification pass has already landed, but the task still has unchecked Playwright/E2E matrix rows or final closure gates.

## Pattern

1. **Do not treat focused green specs as matrix completion.** Read the current task TODO/progress docs and map every unchecked E2E row to an actual assertion. A spec file name, a registry entry, or a run with skipped tests is not enough.
2. **Path-scope Playwright registry checks.** Prefer:
   ```bash
   TEST_E2E_AUTH_HARDENING=1 PAID_CONTENT_CREATOR_E2E_READY=1 E2E_BASE_URL=http://host.docker.internal:3000 npx playwright test --list src/tests/e2e/auth/questionEcoCycle.spec.ts src/tests/e2e/auth-user2/questionAcl.spec.ts src/tests/e2e/auth-user3/questionAnswerer.spec.ts
   ```
   Avoid broad greps such as `question|answer|follow` when they also match unrelated feed/follow specs; if used, mark them as supplemental only.
3. **Separate fixture role from ACL path.** If a user fixture has role `user` but is explicitly named in an ACL and the backend returns `privileges.answer.create === true`, label that as explicit named-user ACL coverage only. Do not count it as creator/paidContentCreator role-gated coverage. Use the paidContentCreator fixture (currently test03 in Buffdemy2-web) for paid/role-gated answerer assertions, or stop and document the backend/spec divergence.
4. **Use approved blockers, not self-certified blockers.** For rows that cannot be reached with current backend/test data, require an exact documented and approved backend/test-data blocker before checking the row. Include endpoint, payload, status/body, and why a gated fixture action is not sufficient.
5. **Plan fixture gaps explicitly.** Private non-participant, partial rejection, answered/post-answer-cancel, and expired states may need net-new gated deterministic fixture scenarios/actions. Prefer real UI/API flow first; add test-only helpers only when backend-owned state cannot be reached stably in one E2E.
6. **Require a skip ledger at closure.** If focused Playwright runs report any skipped tests, the final report must enumerate which tests skipped and why, so no matrix row is silently satisfied by a skip.

## Plan-doc review artifact discipline

- If reviewer feedback changes task docs, save the initial raw review artifacts as superseded, patch the docs, regenerate the bundle, and rerun both review legs.
- Final bundles should state their scope and whether prior review artifacts/final aggregate artifacts are excluded to avoid self-referential stale-review loops.
- A bundle generated before writing the final bundle/review artifacts may have a stale `git status` by definition. This is acceptable only if the bundle says review artifacts are excluded; the final user report still needs a fresh `git status --short` so changed/untracked task artifacts are reported accurately.
- Keep one aggregate verdict that names the final bundle, both final reviewer artifacts, observed Claude Code model/effort, static-scan status, verification status, superseded artifacts, and whether post-review edits happened.
