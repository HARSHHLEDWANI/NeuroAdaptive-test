# NeuroLearn — Frontend

Next.js 16 (App Router, `--webpack` dev server), React 19, TypeScript, Tailwind 4,
NextAuth 5 (Google). Setup for the whole project is in the
[root README](../README.md).

## Run

```bash
cp .env.example .env.local   # fill in; see comments in the file
npm install
npm run dev                  # http://localhost:3000
npm run lint
npm run build
```

Under Docker Compose the app is served on `http://localhost:3001`.

## Structure

| Path | Purpose |
|---|---|
| `app/(pages)/` | Pages: `signin`, `dashboard`, `profile`, `courses/new`, `courses/[courseId]/{workspace,study/[lessonId],tutor,assessment,sources/[chunkId]}` |
| `app/api/` | Server route handlers (BFF): `auth`, `chat`, `events`, `quiz`, and `v1/[...path]` proxy to the FastAPI backend |
| `app/actions/` | Server actions |
| `auth.ts`, `proxy.ts` | NextAuth config; route protection (`/dashboard`, `/profile`, `/courses` require sign-in) |
| `lib/` | `api.ts` (backend client), `internal-auth.ts` (server-only internal token), `telemetry.ts` |
| `components/`, `hooks/` | Shared UI and hooks |

## Rules

- `INTERNAL_API_KEY` is server-only and must match the backend's. Never prefix a
  secret with `NEXT_PUBLIC_`; that inlines it into the browser bundle.
- The browser never calls the backend directly with credentials; calls go through
  route handlers or server components, which attach the internal token and the
  authenticated user's identity.
- There is no frontend test runner yet.
