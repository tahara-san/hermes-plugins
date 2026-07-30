# Plan-issues helper shebang/file-mode mismatch

**Issue**

Ruff reports `EXE001`: `plan_issues_workflow.py` has an executable shebang but is not marked executable.

**Location**

`skills/software-development/planning-workflows/scripts/plan_issues_workflow.py:1`

**Severity**

Low

**Context**

The mismatch predates the two-lane meta-review changes and was surfaced by an optional Ruff check. The helper is currently invoked explicitly with `python3`, so this does not block the workflow or its test suite. Resolving it requires choosing whether the repository intends direct execution or Python-only invocation.

**Suggested Fix**

Either mark the script executable in Git if direct `./plan_issues_workflow.py` invocation is supported, or remove the shebang and keep documented `python3 ...` invocation. Add the chosen convention to repository validation if it should remain enforced.
