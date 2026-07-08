# Buffdemy next-intl placeholder regression pattern

Use this when a Buffdemy frontend task touches `src/i18n/translations/**` strings with interpolation.

## Durable lesson

`next-intl` messages use ICU placeholder syntax:

- Correct: `{name}`, `{action}`
- Incorrect: `{{name}}`, `{{action}}`

Double-brace placeholders can compile into JSON successfully but fail at render time with `INVALID_MESSAGE: MALFORMED_ARGUMENT` when `createTranslator`, `useTranslations`, or server `getTranslations` formats the message.

## Recommended fix pattern

1. Add/keep a deterministic test that uses real translation JSON and `createTranslator` instead of mocked `useTranslations`.
2. Exercise each affected key with representative values in both `en` and `ja`.
3. Extend `scripts/check-translation-parity.mjs` or the equivalent i18n check to reject double-brace interpolation in all translation string values, including strings nested under arrays/objects.
4. Convert `{{placeholder}}` to ICU `{placeholder}` in every locale for the same key.
5. Verify with:
   - focused real-message Vitest test
   - `npm run check:i18n`
   - `npm run lint`
   - nearby component tests when related UI behavior is touched

## Guard regex

If the goal is to ban all double-brace interpolation in translations, prefer a broad detector such as:

```js
/\{\{[^{}]+\}\}/
```

This catches `{{name}}`, `{{ name }}`, and broader Handlebars-like expressions such as `{{count, number}}`.
