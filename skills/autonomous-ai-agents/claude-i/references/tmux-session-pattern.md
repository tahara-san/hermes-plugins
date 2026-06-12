# tmux session pattern

- Use unique session names.
- Capture before sending blind keys.
- Prefer `send-keys -l` for one-line literal prompts.
- Prefer `load-buffer` + `paste-buffer` for multiline prompts.
- Clean up with `/exit` and `tmux kill-session` when finished.
