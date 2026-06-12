# Mid-task contract changes

When the user changes requirements during execution:

1. Stop and restate the new contract.
2. Identify stale assumptions in specs/TODOs/tests.
3. Patch task docs before continuing.
4. Remove obsolete compatibility paths unless explicitly required.
5. Rerun impacted verification.
6. Rerun any mandatory review gate on the final updated bundle.

Do not implement stale TODOs just because they are checked into the plan.
