# Planner Stop Hook Out-of-Scope Logging Plan

## Goal

Implement only the Hermes equivalent of the Claude planner Stop hook for out-of-scope issue logging.

The target behavior is from `/home/tahara/dev/claude-plugins/plugins/planner/hooks/check-out-of-scope-issues.sh`: when the assistant is about to finish after mentioning issue-like language such as `pre-existing`, `out-of-scope`, `follow-up`, `skipped`, or `code smell`, the workflow should prevent silently ending unless the finding was logged under `tasks/out-of-scope-issues/` or the assistant explicitly determines there is no out-of-scope issue to log.

## Scope

### In Scope

1. Strengthen `hermes-planning-guards` so out-of-scope issue tracking has active enforcement, not only passive reminder text.
2. Keep the existing `pre_llm_call` reminder context.
3. Add Hermes-native Stop-hook-equivalent behavior using supported Hermes plugin hooks:
   - track whether the current turn touched `tasks/out-of-scope-issues/`;
   - detect issue-like language in the final response;
   - nudge the agent before final delivery when a coding turn mentions issue-like language without logging an issue file;
   - provide a non-coding fallback that makes the missing log visible instead of silently delivering a clean-looking final response.
4. Add focused unit tests for the guard behavior and hook registration.
5. Update only the planning-guards plugin documentation/manifest if needed.
6. Run focused plugin tests and repo validation.

### Out of Scope

- Adding a standalone Hermes `codex-chunk` skill.
- Changing env-blocker behavior or `.env*` allow/block semantics.
- Reworking `plan-doc`, `plan-code`, `plan-clean`, `plan-issues`, `plan-commit`, `simplify`, or `claude-i` workflows.
- Updating bundle/manifests except if a plugin metadata description needs to mention the strengthened Stop-hook-equivalent guard.
- Implementing an exact Claude transcript parser; Hermes should use its native hook payloads instead.

## Current Evidence

### Claude behavior

`../claude-plugins/plugins/planner/hooks/check-out-of-scope-issues.sh`:

- Runs as a Claude Code `Stop` hook.
- Reads the Claude transcript and scans the last assistant turn.
- Trigger keywords include:
  - `pre-existing`
  - `out-of-scope`
  - `follow-up`
  - `no-op`
  - `skipped`
  - `code smell`
- Allows the turn to stop if a `Write`/`Edit` tool-use path in that turn touched `tasks/out-of-scope-issues/`.
- Otherwise blocks Stop with a reminder to log each finding under:
  - `tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md`
  - or `tasks/out-of-scope-issues/<priority>/manual/<YYYYMMDD>_<short-kebab>.md` for human/manual investigation.

### Current Hermes behavior

`hermes-planning-guards` currently:

- Registers `pre_tool_call` for `.env*` protection.
- Registers `pre_llm_call` to inject an out-of-scope issue tracking reminder.
- Does not currently register a hook that can keep a turn going when the assistant tries to finish without logging an issue.

Hermes runtime support checked from local docs/source:

- `pre_verify` can return `{"action": "continue", "message": "..."}` to keep a coding turn going before final delivery.
- `transform_llm_output` can replace final response text before delivery.
- `pre_tool_call` can inspect tool name/args before a write-like call.
- `post_tool_call` can observe completed tools and their args/results, but its return value is ignored.
- `on_session_end` can clean session/turn state after a turn.

## Design

### Hook strategy

1. **Keep `pre_llm_call`:** continue injecting the out-of-scope logging policy reminder.
2. **Add per-turn touched-path tracking:** record when the model attempts or completes a write-like operation involving `tasks/out-of-scope-issues/`.
3. **Add `pre_verify` enforcement for coding turns:** if the final response contains issue-like keywords and no issue file was touched this turn, return a continue directive instructing the agent to log the issue or explicitly state why no out-of-scope issue is present.
4. **Add `transform_llm_output` fallback for non-coding turns:** if issue-like language appears without a touched issue path, append or replace with a visible guard reminder. This is weaker than `pre_verify`, but it avoids silent clean delivery on turns where `pre_verify` does not fire.
5. **Reset state per turn/session:** ensure one turn’s issue-file write does not exempt later turns.

### State model

Use small in-process state keyed by `session_id` and `turn_id` when available:

- `touched_issue_path: bool`
- optional `touched_paths: set[str]` for debugging/tests

Reset on `pre_llm_call` for the current turn and clean up on `on_session_end`.

### Issue-like keyword detection

Preserve Claude’s focused trigger set to avoid noisy false positives:

```text
pre-existing
out-of-scope
follow-up
no-op
skipped
code smell
```

Use case-insensitive matching. Keep the trigger set narrow initially; broaden only with tests and real examples.

### Touched-path detection

Treat a turn as having logged/updated an issue if any of these clearly target `tasks/out-of-scope-issues/`:

- `write_file.path`
- `patch.path`
- V4A patch headers: `*** Update File:`, `*** Add File:`, `*** Delete File:`
- terminal command text containing `tasks/out-of-scope-issues/` in an obvious path reference

Do not attempt to parse arbitrary shell indirection perfectly. This guard is workflow enforcement, not a sandbox.

### Enforcement message

The `pre_verify` continue message should be concise and actionable:

- say the final response mentioned potential out-of-scope/pre-existing/follow-up/skipped/code-smell items;
- say no `tasks/out-of-scope-issues/` file was touched this turn;
- instruct the agent to either:
  - create/update the required issue file with sections `Issue`, `Location`, `Severity`, `Context`, `Suggested Fix`; or
  - if every mention is not actually an out-of-scope issue, revise the final response to say that explicitly.

### Dependabot exception

Keep the existing reminder’s Dependabot exception: do not force issue-file logging solely for GitHub Dependabot alert/security advisory counts unless the user explicitly asks to triage/fix them.

## Files to Update

- `plugins/hermes-planning-guards/hermes_planning_guards/out_of_scope_reminder.py`
- `plugins/hermes-planning-guards/hermes_planning_guards/plugin.py`
- `plugins/hermes-planning-guards/tests/test_out_of_scope_reminder.py`
- `plugins/hermes-planning-guards/tests/test_plugin_registration.py`
- `plugins/hermes-planning-guards/README.md`
- `plugins/hermes-planning-guards/plugin.yaml` if the hook list/description should be updated

## Implementation Steps

### Phase 1 — Refactor reminder module for testable helpers

- Extract `contains_issue_like_language(text: str) -> bool`.
- Extract `extract_issue_paths_from_tool_call(tool_name: str, args: dict) -> set[str]` or equivalent boolean helper.
- Add state helpers keyed by session/turn.
- Preserve `pre_llm_call(**kwargs) -> {"context": REMINDER}`.

### Phase 2 — Track issue-file touches

- Add a tracking hook callback, preferably via `post_tool_call` so successful completed write-like tools are recorded.
- If needed, also use `pre_tool_call` for command/path intent, but avoid interfering with env-blocker’s existing `pre_tool_call` function.
- Make sure this tracking coexists with `block_env_files.pre_tool_call` in `plugin.py`.

### Phase 3 — Add active enforcement

- Add `pre_verify(**kwargs)`:
  - return `None` when `attempt > 0`;
  - return `None` when `coding` is false or no final response is present;
  - return `None` when no issue-like language is present;
  - return `None` when an issue path was touched in this turn;
  - otherwise return `{"action": "continue", "message": <guard message>}`.
- Add `transform_llm_output(**kwargs)` fallback for non-coding turns:
  - leave output unchanged when no issue-like language or issue path was touched;
  - append a short guard note when issue-like language appears without a logged issue.

### Phase 4 — Register hooks and document behavior

- Update `plugin.py` to register:
  - existing env `pre_tool_call` blocker;
  - out-of-scope `pre_llm_call` reminder;
  - out-of-scope path tracker hook(s);
  - out-of-scope `pre_verify` enforcement;
  - out-of-scope `transform_llm_output` fallback;
  - cleanup hook if used.
- Update tests to assert the registration list.
- Update README/plugin metadata to describe the Stop-hook-equivalent behavior.

### Phase 5 — Verify

Run from `/home/tahara/dev/hermes-plugins`:

```bash
python3 scripts/validate_skills.py
uv run --with pytest --with pyyaml pytest -q plugins/hermes-planning-guards/tests tests/test_repo_layout.py tests/test_skill_frontmatter.py
uv run --with pytest --with pyyaml pytest -q
```

## Acceptance Criteria

- The plan does not include `codex-chunk`, env-blocker parity changes, or unrelated planning workflow edits.
- `hermes-planning-guards` has an active Hermes-native approximation of the Claude planner Stop hook.
- Coding turns that mention issue-like language without touching `tasks/out-of-scope-issues/` are nudged before final delivery via `pre_verify`.
- Non-coding turns get a visible fallback via `transform_llm_output`.
- Existing `.env*` blocking behavior remains unchanged by this task.
- Focused plugin tests and repo validation pass with real output.
