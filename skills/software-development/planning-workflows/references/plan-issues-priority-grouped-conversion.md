# Plan-issues priority-grouped conversion

Use this conditional reference when the user invokes `/plan-issues <priority>` or asks to convert one or more `tasks/out-of-scope-issues/<priority>/` buckets.

The canonical contract is `plan-issues/plan-issues.md`; this file only narrows priority-grouped discovery and grouping. It cannot relax the one-task review lifecycle, dependency graph checks, reviewer pins, evidence bounds, or out-of-scope guard.

## Priority-grouped procedure

1. Treat the request as docs-only conversion. Do not implement fixes.
2. Load `planning-workflows`, the canonical `plan-issues` reference, and `plan-doc`.
3. Read every matching issue file, including nested `manual/` entries. Valid priorities are `critical`, `high`, `medium`, `low`, `proposal`, and `other`.
4. Apply the user's filter exactly. Deduplicate normalized kebabs before grouping. Skip Dependabot-only alert/security-count records; GitHub remains their source of truth.
5. Before writing, inspect existing tasks and dirty state so the conversion neither duplicates in-flight work nor absorbs unrelated files.
6. Group by class, ownership, surface, and implementation boundary. Keep medium-or-higher, architectural, multi-subsystem, and non-trivial items separate by default. Ask one early decision when materially different groupings are reasonable.
7. Build the complete dependency graph and detect every cycle before directories are created. Use stable `tasks/<task-name>/` paths. Derive longest-prerequisite-path `implementation_order` waves and safe parallel cohorts in metadata/status only. Independent safe-parallel tasks may share a wave; graph correction requires no directory renaming.
8. Initialize the conversion through `planning-workflows/scripts/plan_issues_workflow.py`. This creates task metadata, the compact status ledger, and a fresh-session handoff per task. The ledger identifies exactly one current task and records direct prerequisites plus parallel cohort.
9. Invoke `plan-doc` per group to create `spec.md` and `todo.md`. Include exact source links, current evidence, goal/scope, acceptance criteria, decisions, phases, verification, dependency gates, out-of-scope rules, kickoff, and final report.
10. Preserve original issue files unless exact cleanup was explicitly requested. Maintain a coverage map proving each source maps to at most one generated plan; explain examined-but-unconverted sources.

## One-task review lifecycle

Creating/mapping all task docs does not authorize a global review campaign.

1. Select the current task from `tasks/plan-issues-status.md`.
2. Put exact repository-relative paths claimed by `spec.md`/`todo.md` in inline code, then enumerate all of them in the reasoned manifest with the real non-symlinked authoritative docs. Fail before dispatch for missing or omitted plan-named paths, directories, current-task review artifacts, duplicate paths, or a full neighboring plan.
3. Generate a bundle for exactly one target slug. There is no generate-all default; versions are discovered only from that task's `reviews/` directory.
4. Within the current task, launch every required independent review lane before waiting: Codex interactive TUI GPT-5.6 SOL/xhigh in managed `tmux`, and interactive Claude Code Fable 5/xhigh through `claude-i`, both against the same digest.
5. Save both complete hash-bound results before editing when practical. Each task-local raw transcript must contain exactly one canonical result block attesting reviewer mode/model/effort/digest/verdict. The helper rehashes the bundle and raw artifacts before aggregation. Consolidate blocker findings into one amendment pass; the default permits four total review rounds: the initial round plus at most three normal rerounds, and only after authoritative docs actually change. A reround is current-only: include latest authoritative evidence plus a concise finding-to-fix delta and historical paths/digests, while prior full bundles and prior raw review artifacts remain unbundled history. There is no separate artifact-consistency review; the helper validates the full approval chain in the same gate. Non-blocking suggestions remain implementation-review attention points and do not force document churn.
6. Aggregate the matching digest. Archive a delayed old-digest result once as superseded; it cannot change current state or trigger a rerun by itself.
7. If the fourth round does not pass, stop and ask the user to decide how to proceed. Do not start another review round without an explicit user decision.
8. Do not generate or dispatch the next task until the current task is approved, explicitly waived, or durably blocked and the user authorizes moving on.

Implementation-order metadata controls later implementation dependencies, not task paths or review rounds. Stable task paths do not change when graph metadata changes. Even tasks in one parallel implementation cohort are reviewed one task at a time so each has an independent manifest, version sequence, reviewer state, and aggregate.

## Dependency and correction discipline

- Do not embed another task's mutable `spec.md` or `todo.md`.
- Freeze compact size-bounded required excerpts only after the prerequisite has a current approved bundle/immutable aggregate identity, record a material excerpt digest, and include that contract explicitly in the dependent manifest. Unrelated prerequisite prose does not mutate the frozen contract; changing its excerpts stales the dependent approval.
- Keep a user-authorized durable block as an explicit downstream gate; any other unapproved prerequisite stops bundling.
- If dependency discovery changes order or cohort metadata, run the helper's metadata-only migration. It updates metadata, status, and handoffs atomically, performs no directory renaming or path-reference rewrite, and invalidates affected active/approved review identity while preserving historical artifacts.
- Adopt existing stable legacy task directories only through `adopt-legacy` with a reviewed explicit definitions mapping; preserve each existing `reviews/` tree as historical evidence.

## Out-of-scope guard

During conversion, deduplicate and log every non-exempt new finding at `tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md`, or the priority's `manual/` subdirectory for human intervention. Use **Issue**, **Location**, **Severity**, **Context**, and **Suggested Fix** in order. Do not create/update an issue solely for Dependabot alerts or advisory counts. Mention every created/updated issue in the wrap-up.

## Final report additions

Alongside the canonical final report, include:

- per-priority counts and filter result;
- manual/skipped/already-covered inputs;
- group-to-source coverage;
- graph waves, prerequisites, parallel cohorts, and cycle-check result;
- the status ledger and each handoff path;
- the current task and why later tasks were not dispatched;
- each generated task's local bundle/hash and both lane states;
- exact cleanup, or that no source was removed.

## Pitfalls

- Planning manual-tier files automatically.
- Treating low priority as permission to over-group unrelated work.
- Launching all generated-task reviewers before closing the current task.
- Reusing a global campaign version.
- Treating `git diff --check` or a coverage map as a substitute for plan-doc review.
- Removing all files in a priority bucket rather than exact mapped sources.
- Preserving stale issue claims as task truth when current evidence disproves them.
