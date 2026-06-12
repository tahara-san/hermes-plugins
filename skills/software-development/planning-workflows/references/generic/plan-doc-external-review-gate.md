# Plan-doc external review gate

For read-only review of plan documents:

1. Build a saved bundle containing task docs, relevant source context, package/test scripts, git status, and untracked task files.
2. Ask the reviewer for a bounded verdict.
3. Apply blocking findings and useful non-blocking doc improvements.
4. Regenerate the bundle after changes.
5. Rerun review before claiming the plan is approved.
6. Save final review artifacts under `tasks/<task-name>/reviews/`.
