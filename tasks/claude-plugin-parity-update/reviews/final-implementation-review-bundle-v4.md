# Final Implementation Review Bundle v4 — claude-plugin-parity-update

Generated: 2026-07-09T12:12:17.120582+00:00
Repository: /home/tahara/dev/hermes-plugins
Task: tasks/claude-plugin-parity-update
Supersedes earlier final implementation review bundles v1-v3.

## Review contract

This is the final v4 plan-code implementation review bundle after:

1. Fixing Codex round-1 blocker `codex-final-review-round1-failed.json`:
   - `post_tool_call` accepts `result` and fail-closes on failed/absent/no-clear-success result evidence.
   - Added regressions for error JSON results, nonzero terminal exit result, failed status, empty/malformed results, and success JSON result without status.
2. Fixing Claude v2 robustness note:
   - repeated `pre_llm_call` for the same non-empty `(session_id, turn_id)` preserves existing issue-touch state;
   - added a same-turn regression covering transform fallback suppression after a successful logged touch and repeated `pre_llm_call`.
3. Fixing Claude v3 absent-turn-id note:
   - if `turn_id` is absent, `pre_llm_call` resets state rather than carrying issue-touch state across same-session turns;
   - added a regression confirming absent-`turn_id` repeated `pre_llm_call` fails safe by nudging instead of silently exempting.

Review the implementation for correctness, security, data integrity, test coverage, and consistency with `tasks/claude-plugin-parity-update/spec.md`.

Scope remains limited to the Hermes planner Stop-hook-equivalent out-of-scope issue logging enforcement in `hermes-planning-guards`:

- Active issue-like final response enforcement via `pre_verify`.
- Visible final-output fallback via `transform_llm_output`.
- Per-turn issue-file touch tracking via `post_tool_call`.
- Existing `.env*` blocking behavior must remain unchanged.
- No `codex-chunk`, env-blocker parity, or unrelated planning workflow changes.

## Verification summary

- `git diff --check`: passed.
- `python3 -m py_compile ...`: passed.
- `python3 scripts/validate_skills.py`: passed.
- `uv run --with pytest --with pyyaml pytest -q plugins/hermes-planning-guards/tests`: passed.
- `uv run --with pytest --with pyyaml pytest -q plugins/hermes-planning-guards/tests tests/test_repo_layout.py tests/test_skill_frontmatter.py`: passed.
- `uv run --with pytest --with pyyaml pytest -q`: passed.
- Static diff scans: no findings.

## git status --short --branch

Exit code: 0

```text
## main...origin/main
 M plugins/hermes-planning-guards/README.md
 M plugins/hermes-planning-guards/hermes_planning_guards/out_of_scope_reminder.py
 M plugins/hermes-planning-guards/hermes_planning_guards/plugin.py
 M plugins/hermes-planning-guards/plugin.yaml
 M plugins/hermes-planning-guards/tests/test_out_of_scope_reminder.py
 M plugins/hermes-planning-guards/tests/test_plugin_registration.py
?? tasks/

```

## git diff --stat

Exit code: 0

```text
 plugins/hermes-planning-guards/README.md           |   8 +-
 .../out_of_scope_reminder.py                       | 282 +++++++++++++++++++-
 .../hermes_planning_guards/plugin.py               |  12 +-
 plugins/hermes-planning-guards/plugin.yaml         |   6 +-
 .../tests/test_out_of_scope_reminder.py            | 285 ++++++++++++++++++++-
 .../tests/test_plugin_registration.py              |   9 +-
 6 files changed, 593 insertions(+), 9 deletions(-)

```

## git diff --check

Exit code: 0

```text

```

## python3 -m py_compile plugin modules

Exit code: 0

```text

```

## python3 scripts/validate_skills.py

Exit code: 0

```text
Skill validation passed

```

## uv run --with pytest --with pyyaml pytest -q plugins/hermes-planning-guards/tests

Exit code: 0

```text
..................................                                       [100%]
34 passed in 0.04s
warning: `VIRTUAL_ENV=/venvs/hermes` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead

```

## uv run --with pytest --with pyyaml pytest -q plugins/hermes-planning-guards/tests tests/test_repo_layout.py tests/test_skill_frontmatter.py

Exit code: 0

```text
.....................................                                    [100%]
37 passed in 0.06s
warning: `VIRTUAL_ENV=/venvs/hermes` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead

```

## uv run --with pytest --with pyyaml pytest -q

Exit code: 0

```text
.....................................                                    [100%]
37 passed in 0.07s
warning: `VIRTUAL_ENV=/venvs/hermes` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead

```

## Static diff scans

Exit code: 0

```text
--- hardcoded secret scan ---
--- shell injection scan ---
--- dangerous eval/exec scan ---
--- unsafe pickle scan ---

```
## Implementation diff

Exit code: 0

```diff
diff --git a/plugins/hermes-planning-guards/README.md b/plugins/hermes-planning-guards/README.md
index 74a7f69..753f0fa 100644
--- a/plugins/hermes-planning-guards/README.md
+++ b/plugins/hermes-planning-guards/README.md
@@ -6,6 +6,12 @@ Hermes plugin for planning workflow guardrails.

 - `pre_tool_call` — blocks direct tool access to protected `.env*` files while allowing `.env.sample` / `.env.example` and source files such as `.env.ts`.
 - `pre_llm_call` — injects a reminder to log out-of-scope findings under `tasks/out-of-scope-issues/` instead of silently dropping or fixing unrelated issues.
+- `post_tool_call` — tracks successful write-like tool calls that touch `tasks/out-of-scope-issues/` during the current turn.
+- `pre_verify` — approximates the Claude planner Stop hook for coding turns: when a draft final response mentions issue-like language (`pre-existing`, `out-of-scope`, `follow-up`, `no-op`, `skipped`, or `code smell`) without touching an out-of-scope issue file, Hermes keeps the turn going with an instruction to log the issue or explicitly state why no issue exists.
+- `transform_llm_output` — provides a visible fallback note for non-coding or otherwise non-verified turns that mention issue-like language without a logged issue file.
+- `on_session_end` — clears in-memory turn tracking state.
+
+Dependabot alert/advisory counts remain exempt from forced issue-file logging unless the user explicitly asks to triage or fix them.

 ## Why plugin hooks?

@@ -20,4 +26,4 @@ python -m hermes_planning_guards.block_env_files
 python -m hermes_planning_guards.out_of_scope_reminder
 ```

-> Security note: this guard is defense-in-depth, not a sandbox or complete security boundary. It blocks obvious protected `.env*` tool targets and command text, but cannot prevent every shell indirection, glob expansion, or future tool surface.
+> Security note: this guard is defense-in-depth, not a sandbox or complete security boundary. It blocks obvious protected `.env*` tool targets and command text, but cannot prevent every shell indirection, glob expansion, or future tool surface. The out-of-scope tracker likewise recognizes obvious Hermes write/patch/terminal path references; it is workflow enforcement, not a complete shell parser.
diff --git a/plugins/hermes-planning-guards/hermes_planning_guards/out_of_scope_reminder.py b/plugins/hermes-planning-guards/hermes_planning_guards/out_of_scope_reminder.py
index 98603d4..8c520c9 100644
--- a/plugins/hermes-planning-guards/hermes_planning_guards/out_of_scope_reminder.py
+++ b/plugins/hermes-planning-guards/hermes_planning_guards/out_of_scope_reminder.py
@@ -1,9 +1,12 @@
-"""Inject out-of-scope issue tracking guidance before LLM calls."""
+"""Inject and enforce out-of-scope issue tracking guidance."""
 from __future__ import annotations

 import json
+import re
 import sys
-from typing import Any
+import threading
+from dataclasses import dataclass, field
+from typing import Any, Iterable

 REMINDER = """
 Planning guard policy: out-of-scope issue tracking.
@@ -36,12 +39,285 @@ in GitHub; mention them briefly in the wrap-up only when relevant, or work from
 GitHub/gh/npm audit when the user explicitly asks to triage or fix them.
 """.strip()

+ISSUE_PATH_FRAGMENT = "tasks/out-of-scope-issues"
+ISSUE_LIKE_LANGUAGE_RE = re.compile(
+    r"(?i)(?<![A-Za-z0-9_])(?:pre-existing|out-of-scope|follow-up|no-op|skipped|code smell)(?![A-Za-z0-9_])"
+)
+NO_ISSUE_TO_LOG_RE = re.compile(
+    r"(?i)(?:"
+    r"no\s+out-of-scope\s+issues?\s+to\s+log"
+    r"|not\s+(?:an?\s+)?out-of-scope\s+issues?"
+    r"|nothing\s+to\s+log\s+under\s+tasks/out-of-scope-issues"
+    r")"
+)
+V4A_PATCH_TARGET_PREFIXES = (
+    "*** Update File:",
+    "*** Add File:",
+    "*** Delete File:",
+)
+FAILED_TOOL_STATUSES = {"blocked", "error", "timeout", "cancelled", "failed", "failure"}

-def pre_llm_call(**_: Any) -> dict[str, str]:
+PRE_VERIFY_MESSAGE = (
+    "Planning guard: your draft final response mentions potential "
+    "out-of-scope, pre-existing, follow-up, skipped, no-op, or code-smell work, "
+    "but no tasks/out-of-scope-issues/ file was touched this turn. "
+    "Before finishing, either create/update the required issue file with sections "
+    "Issue, Location, Severity, Context, and Suggested Fix, or revise the final "
+    "response to explicitly state why every such mention is not an out-of-scope "
+    "issue to log. Dependabot alert/advisory counts remain exempt unless the user "
+    "asked to triage or fix them."
+)
+
+TRANSFORM_GUARD_NOTE = (
+    "\n\nPlanning guard note: this response mentions potential out-of-scope, "
+    "pre-existing, follow-up, skipped, no-op, or code-smell work, but this turn "
+    "did not touch tasks/out-of-scope-issues/. If that mention is a real "
+    "out-of-scope finding, log it under tasks/out-of-scope-issues/<priority>/ "
+    "with Issue, Location, Severity, Context, and Suggested Fix; Dependabot "
+    "alert/advisory counts are exempt unless explicitly being triaged."
+)
+
+
+@dataclass
+class TurnIssueState:
+    touched_issue_path: bool = False
+    touched_paths: set[str] = field(default_factory=set)
+
+
+_state_lock = threading.Lock()
+_turn_state: dict[tuple[str, str], TurnIssueState] = {}
+_latest_turn_by_session: dict[str, str] = {}
+
+
+def _normalize_path_text(text: str) -> str:
+    return str(text or "").strip().strip(" \t\r\n'\"`()[]{}<>,").replace("\\", "/")
+
+
+def is_issue_path(text: str) -> bool:
+    """Return True when text clearly references tasks/out-of-scope-issues/."""
+    normalized = _normalize_path_text(text)
+    return normalized == ISSUE_PATH_FRAGMENT or f"{ISSUE_PATH_FRAGMENT}/" in normalized
+
+
+def contains_issue_like_language(text: str) -> bool:
+    """Detect Claude planner Stop-hook issue-like trigger language."""
+    return bool(text and ISSUE_LIKE_LANGUAGE_RE.search(text))
+
+
+def explicitly_says_no_issue_to_log(text: str) -> bool:
+    """Return True when the response explicitly says no issue file is needed."""
+    return bool(text and NO_ISSUE_TO_LOG_RE.search(text))
+
+
+def _extract_v4a_patch_targets(patch_text: str) -> set[str]:
+    targets: set[str] = set()
+    for line in str(patch_text or "").splitlines():
+        stripped = line.strip()
+        if stripped.startswith(V4A_PATCH_TARGET_PREFIXES):
+            targets.add(stripped.split(":", 1)[1].strip())
+    return targets
+
+
+def _terminal_issue_path_references(command: str) -> set[str]:
+    references: set[str] = set()
+    for token in re.split(r"\s+", str(command or "")):
+        cleaned = _normalize_path_text(token)
+        if is_issue_path(cleaned):
+            references.add(cleaned)
+    if not references and is_issue_path(str(command or "")):
+        references.add(ISSUE_PATH_FRAGMENT)
+    return references
+
+
+def extract_issue_paths_from_tool_call(tool_name: str, args: Any) -> set[str]:
+    """Extract issue-path touches from write-like Hermes tool calls."""
+    tool_input = args if isinstance(args, dict) else {}
+    paths: set[str] = set()
+
+    if tool_name == "write_file":
+        path = str(tool_input.get("path") or "")
+        if is_issue_path(path):
+            paths.add(path)
+        return paths
+
+    if tool_name == "patch":
+        mode = tool_input.get("mode") or "replace"
+        if mode == "patch":
+            for target in _extract_v4a_patch_targets(str(tool_input.get("patch") or "")):
+                if is_issue_path(target):
+                    paths.add(target)
+        else:
+            path = str(tool_input.get("path") or "")
+            if is_issue_path(path):
+                paths.add(path)
+        return paths
+
+    if tool_name == "terminal":
+        return _terminal_issue_path_references(str(tool_input.get("command") or ""))
+
+    return paths
+
+
+def _state_key(session_id: str = "", turn_id: str = "") -> tuple[str, str]:
+    session = str(session_id or "")
+    turn = str(turn_id or "")
+    if not turn:
+        turn = _latest_turn_by_session.get(session, "")
+    return session, turn
+
+
+def _begin_turn(session_id: str = "", turn_id: str = "") -> None:
+    key = (str(session_id or ""), str(turn_id or ""))
+    with _state_lock:
+        _latest_turn_by_session[key[0]] = key[1]
+        if key[1]:
+            _turn_state.setdefault(key, TurnIssueState())
+        else:
+            _turn_state[key] = TurnIssueState()
+
+
+def _mark_issue_paths(paths: Iterable[str], session_id: str = "", turn_id: str = "") -> None:
+    normalized_paths = {_normalize_path_text(path) for path in paths if is_issue_path(path)}
+    if not normalized_paths:
+        return
+    key = _state_key(session_id, turn_id)
+    with _state_lock:
+        state = _turn_state.setdefault(key, TurnIssueState())
+        state.touched_issue_path = True
+        state.touched_paths.update(normalized_paths)
+        _latest_turn_by_session[key[0]] = key[1]
+
+
+def _issue_path_touched(session_id: str = "", turn_id: str = "", changed_paths: Any = None) -> bool:
+    if any(is_issue_path(str(path)) for path in (changed_paths or [])):
+        return True
+    key = _state_key(session_id, turn_id)
+    with _state_lock:
+        state = _turn_state.get(key)
+        return bool(state and state.touched_issue_path)
+
+
+def _tool_result_indicates_failure(result: Any, status: str = "") -> bool:
+    """Return True when a post_tool_call result/status represents failure.
+
+    Hermes currently supplies a normalized status kwarg, but older/docs-shaped
+    payloads may only provide the tool result string. Fail closed when no status
+    exists and the result lacks clear success evidence.
+    """
+    normalized_status = str(status or "").strip().lower()
+    if normalized_status in FAILED_TOOL_STATUSES:
+        return True
+    if normalized_status and normalized_status not in {"ok", "success", "succeeded", "completed"}:
+        return True
+    if normalized_status in {"ok", "success", "succeeded", "completed"}:
+        return False
+
+    if result is None or result == "":
+        return True
+
+    parsed = result
+    if isinstance(result, str):
+        text = result.strip()
+        if not text:
+            return True
+        if text.lower().startswith("error executing tool"):
+            return True
+        try:
+            parsed = json.loads(text)
+        except Exception:
+            return True
+
+    if isinstance(parsed, dict):
+        if parsed.get("error"):
+            return True
+        if parsed.get("success") is False:
+            return True
+        exit_code = parsed.get("exit_code")
+        if exit_code is not None:
+            try:
+                if int(exit_code) != 0:
+                    return True
+            except (TypeError, ValueError):
+                return True
+        return False
+
+    return True
+
+
+def reset_issue_tracking_state() -> None:
+    """Clear in-memory tracking state; intended for tests and session cleanup."""
+    with _state_lock:
+        _turn_state.clear()
+        _latest_turn_by_session.clear()
+
+
+def pre_llm_call(session_id: str = "", turn_id: str = "", **_: Any) -> dict[str, str]:
     """Hermes plugin hook callback for pre_llm_call."""
+    _begin_turn(session_id=session_id, turn_id=turn_id)
     return {"context": REMINDER}


+def post_tool_call(
+    tool_name: str = "",
+    args: Any = None,
+    result: Any = None,
+    status: str = "",
+    session_id: str = "",
+    turn_id: str = "",
+    **_: Any,
+) -> None:
+    """Track successful issue-file touches from write-like tool calls."""
+    if _tool_result_indicates_failure(result, status=status):
+        return
+    _mark_issue_paths(
+        extract_issue_paths_from_tool_call(tool_name, args),
+        session_id=session_id,
+        turn_id=turn_id,
+    )
+
+
+def pre_verify(
+    coding: bool = False,
+    attempt: int = 0,
+    final_response: str = "",
+    session_id: str = "",
+    changed_paths: Any = None,
+    **_: Any,
+) -> dict[str, str] | None:
+    """Keep a coding turn going when issue-like language was not logged."""
+    if attempt > 0 or not coding or not final_response:
+        return None
+    if not contains_issue_like_language(final_response):
+        return None
+    if explicitly_says_no_issue_to_log(final_response):
+        return None
+    if _issue_path_touched(session_id=session_id, changed_paths=changed_paths):
+        return None
+    return {"action": "continue", "message": PRE_VERIFY_MESSAGE}
+
+
+def transform_llm_output(response_text: str = "", session_id: str = "", **_: Any) -> str | None:
+    """Visible fallback for turns where pre_verify does not run."""
+    if not response_text or not contains_issue_like_language(response_text):
+        return None
+    if explicitly_says_no_issue_to_log(response_text):
+        return None
+    if _issue_path_touched(session_id=session_id):
+        return None
+    if TRANSFORM_GUARD_NOTE.strip() in response_text:
+        return None
+    return response_text.rstrip() + TRANSFORM_GUARD_NOTE
+
+
+def on_session_end(session_id: str = "", **_: Any) -> None:
+    """Clean up per-session issue tracking state."""
+    session = str(session_id or "")
+    with _state_lock:
+        for key in [key for key in _turn_state if key[0] == session]:
+            _turn_state.pop(key, None)
+        _latest_turn_by_session.pop(session, None)
+
+
 def main() -> int:
     """Shell-hook compatibility entrypoint."""
     try:
diff --git a/plugins/hermes-planning-guards/hermes_planning_guards/plugin.py b/plugins/hermes-planning-guards/hermes_planning_guards/plugin.py
index 8db29fc..d19c041 100644
--- a/plugins/hermes-planning-guards/hermes_planning_guards/plugin.py
+++ b/plugins/hermes-planning-guards/hermes_planning_guards/plugin.py
@@ -2,9 +2,19 @@
 from __future__ import annotations

 from .block_env_files import pre_tool_call
-from .out_of_scope_reminder import pre_llm_call
+from .out_of_scope_reminder import (
+    on_session_end,
+    post_tool_call,
+    pre_llm_call,
+    pre_verify,
+    transform_llm_output,
+)


 def register(ctx) -> None:
     ctx.register_hook("pre_tool_call", pre_tool_call)
     ctx.register_hook("pre_llm_call", pre_llm_call)
+    ctx.register_hook("post_tool_call", post_tool_call)
+    ctx.register_hook("pre_verify", pre_verify)
+    ctx.register_hook("transform_llm_output", transform_llm_output)
+    ctx.register_hook("on_session_end", on_session_end)
diff --git a/plugins/hermes-planning-guards/plugin.yaml b/plugins/hermes-planning-guards/plugin.yaml
index 57fc9b8..eb4657b 100644
--- a/plugins/hermes-planning-guards/plugin.yaml
+++ b/plugins/hermes-planning-guards/plugin.yaml
@@ -1,7 +1,11 @@
 name: hermes-planning-guards
 version: "0.1.0"
-description: "Planning workflow guardrails: block unsafe .env* tool access and inject out-of-scope issue logging reminders."
+description: "Planning workflow guardrails: block unsafe .env* tool access and actively enforce out-of-scope issue logging reminders."
 author: "tahara-san and contributors"
 provides_hooks:
   - pre_tool_call
   - pre_llm_call
+  - post_tool_call
+  - pre_verify
+  - transform_llm_output
+  - on_session_end
diff --git a/plugins/hermes-planning-guards/tests/test_out_of_scope_reminder.py b/plugins/hermes-planning-guards/tests/test_out_of_scope_reminder.py
index 510cfeb..2518e37 100644
--- a/plugins/hermes-planning-guards/tests/test_out_of_scope_reminder.py
+++ b/plugins/hermes-planning-guards/tests/test_out_of_scope_reminder.py
@@ -1,8 +1,289 @@
-from hermes_planning_guards.out_of_scope_reminder import pre_llm_call
+from hermes_planning_guards.out_of_scope_reminder import (
+    PRE_VERIFY_MESSAGE,
+    TRANSFORM_GUARD_NOTE,
+    contains_issue_like_language,
+    explicitly_says_no_issue_to_log,
+    extract_issue_paths_from_tool_call,
+    on_session_end,
+    post_tool_call,
+    pre_llm_call,
+    pre_verify,
+    reset_issue_tracking_state,
+    transform_llm_output,
+)
+
+
+def setup_function():
+    reset_issue_tracking_state()


 def test_pre_llm_call_injects_context():
-    result = pre_llm_call()
+    result = pre_llm_call(session_id="s1", turn_id="t1")
     assert "context" in result
     assert "tasks/out-of-scope-issues" in result["context"]
     assert "Dependabot" in result["context"]
+
+
+def test_contains_issue_like_language_uses_focused_trigger_set():
+    assert contains_issue_like_language("Found a pre-existing bug")
+    assert contains_issue_like_language("This is OUT-OF-SCOPE for now")
+    assert contains_issue_like_language("Follow-up: simplify this later")
+    assert contains_issue_like_language("This no-op looks suspicious")
+    assert contains_issue_like_language("Skipped unrelated test")
+    assert contains_issue_like_language("There is a code smell here")
+    assert not contains_issue_like_language("Everything passed cleanly")
+    assert not contains_issue_like_language("This unskipped setup is unrelated")
+
+
+def test_explicit_no_issue_to_log_language_is_detected():
+    assert explicitly_says_no_issue_to_log("There is no out-of-scope issue to log.")
+    assert explicitly_says_no_issue_to_log("Skipped work is not an out-of-scope issue.")
+    assert explicitly_says_no_issue_to_log(
+        "Nothing to log under tasks/out-of-scope-issues for this follow-up note."
+    )
+    assert not explicitly_says_no_issue_to_log("There is an out-of-scope issue.")
+
+
+def test_extract_issue_paths_from_write_file():
+    paths = extract_issue_paths_from_tool_call(
+        "write_file",
+        {"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+    )
+    assert paths == {"tasks/out-of-scope-issues/medium/20260709_bug.md"}
+
+
+def test_extract_issue_paths_from_patch_replace_mode():
+    paths = extract_issue_paths_from_tool_call(
+        "patch",
+        {"path": "tasks/out-of-scope-issues/low/20260709_cleanup.md"},
+    )
+    assert paths == {"tasks/out-of-scope-issues/low/20260709_cleanup.md"}
+
+
+def test_extract_issue_paths_from_v4a_patch_targets():
+    paths = extract_issue_paths_from_tool_call(
+        "patch",
+        {
+            "mode": "patch",
+            "patch": """*** Begin Patch
+*** Add File: tasks/out-of-scope-issues/high/20260709_stale.md
++**Issue**
+*** Update File: src/app.py
+*** End Patch
+""",
+        },
+    )
+    assert paths == {"tasks/out-of-scope-issues/high/20260709_stale.md"}
+
+
+def test_extract_issue_paths_from_terminal_command_text():
+    paths = extract_issue_paths_from_tool_call(
+        "terminal",
+        {"command": "python scripts/write.py tasks/out-of-scope-issues/manual/20260709_item.md"},
+    )
+    assert "tasks/out-of-scope-issues/manual/20260709_item.md" in paths
+
+
+def test_pre_verify_allows_clean_response():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    assert pre_verify(coding=True, final_response="Done; all checks passed.", session_id="s1") is None
+
+
+def test_pre_verify_allows_after_issue_path_touch():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    post_tool_call(
+        tool_name="write_file",
+        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        status="ok",
+        session_id="s1",
+        turn_id="t1",
+    )
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1") is None
+
+
+def test_pre_verify_allows_changed_issue_path_without_observed_tool_call():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    assert (
+        pre_verify(
+            coding=True,
+            final_response="Found a follow-up.",
+            session_id="s1",
+            changed_paths=["tasks/out-of-scope-issues/low/20260709_followup.md"],
+        )
+        is None
+    )
+
+
+def test_pre_verify_continues_when_issue_like_language_unlogged():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    result = pre_verify(coding=True, final_response="There is a pre-existing issue.", session_id="s1")
+    assert result == {"action": "continue", "message": PRE_VERIFY_MESSAGE}
+
+
+def test_pre_verify_allows_explicit_no_issue_to_log_response():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    assert (
+        pre_verify(
+            coding=True,
+            final_response="Skipped setup is not an out-of-scope issue.",
+            session_id="s1",
+        )
+        is None
+    )
+
+
+def test_pre_verify_is_scoped_to_coding_and_first_attempt():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    assert pre_verify(coding=False, final_response="There is a code smell.", session_id="s1") is None
+    assert pre_verify(coding=True, attempt=1, final_response="There is a code smell.", session_id="s1") is None
+
+
+def test_transform_llm_output_appends_visible_fallback_when_unlogged():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    response = transform_llm_output("Skipped a follow-up item.", session_id="s1")
+    assert response == "Skipped a follow-up item." + TRANSFORM_GUARD_NOTE
+
+
+def test_transform_llm_output_allows_explicit_no_issue_to_log_response():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    assert transform_llm_output(
+        "Skipped setup is not an out-of-scope issue.",
+        session_id="s1",
+    ) is None
+
+
+def test_transform_llm_output_leaves_logged_or_clean_output_unchanged():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    assert transform_llm_output("Everything passed.", session_id="s1") is None
+    post_tool_call(
+        tool_name="patch",
+        args={"path": "tasks/out-of-scope-issues/other/20260709_note.md"},
+        status="ok",
+        session_id="s1",
+        turn_id="t1",
+    )
+    assert transform_llm_output("Skipped a follow-up item.", session_id="s1") is None
+
+
+def test_failed_tool_status_does_not_count_as_logged():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    post_tool_call(
+        tool_name="write_file",
+        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        status="blocked",
+        session_id="s1",
+        turn_id="t1",
+    )
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")
+
+
+def test_failed_status_string_does_not_count_as_logged():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    post_tool_call(
+        tool_name="write_file",
+        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        status="failed",
+        session_id="s1",
+        turn_id="t1",
+    )
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")
+
+
+def test_error_result_without_status_does_not_count_as_logged():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    post_tool_call(
+        tool_name="write_file",
+        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        result='{"error":"write failed"}',
+        session_id="s1",
+        turn_id="t1",
+    )
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")
+
+
+def test_nonzero_terminal_result_without_status_does_not_count_as_logged():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    post_tool_call(
+        tool_name="terminal",
+        args={"command": "touch tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        result='{"output":"failed","exit_code":1,"error":null}',
+        session_id="s1",
+        turn_id="t1",
+    )
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")
+
+
+def test_empty_or_malformed_result_without_status_does_not_count_as_logged():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    for result in ("", "not json"):
+        post_tool_call(
+            tool_name="write_file",
+            args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+            result=result,
+            session_id="s1",
+            turn_id="t1",
+        )
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")
+
+
+def test_success_result_without_status_counts_as_logged():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    post_tool_call(
+        tool_name="write_file",
+        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        result='{"success":true}',
+        session_id="s1",
+        turn_id="t1",
+    )
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1") is None
+
+
+def test_repeated_pre_llm_call_same_turn_preserves_issue_touch():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    post_tool_call(
+        tool_name="write_file",
+        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        status="ok",
+        session_id="s1",
+        turn_id="t1",
+    )
+    pre_llm_call(session_id="s1", turn_id="t1")
+    assert transform_llm_output("Found a pre-existing issue.", session_id="s1") is None
+
+
+def test_repeated_pre_llm_call_without_turn_id_resets_issue_touch_safely():
+    pre_llm_call(session_id="s1")
+    post_tool_call(
+        tool_name="write_file",
+        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        status="ok",
+        session_id="s1",
+    )
+    pre_llm_call(session_id="s1")
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")
+
+
+def test_new_turn_resets_previous_issue_touch():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    post_tool_call(
+        tool_name="write_file",
+        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        status="ok",
+        session_id="s1",
+        turn_id="t1",
+    )
+    pre_llm_call(session_id="s1", turn_id="t2")
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")
+
+
+def test_on_session_end_clears_tracking_state():
+    pre_llm_call(session_id="s1", turn_id="t1")
+    post_tool_call(
+        tool_name="write_file",
+        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
+        status="ok",
+        session_id="s1",
+        turn_id="t1",
+    )
+    on_session_end(session_id="s1")
+    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")
diff --git a/plugins/hermes-planning-guards/tests/test_plugin_registration.py b/plugins/hermes-planning-guards/tests/test_plugin_registration.py
index c36225a..6225f62 100644
--- a/plugins/hermes-planning-guards/tests/test_plugin_registration.py
+++ b/plugins/hermes-planning-guards/tests/test_plugin_registration.py
@@ -48,4 +48,11 @@ def test_register_wires_expected_hooks():
     ctx = FakeContext()
     module.register(ctx)
     names = [name for name, _ in ctx.hooks]
-    assert names == ["pre_tool_call", "pre_llm_call"]
+    assert names == [
+        "pre_tool_call",
+        "pre_llm_call",
+        "post_tool_call",
+        "pre_verify",
+        "transform_llm_output",
+        "on_session_end",
+    ]

```

## File snapshot: tasks/claude-plugin-parity-update/spec.md

```text
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

```

## File snapshot: tasks/claude-plugin-parity-update/todo.md

```text
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
- [~] Mandatory Codex-style independent review rerun pending against `tasks/claude-plugin-parity-update/reviews/final-implementation-review-bundle-v4.md`; round 1 failed and was fixed in source/tests; Claude v2/v3 robustness notes were fixed before final review, including absent-turn_id safe reset.
- [~] Mandatory Claude Code Opus 4.8 @ xhigh interactive review rerun pending against the same v2 implementation bundle; round 1, v2, and v3 approvals are stale after final robustness hardening.
- [ ] Aggregate final review verdict pending.
- [ ] Final report pending after review verdicts are saved.

```

## File snapshot: tasks/claude-plugin-parity-update/reviews/codex-final-review-round1-failed.json

```text
{
  "passed": false,
  "security_concerns": [],
  "logic_errors": [
    "`post_tool_call` does not correctly determine successful tool execution in real Hermes hook payloads. The Hermes hook signature provides `result` as a JSON string and may not provide a `status` parameter; failed write/patch/terminal calls with error JSON and no status are counted as successful issue-file touches, causing `pre_verify`/`transform_llm_output` to allow final responses with issue-like language even though no issue file was actually written."
  ],
  "test_gaps": [
    "Tests only cover synthetic `status='blocked'` failure handling and do not cover `result` JSON containing an error with no status.",
    "Tests do not cover common failure status strings such as `failed` being treated as failure."
  ],
  "suggestions": [
    "Change `post_tool_call` to accept and inspect `result`, parse JSON, and return without marking a touch when the result contains an error or otherwise indicates failure; keep optional status handling as backwards-compatible input.",
    "Add focused tests for result error JSON, malformed/empty result behavior, and success result shape."
  ],
  "summary": "Codex-style review failed on successful-touch detection; source/env scope otherwise looked clean.",
  "delegation_id": "deleg_c4fea4be",
  "subagent_session_id": "20260709_115014_fdfd7a",
  "bundle_path": "tasks/claude-plugin-parity-update/reviews/final-implementation-review-bundle.md",
  "captured_at": "2026-07-09T11:57:42.910798+00:00"
}

```
