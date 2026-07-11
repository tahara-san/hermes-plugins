# Plan-Code Unrecoverable Interactive Codex Verdict Replacement

Use this when a mandatory `plan-code` interactive Codex TUI session appears to finish, but no parseable verdict is durably available.

## Trigger

- A mandatory interactive Codex review has a known managed tmux session and immutable bundle identity.
- The pane disappears, exits, or becomes unavailable before a complete raw capture is saved.
- No parseable normalized verdict exists in review artifacts.
- The model/effort banner, bundle identity, or final verdict cannot be fully attested from retained evidence.

## Rule

Session completion is not approval. A mandatory review gate requires a parseable saved verdict tied to the finalized bundle, raw pane evidence, and the GPT-5.6 SOL @ xhigh attestation—or an explicit user waiver. Do not infer or reconstruct a verdict from timing, partial pane text, or an exit status.

## Recovery sequence

1. Inspect the original managed tmux session by its exact session/pane id.
   - Capture a wide pane window if the session still exists.
   - Verify the displayed model/effort, reviewed bundle path/hash, and complete final verdict.
2. Check durable local review artifacts.
   - Look for the raw pane capture and normalized verdict associated with the same bundle identity.
   - Reject evidence that belongs to an older or different bundle.
3. Save an unrecovered/superseded artifact when the evidence is incomplete.
   - Include the tmux session, bundle path/hash, available pane evidence, missing attestation/verdict fields, and why it cannot satisfy the gate.
   - Status examples: `SUPERSEDED_UNRECOVERED_VERDICT`, `pending_unrecovered_verdict`.
4. Start a fresh pinned interactive Codex TUI session against the same current immutable bundle when it remains current.
   - Keep the replacement session and raw artifact distinct from the lost attempt.
   - Never substitute a Hermes `delegate_task` reviewer, `codex exec`, or `codex review`.
5. Patch live task docs/TODOs immediately.
   - The active review row should name the replacement tmux session and pending artifact.
   - Do not mark the phase/task complete until the replacement produces parseable passing JSON with the required attestation and the final artifact-consistency/doc gate passes.

## Artifact checklist

- Superseded/unrecovered artifact for the lost interactive session.
- Pending artifact for the replacement interactive session.
- Any late older pane/verdict evidence saved as superseded, not counted as active.
- Task docs name one active review blocker and distinguish historical/superseded evidence.
- `git diff --check` and JSON parsing pass after artifact edits.

## Pitfalls

- Do not let a stale approval from an older bundle close the current gate.
- Do not count a TUI exit as approval without the final normalized verdict and attestation.
- Do not leave multiple pending files that each appear active; retire or supersede stale pending markers.
- If task docs change while reconciling review artifacts, regenerate the bundle and rerun every required independent review lane, launching them before waiting on any one lane.
