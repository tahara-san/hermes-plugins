# Bun mock.module suite-order leakage

Bun `mock.module(...)` mocks can leak across test files in the same process. A file that mocks a shared config/module with a partial object can poison later imports that expect additional fields, producing failures only in the full suite while focused file tests pass.

## Diagnostic pattern

- Focused test passes, full suite fails.
- Failure looks like a valid runtime value became `undefined` only after another test file ran.
- Search for `mock.module` of the same module path, including aliases and relative paths.
- Inspect partial config mocks first.

## Preferred fixes

1. Prefer narrower dependency injection or local spies when feasible.
2. If the module mock is still the right seam, make the fake module complete enough for every downstream import in the process, not just the file that installed it.
3. Verify the exact combined/full-suite command that exposed the leak, not only the focused file.

## Avoid

- Weakening production code to tolerate test-only partial mocks.
- Adding arbitrary inert exports without understanding which later import needs the value.
- Treating the focused pass as enough when the full-suite order was the failing condition.
