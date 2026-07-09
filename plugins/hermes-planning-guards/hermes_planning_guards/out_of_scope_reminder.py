"""Inject and enforce out-of-scope issue tracking guidance."""
from __future__ import annotations

import json
import re
import sys
import threading
from dataclasses import dataclass, field
from typing import Any, Iterable

REMINDER = """
Planning guard policy: out-of-scope issue tracking.
When you encounter warnings, issues, code smells, bugs, skipped items, follow-ups,
or potential problems during a task that are outside the current task scope, do
not silently ignore them and do not fix them inline unless the user explicitly asks.

Log each non-exempt finding as a separate markdown file under:
  tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md

If the issue requires human investigation or intervention, use:
  tasks/out-of-scope-issues/<priority>/manual/<YYYYMMDD>_<short-kebab>.md

Priority must be one of:
  critical, high, medium, low, proposal, other

Each file must contain these sections in order:
  **Issue**
  **Location**
  **Severity**
  **Context**
  **Suggested Fix**

Before creating a new file, check for an existing matching issue and update it
instead of duplicating it. Mention logged out-of-scope issues in the wrap-up.

Exception: do not create or update out-of-scope issue files solely for GitHub
Dependabot alerts/security advisory counts. Dependabot alerts are already tracked
in GitHub; mention them briefly in the wrap-up only when relevant, or work from
GitHub/gh/npm audit when the user explicitly asks to triage or fix them.
""".strip()

ISSUE_PATH_FRAGMENT = "tasks/out-of-scope-issues"
ISSUE_LIKE_LANGUAGE_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_])(?:pre-existing|out-of-scope|follow-up|no-op|skipped|code smell)(?![A-Za-z0-9_])"
)
NO_ISSUE_TO_LOG_RE = re.compile(
    r"(?i)(?:"
    r"no\s+out-of-scope\s+issues?\s+to\s+log"
    r"|not\s+(?:an?\s+)?out-of-scope\s+issues?"
    r"|nothing\s+to\s+log\s+under\s+tasks/out-of-scope-issues"
    r")"
)
V4A_PATCH_TARGET_PREFIXES = (
    "*** Update File:",
    "*** Add File:",
    "*** Delete File:",
)
FAILED_TOOL_STATUSES = {"blocked", "error", "timeout", "cancelled", "failed", "failure"}

PRE_VERIFY_MESSAGE = (
    "Planning guard: your draft final response mentions potential "
    "out-of-scope, pre-existing, follow-up, skipped, no-op, or code-smell work, "
    "but no tasks/out-of-scope-issues/ file was touched this turn. "
    "Before finishing, either create/update the required issue file with sections "
    "Issue, Location, Severity, Context, and Suggested Fix, or revise the final "
    "response to explicitly state why every such mention is not an out-of-scope "
    "issue to log. Dependabot alert/advisory counts remain exempt unless the user "
    "asked to triage or fix them."
)

TRANSFORM_GUARD_NOTE = (
    "\n\nPlanning guard note: this response mentions potential out-of-scope, "
    "pre-existing, follow-up, skipped, no-op, or code-smell work, but this turn "
    "did not touch tasks/out-of-scope-issues/. If that mention is a real "
    "out-of-scope finding, log it under tasks/out-of-scope-issues/<priority>/ "
    "with Issue, Location, Severity, Context, and Suggested Fix; Dependabot "
    "alert/advisory counts are exempt unless explicitly being triaged."
)


@dataclass
class TurnIssueState:
    touched_issue_path: bool = False
    touched_paths: set[str] = field(default_factory=set)


_state_lock = threading.Lock()
_turn_state: dict[tuple[str, str], TurnIssueState] = {}
_latest_turn_by_session: dict[str, str] = {}


def _normalize_path_text(text: str) -> str:
    return str(text or "").strip().strip(" \t\r\n'\"`()[]{}<>,").replace("\\", "/")


def is_issue_path(text: str) -> bool:
    """Return True when text clearly references tasks/out-of-scope-issues/."""
    normalized = _normalize_path_text(text)
    return normalized == ISSUE_PATH_FRAGMENT or f"{ISSUE_PATH_FRAGMENT}/" in normalized


def contains_issue_like_language(text: str) -> bool:
    """Detect Claude planner Stop-hook issue-like trigger language."""
    return bool(text and ISSUE_LIKE_LANGUAGE_RE.search(text))


def explicitly_says_no_issue_to_log(text: str) -> bool:
    """Return True when the response explicitly says no issue file is needed."""
    return bool(text and NO_ISSUE_TO_LOG_RE.search(text))


def _extract_v4a_patch_targets(patch_text: str) -> set[str]:
    targets: set[str] = set()
    for line in str(patch_text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith(V4A_PATCH_TARGET_PREFIXES):
            targets.add(stripped.split(":", 1)[1].strip())
    return targets


def _terminal_issue_path_references(command: str) -> set[str]:
    references: set[str] = set()
    for token in re.split(r"\s+", str(command or "")):
        cleaned = _normalize_path_text(token)
        if is_issue_path(cleaned):
            references.add(cleaned)
    if not references and is_issue_path(str(command or "")):
        references.add(ISSUE_PATH_FRAGMENT)
    return references


def extract_issue_paths_from_tool_call(tool_name: str, args: Any) -> set[str]:
    """Extract issue-path touches from write-like Hermes tool calls."""
    tool_input = args if isinstance(args, dict) else {}
    paths: set[str] = set()

    if tool_name == "write_file":
        path = str(tool_input.get("path") or "")
        if is_issue_path(path):
            paths.add(path)
        return paths

    if tool_name == "patch":
        mode = tool_input.get("mode") or "replace"
        if mode == "patch":
            for target in _extract_v4a_patch_targets(str(tool_input.get("patch") or "")):
                if is_issue_path(target):
                    paths.add(target)
        else:
            path = str(tool_input.get("path") or "")
            if is_issue_path(path):
                paths.add(path)
        return paths

    if tool_name == "terminal":
        return _terminal_issue_path_references(str(tool_input.get("command") or ""))

    return paths


def _state_key(session_id: str = "", turn_id: str = "") -> tuple[str, str]:
    session = str(session_id or "")
    turn = str(turn_id or "")
    if not turn:
        turn = _latest_turn_by_session.get(session, "")
    return session, turn


def _begin_turn(session_id: str = "", turn_id: str = "") -> None:
    key = (str(session_id or ""), str(turn_id or ""))
    with _state_lock:
        _latest_turn_by_session[key[0]] = key[1]
        if key[1]:
            _turn_state.setdefault(key, TurnIssueState())
        else:
            _turn_state[key] = TurnIssueState()


def _mark_issue_paths(paths: Iterable[str], session_id: str = "", turn_id: str = "") -> None:
    normalized_paths = {_normalize_path_text(path) for path in paths if is_issue_path(path)}
    if not normalized_paths:
        return
    key = _state_key(session_id, turn_id)
    with _state_lock:
        state = _turn_state.setdefault(key, TurnIssueState())
        state.touched_issue_path = True
        state.touched_paths.update(normalized_paths)
        _latest_turn_by_session[key[0]] = key[1]


def _issue_path_touched(session_id: str = "", turn_id: str = "", changed_paths: Any = None) -> bool:
    if any(is_issue_path(str(path)) for path in (changed_paths or [])):
        return True
    key = _state_key(session_id, turn_id)
    with _state_lock:
        state = _turn_state.get(key)
        return bool(state and state.touched_issue_path)


def _tool_result_indicates_failure(tool_name: str, result: Any, status: str = "") -> bool:
    """Return True when a post_tool_call result/status represents failure.

    Hermes currently supplies a normalized status kwarg, but older/docs-shaped
    payloads may only provide the tool result string. Fail closed when no status
    exists and the result lacks tool-specific success evidence.
    """
    normalized_status = str(status or "").strip().lower()
    if normalized_status in FAILED_TOOL_STATUSES:
        return True
    if normalized_status and normalized_status not in {"ok", "success", "succeeded", "completed"}:
        return True
    if normalized_status in {"ok", "success", "succeeded", "completed"}:
        return False

    if result is None or result == "":
        return True

    parsed = result
    if isinstance(result, str):
        text = result.strip()
        if not text:
            return True
        if text.lower().startswith("error executing tool"):
            return True
        try:
            parsed = json.loads(text)
        except Exception:
            return True

    if not isinstance(parsed, dict):
        return True

    if parsed.get("error"):
        return True
    if parsed.get("success") is False or parsed.get("ok") is False:
        return True
    if parsed.get("success") is True or parsed.get("ok") is True:
        return False

    exit_code = parsed.get("exit_code")
    if exit_code is not None:
        try:
            return int(exit_code) != 0
        except (TypeError, ValueError):
            return True

    if tool_name == "write_file":
        return "bytes_written" not in parsed and "resolved_path" not in parsed
    if tool_name == "patch":
        return "diff" not in parsed and "files_modified" not in parsed

    return True


def reset_issue_tracking_state() -> None:
    """Clear in-memory tracking state; intended for tests and session cleanup."""
    with _state_lock:
        _turn_state.clear()
        _latest_turn_by_session.clear()


def pre_llm_call(session_id: str = "", turn_id: str = "", **_: Any) -> dict[str, str]:
    """Hermes plugin hook callback for pre_llm_call."""
    _begin_turn(session_id=session_id, turn_id=turn_id)
    return {"context": REMINDER}


def post_tool_call(
    tool_name: str = "",
    args: Any = None,
    result: Any = None,
    status: str = "",
    session_id: str = "",
    turn_id: str = "",
    **_: Any,
) -> None:
    """Track successful issue-file touches from write-like tool calls."""
    if _tool_result_indicates_failure(tool_name, result, status=status):
        return
    _mark_issue_paths(
        extract_issue_paths_from_tool_call(tool_name, args),
        session_id=session_id,
        turn_id=turn_id,
    )


def pre_verify(
    coding: bool = False,
    attempt: int = 0,
    final_response: str = "",
    session_id: str = "",
    changed_paths: Any = None,
    **_: Any,
) -> dict[str, str] | None:
    """Keep a coding turn going when issue-like language was not logged."""
    if attempt > 0 or not coding or not final_response:
        return None
    if not contains_issue_like_language(final_response):
        return None
    if explicitly_says_no_issue_to_log(final_response):
        return None
    if _issue_path_touched(session_id=session_id, changed_paths=changed_paths):
        return None
    return {"action": "continue", "message": PRE_VERIFY_MESSAGE}


def transform_llm_output(response_text: str = "", session_id: str = "", **_: Any) -> str | None:
    """Visible fallback for turns where pre_verify does not run."""
    if not response_text or not contains_issue_like_language(response_text):
        return None
    if explicitly_says_no_issue_to_log(response_text):
        return None
    if _issue_path_touched(session_id=session_id):
        return None
    if TRANSFORM_GUARD_NOTE.strip() in response_text:
        return None
    return response_text.rstrip() + TRANSFORM_GUARD_NOTE


def on_session_end(session_id: str = "", **_: Any) -> None:
    """Clean up per-session issue tracking state."""
    session = str(session_id or "")
    with _state_lock:
        for key in [key for key in _turn_state if key[0] == session]:
            _turn_state.pop(key, None)
        _latest_turn_by_session.pop(session, None)


def main() -> int:
    """Shell-hook compatibility entrypoint."""
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    json.dump(pre_llm_call(), sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
