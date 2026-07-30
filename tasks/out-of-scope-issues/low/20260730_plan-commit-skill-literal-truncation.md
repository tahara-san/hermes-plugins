**Issue**

`plan-commit/SKILL.md` contains a literal truncation marker in a cut-off policy line, so the published skill source is incomplete.

**Location**

`skills/software-development/plan-commit/SKILL.md:157`

**Severity**

low

**Context**

A repository-wide literal-truncation scan performed while repairing the in-scope planning-workflow skill found this separate cut-off line. The existing `20260711_plan-commit-missing-reference-links.md` issue tracks two dead reference targets, not source text lost to a truncation marker, so this is not a duplicate. `plan-commit/SKILL.md` was not part of the active helper/meta-review change and was left untouched.

**Suggested Fix**

Recover the exact pre-truncation paragraph from Git history, reconcile it with the current plan-commit policy rather than blindly restoring obsolete wording, and add a policy test that rejects literal truncation markers in public skill entrypoints. Run the plan-commit and planning review-policy suites afterward.
