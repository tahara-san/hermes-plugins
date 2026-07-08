# Buffdemy frontend ACL gating notes

Use these notes when executing Buffdemy frontend plans that add or adjust article/comment permission gates.

## Durable workflow lessons

- Treat API source schemas as part of the contract, not just UI model schemas. When adding new ACL/privilege fields to article models, update and test the corresponding source/schema validation used by every touched fetch path (for example Article API source props before serialization/model conversion).
- Cover both top-level and deep-link/permalink flows. Comment/reply gating can regress in permalink-focused code paths even when the regular article page works.
- Test denied-create/readable-comment states separately from denied-read states. A user may be allowed to read existing comments/replies while not allowed to create new top-level comments or replies.
- Verify localized error handling end-to-end when backend AppError codes are introduced: helper mapping, toast behavior, and EN/JA key parity.
- Browser/jsdom-facing tests should preserve direct narrow imports where possible; avoid simplifying to broad barrels if that pulls server/Node-only modules into client test bundles.

## Suggested targeted verification shape

- Schema/model contract test for the new ACL/privilege fields.
- Composer gating test for top-level comment creation.
- Reply/thread gating test where read is allowed but create is denied.
- Permalink child-reply test for `canCreateReply === false`.
- Error-code-to-i18n-key helper test plus translation parity check.
