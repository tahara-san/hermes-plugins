"""Inject out-of-scope issue tracking guidance before LLM calls."""
from __future__ import annotations

import json
import sys
from typing import Any

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


def pre_llm_call(**_: Any) -> dict[str, str]:
    """Hermes plugin hook callback for pre_llm_call."""
    return {"context": REMINDER}


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
