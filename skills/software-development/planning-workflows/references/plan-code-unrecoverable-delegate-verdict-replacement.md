# Plan-Code Unrecoverable Delegate Verdict Replacement

Use this when a mandatory `plan-code` Codex-style `delegate_task` appears to finish internally, but no parseable verdict is durably available to the parent session.

## Trigger

- A mandatory delegate review has a known delegation id and child session id.
- Logs show the child session reached `Turn ended: reason=text_response(...)` or otherwise appears complete.
- The final assistant message/verdict is not present in `session_search`, the WebUI parent session, review artifacts, or any durable delivery payload.
- Logs show persistence/delivery issues such as child `Session DB append_message failed` warnings.

## Rule

Internal completion is not approval. A mandatory review gate requires a parseable saved verdict or an explicit user waiver. Do not infer or reconstruct the JSON verdict from response length, timing, or partial transcript.

## Recovery sequence

1. Check the parent delivery surface for the exact delegation id.
   - Search the parent WebUI/session transcript for `[ASYNC DELEGATION BATCH COMPLETE — <id>]`.
   - Search logs for dispatch, child session id, tool calls, and `Turn ended`.
2. Try durable transcript recovery.
   - Use `session_search` for the child session if available.
   - If the child transcript lacks the final message because persistence failed, record that explicitly.
3. Save an unrecovered/superseded artifact for the lost delegate.
   - Include: `delegation_id`, child session id, bundle path, observed log evidence, persistence/delivery failure, and why it cannot satisfy the gate.
   - Status examples: `SUPERSEDED_UNRECOVERED_VERDICT`, `pending_unrecovered_verdict`.
4. Dispatch a fresh replacement delegate against the same current immutable bundle if the bundle remains current.
   - Name it as the active gate in a new pending artifact.
   - Mark older approvals and unrecovered completions as superseded evidence only.
5. Patch live task docs/TODOs immediately.
   - The active review row should name the replacement delegate and pending artifact.
   - Do not mark phase/task complete until the replacement returns parseable passing JSON and the final artifact-consistency/doc gate passes.

## Artifact checklist

- Superseded/unrecovered artifact for the lost delegate.
- Pending artifact for the replacement delegate.
- Any late older delegate approvals saved as `SUPERSEDED_APPROVED`, not counted as active.
- Task docs name one active review blocker and distinguish historical/superseded evidence.
- `git diff --check` and JSON parsing pass after artifact edits.

## Pitfalls

- Do not let a stale approval from an older bundle close the current gate.
- Do not count `Turn ended` as approval without the final JSON.
- Do not leave multiple pending files that each appear active; retire or supersede stale pending markers.
- If task docs change while reconciling review artifacts, plan one final artifact-consistency/doc review before completion.
