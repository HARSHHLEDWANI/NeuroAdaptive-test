# Decisions and task summaries

This file records completed cleanup and preparation work for future reference. Product
direction and implementation gaps remain documented in [README.md](README.md) and
[implementation-gap.md](implementation-gap.md).

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
