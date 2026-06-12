# Interactive Claude Code pattern

Use `tmux` for interactive Claude Code sessions:

```bash
tmux new-session -d -s claude-task -x 160 -y 48
tmux send-keys -t claude-task 'cd /path/to/repo && claude' Enter
sleep 5
tmux capture-pane -t claude-task -p -S -120
```

For multiline prompts:

```bash
tmux load-buffer /tmp/prompt.md
tmux paste-buffer -t claude-task
tmux send-keys -t claude-task Enter
```

Avoid shell-quoting large prompts directly.
