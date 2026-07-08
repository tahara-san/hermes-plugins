# Recovering a Claude Code review verdict from JSONL transcripts

Use this when an interactive Claude Code review session disappears, the tmux pane is gone, or the final verdict scrolled out before capture.

## When this applies

- Claude Code was started through `claude-i` in tmux/PTTY.
- The session read the prepared review bundle and likely produced a verdict.
- `tmux capture-pane` can no longer find the pane/session, or pane scrollback lacks the final verdict.
- You need a saved review artifact for a mandatory review gate.

## Recovery steps

1. Do **not** count the review as passed from memory or partial pane output.
2. Locate recent project transcripts under Claude's local store:
   - `~/.claude/projects/-workspace-dev-<repo-name>/*.jsonl`
   - sort by modification time and search for the bundle path or task slug.
3. Parse assistant messages from the matching JSONL and extract the last message containing verdict markers such as `VERDICT:`, `BLOCKERS:`, `APPROVED`, or `CHANGES_REQUIRED`.
4. Save the recovered text as the raw review artifact and include:
   - transcript path;
   - captured model/banner if available from pane output or JSONL model field;
   - note that the artifact was recovered from local transcript storage;
   - whether Claude edited files or ran commands (verify from transcript/pane; if uncertain, say uncertain and inspect git status).
5. If the JSONL has only partial analysis and no explicit verdict, rerun the review or save an incomplete/blocker artifact. Do not promote partial analysis to approval.

## Useful extraction pattern

```bash
python - <<'PY'
from pathlib import Path
import json, time
root = Path('/home/hermes/.claude/projects/-workspace-dev-buffdemy2-web')
files = sorted(root.glob('*.jsonl'), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
for p in files:
    text = p.read_text(errors='replace')
    if 'implementation-review-bundle.md' not in text and 'task-slug' not in text:
        continue
    matches = []
    for line in text.splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        msg = obj.get('message') or {}
        if msg.get('role') != 'assistant':
            continue
        parts = msg.get('content') or []
        body = ''.join(part.get('text', '') for part in parts if isinstance(part, dict))
        if any(marker in body for marker in ['VERDICT:', 'BLOCKERS:', 'APPROVED', 'CHANGES_REQUIRED']):
            matches.append(body)
    print(p, time.ctime(p.stat().st_mtime))
    print(matches[-1] if matches else 'NO EXPLICIT VERDICT')
PY
```

## Pitfalls

- Another Claude tmux session for a different repo/task may be active. Inspect before sending anything; do not paste recovery prompts into an unrelated session.
- Transcript search results can match old tasks that used similarly named bundles. Always match the active repo and task slug.
- A recovered approval becomes stale if source/test/task artifacts changed after the transcript timestamp.
