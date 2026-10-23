# NeuroLearn — Neuro Adaptive AI Assistant

NeuroLearn turns a learner's own source material into an adaptive learning loop:

```
DOCUMENT → CONCEPTS → COURSE → ASSESS → MASTERY → ADAPT → TEACH → ASSESS AGAIN
```

Upload documents, get a generated concept graph and course, study lessons and
ask a source-grounded tutor, take diagnostic questions, and have the next
activity chosen from per-concept mastery. Every adaptive decision is logged with
its reason before it is served.

> **Status honesty.** Heuristic weights (mastery prior, adaptation scoring, FSLSM
> deltas) are hand-chosen, configurable defaults. They are **not** empirically
> validated. See [docs/SECURITY.md](docs/SECURITY.md) for what has and has not
> been tested, and [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for the
> as-built description.

## Documentation map

| File | Read it for |
|---|---|
| [AGENTS.md](AGENTS.md) | Operating contract for AI agents. Wins on conflict. |
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | Architecture of record: what is built, what is planned, known issues, invariants. |
| [architecture.md](architecture.md) | **Target** architecture (Supabase, Celery, Neo4j, Judge0, Railway). Not what runs today — see the deviations table in SYSTEM_ARCHITECTURE §5. |
| [frozen-scope.md](frozen-scope.md) | P0 scope, supported inputs, evaluation claims. |
| [implementation-plan.md](implementation-plan.md) | Task plan and ownership. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Branches, commits, PRs, test layers. |
| [SPRINT_LOG.md](SPRINT_LOG.md) | Dated engineering log per phase, including live-verification notes. |
| [docs/SECURITY.md](docs/SECURITY.md) | Threat-class coverage and residual risk. |
| [docs/adaptation-spec.md](docs/adaptation-spec.md) | Adaptation engine specification. |
| [docs/neurolearn-implementation-status.md](docs/neurolearn-implementation-status.md) | Historical Phase 0 audit (2026-08-26). Superseded; kept as a baseline. |

## What runs today

- **Web:** Next.js 16 (App Router, React 19, Tailwind 4), NextAuth 5 with Google
  sign-in. Pages: `/signin`, `/dashboard`, `/profile`, `/courses/new`, and per
  course `workspace`, `study/[lessonId]`, `tutor`, `assessment`,
  `sources/[chunkId]`. Server route handlers hold the internal token; the
  browser never sees it.
- **API:** FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic on PostgreSQL 16, under
  `/api/v1`. Domain modules in `backend/app/modules/`: `auth`, `courses`,
  `documents`, `jobs`, `retrieval`, `curriculum`, `assessment`, `mastery`,
  `adaptation`, `tutor`, `evaluation`, `privacy`, `audit`, `abuse`, `events`,
  `profile`, `chat`, `content`, `identity`.
- **Processing:** document ingestion and curriculum generation run as in-process
  FastAPI background tasks (no Celery/Redis worker yet). Jobs left RUNNING by a
  crashed process are marked FAILED on startup.
- **AI providers:** Gemini for generation and embeddings, behind gateway
  interfaces (`backend/app/services/generation`, `.../embedding`) with fake
  implementations for tests. Groq serves the legacy chat path.
- **Vectors:** Qdrant (compose service), behind `backend/app/services/vectorstore`.
- **Storage:** uploaded originals on the backend's local volume, served only
  through an authenticated, owner-checked endpoint.

Anything in `architecture.md` not listed above (Supabase, Celery/Upstash,
Neo4j, Judge0, Railway/Vercel deployment) is **target design, not implemented**.

## Prerequisites

- Docker + Docker Compose (recommended path), **or**
- Python 3.11, Node.js 20+, PostgreSQL 16, and a Qdrant instance for running
  services natively.
- A Google OAuth client (sign-in), a Gemini API key, and a Groq API key.

## Quick start (Docker Compose)

1. **Backend env.** Copy `backend/.env.example` to `backend/.env` and fill it in.
   `SECRET_KEY` and `INTERNAL_API_KEY` are **required** — there are no defaults,
   each must be ≥ 32 characters, and known placeholders are rejected at startup.
   Generate with:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   `INTERNAL_API_KEY` must match the frontend value exactly.

2. **Frontend env.** Copy `frontend/.env.example` to `frontend/.env.local` and
   fill it in (`NEXTAUTH_SECRET`, Google client id/secret, `INTERNAL_API_KEY`).
   Never give a secret a `NEXT_PUBLIC_` prefix.

3. **Google OAuth redirect.** Add
   `http://localhost:3001/api/auth/callback/google` (Compose) and/or
   `http://localhost:3000/api/auth/callback/google` (native dev) to the
   client's authorized redirect URIs.

4. **Start.**
   ```bash
   docker compose up --build
   ```
   | Service | Host port | Notes |
   |---|---|---|
   | Frontend | 3001 | |
   | Backend API | 8001 | OpenAPI docs at `/docs`. Runs `alembic upgrade head` on start. |
   | PostgreSQL | 5433 | Container-internal `db:5432`. |
   | Qdrant | 6333 / 6334 | |

   After editing `backend/.env`, recreate the container
   (`docker compose up -d --force-recreate backend`); `restart` does **not**
   re-read `env_file`.

## Native development

```bash
# Backend (from backend/)
pip install -r requirements.txt -r requirements-dev.txt
# set DATABASE_URL and QDRANT_URL=http://localhost:6333 in backend/.env
python -m alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (from frontend/)
npm install
npm run dev          # http://localhost:3000
```

Schema changes are Alembic migrations only; `create_all` is never used.

## Tests and checks

```bash
cd backend && python -m pytest        # unit, service, API, security, evaluation layers
cd frontend && npm run lint
```

Backend tests use deterministic fake Gemini gateways and an isolated database,
so they spend no provider quota. The frontend has no test runner yet. The last
suite count recorded in [SPRINT_LOG.md](SPRINT_LOG.md) is 363 passing; run the
suite to get the current number. Test layers are defined in
[CONTRIBUTING.md](CONTRIBUTING.md).

## Model configuration

Provider models are settings, not literals: `GEMINI_GENERATION_MODEL`,
`GEMINI_EMBEDDING_MODEL`, `GROQ_MODEL`. Providers retire models without notice
(both `gemini-2.5-flash-lite` and a Groq model have already been retired); a
retirement should be a config change. The API error normally names the
replacement.

## Security basics

- Identity comes only from server-side authentication via
  `app.core.security.get_current_user`, never from client input.
- Resources the caller does not own return 404, not 403.
- Uploaded and retrieved text is untrusted data, delimited in every prompt.
- No malware scanning exists. See [docs/SECURITY.md](docs/SECURITY.md).

## Contributing

Branch from the integration branch as `feature|fix|chore|refactor/<slug>`, one
concern per branch, imperative commit messages. Read
[CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) first.
