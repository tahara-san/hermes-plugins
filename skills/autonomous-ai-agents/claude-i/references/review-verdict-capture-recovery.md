# Claude Code review verdict capture recovery

Use this when an interactive Claude Code review completes but the saved tmux pane artifact is missing the explicit verdict line, or a partial pane capture starts mid-output.

## Symptoms

- The pane shows useful findings, but the captured artifact lacks `VERDICT: APPROVED` / `VERDICT: CHANGES_REQUIRED`.
- `tmux capture-pane -S -1000` still misses the top of the final answer because pane history is limited.
- The prompt line contains an unsent follow-up from the operator after the verdict.
- Claude reports `API Error: Connection closed mid-response` or similar after reading the bundle, leaving analysis text but no final parseable verdict.

## Recovery pattern

1. Do **not** count the partial artifact as a mandatory approval yet.
2. Resume or keep the same Claude Code session open.
3. Ask Claude to restate only the verdict structure, without any file reads, edits, or commands. If the prior response was interrupted after Claude already read the bundle, explicitly say “based only on the context you already reviewed” so it does not restart the review or request more permissions:

```text
Your previous response was interrupted after you read the complete bundle. Do not read files, edit files, or run commands now. Based only on the context you already reviewed, restate only the final review verdict in the requested structure. Include VERDICT, BLOCKERS, NON_BLOCKING_NOTES, and TESTING_GAPS.
```

For JSON-gated reviews, ask for only the JSON object and save a clean parsed JSON artifact separately from the raw tmux transcript.

4. Capture the pane again and verify the saved artifact contains:
   - `VERDICT: APPROVED` or `VERDICT: CHANGES_REQUIRED`;
   - `BLOCKERS:`;
   - an explicit blocker list or `none`.
5. If an accidental follow-up is sitting unsent at the prompt, clear it with `C-u` before sending `/exit`:

```bash
tmux send-keys -t "$SESSION" C-u
tmux send-keys -t "$SESSION" '/exit' Enter
```

6. If Claude returns non-blocking suggestions and you choose not to implement them, record that disposition in the aggregate verdict so the approval remains current.

## Pitfall

Do not paste a new implementation/fix request into a review session after approval unless you intentionally want to stale the approval and rerun verification/review. Clear unsent text before exiting.