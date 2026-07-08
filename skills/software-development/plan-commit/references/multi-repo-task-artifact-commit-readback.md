# Multi-repo task artifact commit readback

Use this when a completed plan-code task spans more than one repository, but the task directory lives in only one repo (commonly frontend task artifacts documenting a backend test/code change).

## Problem pattern

A backend/source change may be committed and pushed before the frontend task-artifact commit. When a later pre-commit artifact-consistency review inspects the frontend task docs plus current backend status, the backend file no longer appears dirty. A reviewer can misclassify that as a contradiction if the bundle only says "backend file changed" without showing the backend commit readback.

## Safe sequence

1. Commit/push each repo's implementation scope with exact path staging.
2. After a cross-repo implementation commit is pushed, record its commit SHA/branch in the task artifacts that live in the other repo before staging those artifacts.
   - Example note: "Backend test change was committed and pushed first as `<sha>` on backend branch `<branch>`, so it is no longer expected to appear dirty during the frontend task-artifact commit."
3. Include both of these in any pre-commit artifact-consistency bundle:
   - current backend `git status --short --branch`;
   - backend commit readback for the task path, e.g. `git log --oneline --decorate -1 --name-status -- <backend-path>` plus `git rev-parse --short HEAD` / upstream readback.
4. If a consistency review fails because it only saw clean backend status, save that failed review as superseded, patch task docs with backend commit readback, regenerate the consistency bundle, and rerun the review.
5. Only then commit the frontend task artifacts and proceed to task-directory cleanup.

## Pitfalls

- Do not imply a backend change is still unstaged/dirty after it has already been committed and pushed.
- Do not rely on status alone for already-pushed cross-repo work; status proves local cleanliness, not historical inclusion.
- Do not amend/force-push just to make both repos appear dirty at once; normal separate commits with explicit readback are cleaner.
