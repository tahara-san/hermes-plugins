# Barrel import cycles and lazy public exports

## Trigger

Use this when a TypeScript/ESM package has a public barrel that re-exports both low-level runtime utilities and higher-level helpers, and a runtime startup fails with a TDZ-style error such as:

```text
ReferenceError: Cannot access '<BaseClass>' before initialization
```

A common shape is:

```text
BaseRepository -> client/index barrel -> index-management helper -> repositories -> BaseRepository
```

The package may still typecheck, because the failure is caused by eager ESM module evaluation order rather than TypeScript types.

## Durable fix pattern

1. Identify the lowest-level module that should be safe to import broadly, for example `@pkg/mongo/client`.
2. Check whether that module eagerly re-exports helpers that import higher-level modules from the same package.
3. Keep the public API stable when callers already import the helper from the low-level barrel, but make the high-level helper lazy:

```ts
export async function createAllIndexes(): Promise<void> {
  const module = await import('./createAllIndexes.js');
  return module.createAllIndexes();
}

export async function verifyRequiredIndexes(targetDb: Db): Promise<void> {
  const module = await import('./verifyRequiredIndexes.js');
  return module.verifyRequiredIndexes(targetDb);
}
```

4. Do not broaden repository imports to a larger barrel as a simplification. Keep low-level repository modules importing only the lightweight client primitives they need.
5. Verify both compile-time and runtime startup. A package build passing is not enough for this class of bug.

## Verification checklist

- Package build passes.
- App/service that previously crashed starts successfully.
- Startup logs reach the expected readiness point, not just container `Up` status.
- If index creation/verification was involved, logs show the lazy-loaded helper executed when invoked.
