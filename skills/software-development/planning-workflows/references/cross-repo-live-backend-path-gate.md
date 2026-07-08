# Cross-repo live backend path gate

Use when a plan-code or plan-doc task spans a frontend repo plus a backend service, especially when local smoke tests depend on a running Docker/containerized backend or when several similarly named backend repos exist.

## Problem pattern

A task document, prior session, or local directory search may point to the wrong backend checkout. The frontend's live local API can be served from a different mounted repo/path, and similarly named legacy repos can contain plausible but obsolete notification/routes/model code. If the agent edits or plans against the wrong checkout and then smokes the frontend, the live backend can still return stale behavior (for example `GET /link` returns `not_found`) because the running container is mounted from a different source tree.

## Required workflow

1. Before backend edits or backend-grounded plan/review claims, identify the backend that actually serves or owns the frontend contract:
   - inspect the frontend API config/host/port;
   - inspect running containers and their source mounts when a live service exists;
   - confirm the route/model/producer files in the target repo, not just any similarly named checkout;
   - when the user explicitly names a repo, treat that path as authoritative and re-audit there even if another repo has plausible code.
2. Compare the live/authoritative backend path with the task's planned backend path.
3. If they differ:
   - record the mismatch in task notes;
   - stop before editing the different live repo/path unless the user explicitly approves switching target repos;
   - do not claim live smoke coverage for backend behavior from edits made in the non-live checkout.
4. Use read-only container inspection to gather evidence when the host path is not mounted into the Hermes workspace.
5. If the user later approves the live path, restart/reload only the relevant service after confirming no unrelated long-running work is in progress.

## Evidence to capture in task notes

- Planned repo/path and branch.
- User- or config-confirmed authoritative repo/path when different from the initially inspected path.
- Running service/container name and API port when applicable.
- Container mount mapping, e.g. `host/path -> /app/apps/api`, when applicable.
- Route/model/producer files inspected in the authoritative repo.
- Any stale or superseded review artifacts caused by wrong-path evidence.
- A direct probe showing the live service behavior before/after implementation when smoke coverage is claimed.

## Pitfall

Do not turn this into a durable claim that one specific path is always the backend. The durable rule is the gate: verify the live service mount for the current session before editing or claiming smoke coverage.
