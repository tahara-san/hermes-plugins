"""Block Hermes tool access to protected .env* files.

Allows `.env.sample`, `.env.example`, and source/config files such as `.env.ts`, `.env.schema.ts`,
or `.env.config.js` where the basename starts with `.env` but has a source-code
extension.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Optional

SCRIPT_SOURCE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts",
    ".py", ".rb", ".go", ".rs", ".java", ".kt", ".kts", ".swift",
    ".php", ".sh", ".bash", ".zsh", ".fish", ".ps1",
}

ENV_PATH_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_-])(?:[^\s\"'`|;&<>:]*[/\\])?\.env[^\s\"'`|;&<>:]*")

REASON_SUFFIX = (
    "Hermes planning guard forbids tool access to .env* files. "
    "Allowed exceptions: filenames containing 'sample' or 'example', or .env* files with "
    "script/source extensions such as .ts, .js, .tsx, .jsx, .mjs, .cjs, etc."
)


def _basename(path: str) -> str:
    if not path:
        return ""
    text = str(path).strip().strip(" \t\r\n'\"`()[]{}<>,")
    if not text:
        return ""
    return PurePosixPath(text.replace("\\", "/")).name or PureWindowsPath(text).name


def _has_allowed_script_extension(base_lower: str) -> bool:
    return any(base_lower.endswith(ext) for ext in SCRIPT_SOURCE_EXTENSIONS)


def is_blocked_basename(base: str) -> bool:
    if not base:
        return False
    base_lower = base.lower()
    if not base_lower.startswith(".env"):
        return False
    if "sample" in base_lower or "example" in base_lower:
        return False
    if _has_allowed_script_extension(base_lower):
        return False
    return True


def _block(message: str) -> dict[str, str]:
    return {"action": "block", "message": message}


def check_path(path: str, label: str = "path") -> Optional[dict[str, str]]:
    if not path:
        return None
    if is_blocked_basename(_basename(path)):
        return _block(f"Blocked env-file access via {label}: {path}. {REASON_SUFFIX}")
    return None


def check_glob_or_pattern(pattern: str, label: str = "pattern") -> Optional[dict[str, str]]:
    if not pattern:
        return None
    base = _basename(pattern)
    if is_blocked_basename(base):
        return _block(f"Blocked env-file glob/search target via {label}: {pattern}. {REASON_SUFFIX}")
    if base.lower().startswith(".env") and "sample" not in base.lower() and "example" not in base.lower():
        suffixless = base.rstrip("*?[]!").lower()
        if not _has_allowed_script_extension(suffixless):
            return _block(f"Blocked env-file glob/search target via {label}: {pattern}. {REASON_SUFFIX}")
    return None


def check_text_for_env_token(text: str, label: str) -> Optional[dict[str, str]]:
    if not text:
        return None
    for match in ENV_PATH_TOKEN_RE.finditer(text):
        token = match.group(0)
        if is_blocked_basename(_basename(token)):
            return _block(f"Blocked: {label} references env file '{token}'. {REASON_SUFFIX}")
    return None


def check_v4a_patch(patch_text: str) -> Optional[dict[str, str]]:
    if not patch_text:
        return None
    for line in patch_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("*** Update File:", "*** Add File:", "*** Delete File:")):
            target = stripped.split(":", 1)[1].strip()
            result = check_path(target, "patch target")
            if result is not None:
                return result
    return check_text_for_env_token(patch_text, "patch content")


def pre_tool_call(tool_name: str = "", args: Any = None, **_: Any) -> Optional[dict[str, str]]:
    """Hermes plugin hook callback for pre_tool_call."""
    tool_input = args if isinstance(args, dict) else {}

    if tool_name in {"read_file", "write_file"}:
        return check_path(str(tool_input.get("path") or ""), "path")

    if tool_name == "patch":
        mode = tool_input.get("mode") or "replace"
        if mode == "patch":
            return check_v4a_patch(str(tool_input.get("patch") or ""))
        return check_path(str(tool_input.get("path") or ""), "path")

    if tool_name == "search_files":
        for key in ("path", "pattern", "file_glob"):
            result = check_glob_or_pattern(str(tool_input.get(key) or ""), key)
            if result is not None:
                return result
        return None

    if tool_name == "terminal":
        return check_text_for_env_token(str(tool_input.get("command") or ""), "terminal command")

    if tool_name == "execute_code":
        return check_text_for_env_token(str(tool_input.get("code") or ""), "execute_code script")

    return None


def main() -> int:
    """Shell-hook compatibility entrypoint."""
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    result = pre_tool_call(
        tool_name=payload.get("tool_name") or "",
        args=payload.get("tool_input") or {},
    )
    if result:
        json.dump({"decision": result["action"], "reason": result["message"]}, sys.stdout)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
