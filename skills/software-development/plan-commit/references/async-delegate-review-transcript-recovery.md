# Async Delegate Review Transcript Recovery During Commit Prep

Use when a mandatory plan-code/code-review delegate was dispatched but the parent session has not received the verdict before commit readiness or commit/push.

## Recovery pattern

1. Search Hermes logs for the delegation id, bundle path, or unique review phrase:
   - `grep -R "<delegation_id>\|<bundle-name-or-review-phrase>" ~/.hermes/logs/agent.log*`
2. Identify the child line with `platform=subagent` and note `session=<session_id>`.
3. Confirm whether a later `Turn ended ... session=<session_id>` exists. If it does, the reviewer likely completed even if the parent did not receive the message.
4. Read the child transcript with `session_search(session_id="<session_id>", profile="default")`.
5. If `session_search` returns a persisted-output file because the transcript is huge, parse that file as JSON and inspect the final non-empty assistant message.
6. Extract and parse the JSON verdict. Save it as a review artifact. Only proceed if it is parseable and passing.

## Parser snippet

```python
import json
src = '/tmp/hermes-results/<persisted-output>.txt'
with open(src) as f:
    data = json.load(f)

for message in reversed(data['messages']):
    if message.get('role') == 'assistant' and (message.get('content') or '').strip():
        content = message['content'].strip()
        verdict = json.loads(content[content.find('{'):content.rfind('}') + 1])
        break
```

## Pitfalls

- A dispatch id alone is not a review pass.
- A `Turn ended` log line alone is not a review pass; the verdict still must be recovered and parsed.
- Recover the Hermes delegate or dispatch a fresh bounded `delegate_task` reviewer. If no parseable verdict is available, save a blocker and stop before staging; never invoke or inspect a local Codex CLI as fallback.
- Claude Code remains a separate, explicitly requested CLI review lane through `claude-i`; it is not a local Codex fallback.
- Do not encode local CLI auth/setup failures as durable constraints; they are environment state, not workflow rules.
