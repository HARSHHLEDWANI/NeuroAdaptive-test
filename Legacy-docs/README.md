# NeuroLearn

Undergraduate CS study from the learner's own notes. Revised v1 scope: frozen-scope.md; actual capabilities: SYSTEM_ARCHITECTURE.md; executed checks: docs/BASELINE_REPORT.md. Lesson-specific assessments and the full adaptive loop are subsequent work.

## Runtimes and configuration
Baseline runtimes: Python 3.11 and Node 20, matching Docker/CI. npm is the frontend package manager. Runtime/provider upgrades are separate verified tasks.

Copy backend/.env.example to backend/.env and frontend/.env.example to frontend/.env.local. Generate distinct SECRET_KEY/NEXTAUTH_SECRET and a shared INTERNAL_API_KEY using `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Fill the same Google OAuth credentials on the Next.js server. Required secrets have no default. Live Gemini is required for normal course generation, never fake runtime output. Storage credentials are optional locally; originals use private backend/var/uploads. Hosted storage requires private Supabase S3 configuration and separate verification.

## Docker development
`docker compose up --build` starts database, Redis, migrations, API, worker and web. Migrations run once and failure blocks API/worker startup. Web: http://localhost:3001; API: http://localhost:8001; PostgreSQL host port 5433, container port 5432. Register Google callback http://localhost:3001/api/auth/callback/google. Existing Compose project/volume identity must be preserved to retain database state. Do not run `down -v` on learner databases.

## Native development
1. `docker compose up -d db redis`
2. In backend: `python3.11 -m venv .venv`; activate it; `pip install -c constraints.txt -r requirements.txt -r requirements-dev.txt`.
3. Native database/Redis URLs use localhost as in the templates. Run `alembic upgrade head`; `uvicorn app.main:app --reload --no-access-log --port 8001`; in a separate shell run `celery -A app.core.celery_app.celery_app worker --loglevel=INFO --concurrency=2`.
4. In frontend: `npm ci`; `npm run dev`. Native web port is 3000; register http://localhost:3000/api/auth/callback/google. INTERNAL_API_URL=http://127.0.0.1:8001 on the Next.js server.

The tokenizer vocabulary is real, cached during the Docker build; native setup downloads it once with `python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"`. Installation may use network. Tests never substitute a tokenizer or spend AI quota.

## Checks
Backend: `python -m pytest`; `ruff check .`. Frontend: `npm test`; `npm run lint`; `npm run typecheck`; `npm run build`. PostgreSQL/Redis integration instructions and exact results live in docs/BASELINE_REPORT.md. Use disposable databases named neurolearn_test*, never product state.

Generate API types with frontend `npm run contracts:generate` after backend requirements are installed and safe configuration is supplied. CI checks schema/type drift. Expected configuration is documented in environment templates; secrets and runtime data are ignored by Git and Docker builds.

## Integration
Task branches use feat/<task-id>-<short-name>. develop is integration, main receives executed green checkpoints. Preserve migrations and learner data. Historical reset/seed tools require an explicit disposable database and opt-in; production generation does not call them.
