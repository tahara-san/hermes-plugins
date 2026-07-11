# Plan-Doc Read-Only Review Stall Recovery

Use this when an interactive `claude-i` plan-doc review reads the prepared bundle but does not produce an explicit verdict.

## Recovery pattern

1. Confirm the TUI banner/model before sending the review prompt and save/capture it in the eventual artifact.
2. Paste a bounded read-only prompt that forbids edits/tests/builds and asks for a fixed verdict structure.
3. If Claude reads the bundle but remains in long thinking with no verdict, wait a bounded interval rather than indefinitely.
4. Send a short follow-up asking it to stop exploration and return the requested verdict from already-read context.
5. If the follow-up is queued behind thinking/tool state, interrupt with `Ctrl-C` and send a no-tools verdict request.
6. If there is still no explicit verdict after the bounded retry, save the pane as `INCOMPLETE` and stop/kill the session. Do not count the attempt as approval.
7. In plan-doc workflows, write a blocked/pending review artifact naming:
   - the bundle path
   - the model/banner observed
   - any pending interactive Codex tmux session and raw-pane artifact
   - the incomplete Claude artifact path
   - exact resume steps

## Important rule

A Claude session that only read the bundle and did not emit `VERDICT: APPROVED` or equivalent is not a passed review gate. Do not write an aggregate `plan-review.json` until required legs pass or the user explicitly waives a leg.
