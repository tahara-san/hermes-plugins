# Buffdemy backend post-merge dev deploy checklist

Use this when a `/plan-code` implementation has been externally merged and the user wants the local repo/dev stack brought back to the merged state.

## Git sync

1. Fetch/prune origin.
2. Confirm the task PR/branch is merged upstream before deleting or abandoning any branch assumptions.
3. Switch to `develop`.
4. Fast-forward/pull `develop` to `origin/develop`.
5. Verify:
   - `git status --short` is clean
   - `git rev-list --left-right --count @{u}...HEAD` is `0 0`
   - local `HEAD` matches `origin/develop`
6. Leave local feature branches alone unless the user explicitly asks for cleanup.

## Dev-stack deploy

For Buffdemy backend Docker/compose work, force development mode unless the user explicitly requested production:

```bash
NODE_ENV=development docker compose up -d --build --force-recreate
```

Do not rely on the invoking shell's `NODE_ENV`; an inherited `NODE_ENV=production` can make the dev API restart-loop on production-only config such as Elasticsearch token requirements.

## Smoke verification

After the stack is recreated:

1. Inspect service status for app services (`api`, `outbox-processor`, `unified-consumer`, `cron-worker`) and dependencies.
2. Verify the API container environment reports `NODE_ENV=development`.
3. Smoke `/health` and require HTTP 200.
4. If a service fails, check logs and distinguish expected external/config gates from regressions before reporting completion.

## Report shape

Keep the user-facing report concise:

- git branch/sync state
- deploy mode (`NODE_ENV=development`)
- service status
- smoke-check result
- any branch cleanup intentionally not performed
