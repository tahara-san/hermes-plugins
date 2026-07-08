# Identifier Field → Autosuggest/Multi-Select Plan-Doc Pitfalls

Use this reference when a plan-doc replaces a raw ID/text field with a rich autosuggest or multi-select UI.

## Required gates before implementation

1. **New suggestion path**: define how new options are searched (query params, filtering, auth, rate limits, public-only payload shape).
2. **Existing-value hydration path**: define how already-stored IDs hydrate back into displayable selected items. Suggestion search is not enough for this.
3. **Legacy preservation**: if the old raw field accepted broader values than the new suggestions allow, existing saved values may be outside the new suggestion filter. Preserve them unless the user removes them.
4. **Unresolved fallback**: specify how to render and preserve stored IDs that cannot be resolved to public identity (`Unknown user (<id>)`, ID-only chip, or equivalent).
5. **Max-count migration**: if the new widget adds a max count where the old raw field had none, do not truncate existing over-limit saved values. Render all existing values, block new additions until under the max, or record an explicit product decision to migrate/drop.
6. **Payload boundary**: explicitly state whether selected objects save as IDs, names, slugs, or rich objects; verify no display label becomes the persisted identifier.
7. **Switching modes**: if the containing UI can switch away from the selector, test both UI preservation and save-payload omission for other modes.

## Backend/API contract checklist

- Search endpoint filters new suggestions according to product rules.
- Batch identity endpoint resolves stored IDs without applying the new-suggestion filter unless the product explicitly wants destructive migration.
- Response contains public identity only; no private fields such as email or auth IDs.
- Query params are allowlisted; limit is clamped; minimum query length and unsupported-param behavior are documented.
- Missing/deleted/private IDs have documented behavior and frontend fallback semantics.

## UI/test checklist

- Existing saved values hydrate into chips/items.
- Unresolved existing IDs render fallback chips and survive re-save unless removed.
- Existing over-max selections are not truncated.
- New suggestions are filtered correctly and duplicates are prevented.
- IME composition does not show stale suggestions.
- Stale async results cannot overwrite newer query results.
- Keyboard/ARIA basics are covered for custom combobox/listbox behavior.
- Payload tests prove non-selector modes do not leak preserved selected IDs.
