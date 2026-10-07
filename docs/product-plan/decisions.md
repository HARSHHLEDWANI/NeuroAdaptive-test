# Decisions and task summaries

This file records completed cleanup and preparation work for future reference. Product
direction and implementation gaps remain documented in [README.md](README.md) and
[implementation-gap.md](implementation-gap.md).

## P0 deployed foundation — repository configuration — 2026-10-07

**Implemented:** added production Railway API and worker entrypoints, Railway `PORT`
binding, health-check/deploy instructions, bounded Celery task limits, and private
Supabase S3-compatible upload handling with streamed SHA-256 verification. Local Compose
continues to override the API command for development. Vercel uses its native Next.js
build from `frontend/`; provider-specific projects and values are not in the repository.

**Inspected:** Alembic remains the schema authority; the chain has one head and its
historical populated-legacy-table guard remains active. Jobs use PostgreSQL leases and
heartbeats, late acknowledgment, durable stages, and explicit learner retry after dispatch
failure or interruption. This is user-triggered retry, not demonstrated automatic recovery.

**Not executed:** no provider project was linked and Docker was unavailable. No migration,
deployment, OAuth flow, storage operation, or live queue job was run. No production URL is
known. See [implementation-gap.md](implementation-gap.md) for environment placement,
remaining setup, and verification status.

**Official references reviewed:** [Railway deployment configuration](https://docs.railway.com/deployments/pre-deploy-command),
[Railway Redis](https://docs.railway.com/databases/redis), [Railway private networking](https://docs.railway.com/networking/private-networking),
[Supabase PostgreSQL connections](https://supabase.com/docs/guides/database/connecting-to-postgres),
[Supabase pgvector](https://supabase.com/docs/guides/database/extensions/pgvector),
[Supabase S3 compatibility](https://supabase.com/docs/guides/storage/s3/compatibility),
[Supabase S3 authentication](https://supabase.com/docs/guides/storage/s3/authentication),
[Vercel Next.js builds](https://vercel.com/docs/builds/configure-a-build), and
[Google OAuth web-server flow](https://developers.google.com/identity/protocols/oauth2/web-server).

## Pre-P0 frontend cleanup — 2026-10-07

**Code inspection:** Removed the unused adaptive/tracking chain (`AdaptiveContent`,
`CalibrationQuiz`, `TrackedImage`, `TrackedParagraph`, `TrackedCodeBlock`, and
`useTrackVisibility`): references were limited to imports inside that chain, with no
course-page, route, dynamic-import, or test consumer. Removed the profile page and its
actions because `/profile` is intentionally redirected and the actions had no other
consumer. Removed the chat/history and quiz API handlers because `proxy.ts` returns 404
for those paths. The legacy page redirects and API 404 guards remain; the `/api/v1`
catch-all still rejects `chat`, `profile`, and `assessment` roots through
`isBrowserApiPath`, which the existing frontend test covers. No current course flow
consumer was found.

**Retained dependencies:** Backend profile/chat/content/assessment implementations and
generated API types remain. Authentication still creates `UserProfile`, and backend
profile/content/chat, privacy cleanup, model registration, and tests still depend on
legacy profile models or routes. `MasteryMap`, shared telemetry/auth helpers, provider
adapters/fakes, and evaluation infrastructure remain for future work.

**Executed checks:** Frontend tests passed (6/6), lint passed, typecheck passed, and
production build passed with dummy local backend/auth values. Typecheck required removing
a stale ignored `.next/dev/types/validator.ts` left from the pre-cleanup route tree.
`git diff --check` passed after final diff review.
