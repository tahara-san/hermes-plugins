# Buffdemy Notification Frontend Planning Notes

Use when planning `buffdemy2-web` notification UI work against the backend notification guide.

## Backend contract facts

- Backend persistence/summaries/outbox/RabbitMQ/consumer may exist before public REST routes do.
- Frontend v1 should treat these as dependencies unless the user explicitly expands scope to `buffdemy-backend` route implementation:
  - `GET /notification-summary`
  - `GET /notification-summary/unread-count`
  - `PUT /notification-summary/:notificationSummary/read`
  - `PUT /notification-summary/read-all`
- Prefer grouped notification summaries for v1, not individual chronological notification items.
- V1 should be REST-only unless the user explicitly changes scope. Do not plan WebSocket/SSE/push/realtime transport.
- Backend should provide render-ready `payload`, `lastDoerData`, and `target` fields to avoid client-side N+1 hydration. If not available, keep the feature flag disabled or degrade safely without broken links/crashes.

## Frontend planning checklist

- Add a strict feature flag; default disabled. For public client env vars, prefer literal parsing such as `NEXT_PUBLIC_NOTIFICATIONS_ENABLED === 'true'`.
- Specify disabled behavior for both the topbar entry point and direct `/notifications/` route. The disabled route must not call notification endpoints; render an unavailable state or redirect deliberately.
- Plan a dedicated notification adapter/model that owns endpoint paths so backend route changes stay isolated.
- Plan schemas/types for summary rows, unread count, mark-one-read, mark-all-read, and query params.
- If adding `notification.json` translation files, also plan registration in `src/i18n/translations/en/index.ts` and `src/i18n/translations/ja/index.ts`.
- For parallel UI/helper/hook work, create one shared typed mock fixture after the schema contract exists so workstreams do not invent divergent summary shapes.
- Because notification UI typically adds an App Router page plus client/server boundary integration, require `npm run build` in final verification, not just optional lint/unit checks.
