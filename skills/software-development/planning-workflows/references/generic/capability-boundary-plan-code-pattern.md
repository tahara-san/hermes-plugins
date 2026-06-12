# Capability-boundary plan-code pattern

For auth, API, cache, or capability-boundary changes, plans should prove:

- who can read;
- who can write;
- who is denied;
- denied paths have no side effects;
- public response serialization does not leak private fields;
- compatibility endpoints preserve intended auth behavior.

Plan tests for positive, negative, and actor-transition cases.
