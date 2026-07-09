# Planner Stop Hook Out-of-Scope Logging — TODO

## Phase 1: Refactor reminder module for testable helpers
- [x] Preserve existing `pre_llm_call` reminder injection.
- [x] Add `contains_issue_like_language(text: str) -> bool` using Claude’s focused trigger set: `pre-existing`, `out-of-scope`, `follow-up`, `no-op`, `skipped`, `code smell`.
- [x] Add helper(s) to detect `tasks/out-of-scope-issues/` paths in write-like Hermes tool calls.
- [x] Add per-turn state keyed by `session_id`/`turn_id` when available.

## Phase 2: Track issue-file touches
- [x] Track `write_file.path` touches under `tasks/out-of-scope-issues/`.
- [x] Track `patch.path` and V4A patch target touches under `tasks/out-of-scope-issues/`.
- [x] Track obvious terminal command references to `tasks/out-of-scope-issues/`.
- [x] Ensure tracking coexists with the existing env-blocker `pre_tool_call` hook.
- [x] Reset state on new turns and clean up on session end if needed.

## Phase 3: Add active Stop-hook-equivalent enforcement
- [x] Add `pre_verify` hook that returns a continue directive when a coding final response mentions issue-like language but no issue file was touched this turn.
- [x] Self-throttle `pre_verify` with `attempt > 0` to avoid loops.
- [x] Add `transform_llm_output` fallback for non-coding turns where issue-like language appears without an issue-file touch.
- [x] Keep the Dependabot exception in reminder/enforcement wording.

## Phase 4: Register hooks and update docs
- [x] Update `plugins/hermes-planning-guards/hermes_planning_guards/plugin.py` hook registration.
- [x] Update `plugins/hermes-planning-guards/tests/test_plugin_registration.py` expected hooks.
- [x] Update `plugins/hermes-planning-guards/README.md` to describe Stop-hook-equivalent behavior.
- [x] Update `plugins/hermes-planning-guards/plugin.yaml` hook list/description if needed.

## Phase 5: Tests and validation
- [x] Add tests for issue-like keyword detection.
- [x] Add tests for touched-path detection across `write_file`, `patch`, V4A patch, and terminal command text.
- [x] Add tests for `pre_verify` continue vs allow cases.
- [x] Add tests for `transform_llm_output` fallback vs unchanged cases.
- [x] Run `python3 scripts/validate_skills.py`.
- [x] Run `uv run --with pytest --with pyyaml pytest -q plugins/hermes-planning-guards/tests tests/test_repo_layout.py tests/test_skill_frontmatter.py`.
- [x] Run `uv run --with pytest --with pyyaml pytest -q`.

## Completion checklist
- [x] Scope is limited to planner Stop hook/out-of-scope issue logging enforcement.
- [x] No `codex-chunk` skill work is included.
- [x] No env-blocker behavior changes are included.
- [x] `hermes-planning-guards` actively nudges or flags unlogged out-of-scope issue mentions.
- [x] Focused and full repo tests pass with real output.


## Plan-code workflow gates
- [x] Simplify gate run after implementation; narrow simplification added explicit "no issue to log" handling and tighter trigger boundaries.
- [x] Verification commands completed with real output.
- [x] Mandatory Codex-style independent review passed against `tasks/claude-plugin-parity-update/reviews/final-implementation-review-bundle-v5.md`; final artifact: `tasks/claude-plugin-parity-update/reviews/codex-style-review-v5.json`.
- [x] Mandatory Claude Code Opus 4.8 @ xhigh interactive review passed against the same v5 implementation bundle; final artifact: `tasks/claude-plugin-parity-update/reviews/claude-opus48-xhigh-review-v5.json`.
- [x] Aggregate final review verdict passed; stale failed/superseded review artifacts retained for audit history.
- [x] Final report ready after review verdicts were saved.
