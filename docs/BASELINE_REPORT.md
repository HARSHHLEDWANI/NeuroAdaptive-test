# NeuroLearn — Development Baseline Report

PHASE / TASK: B00–B07 development baseline
STATUS: complete (local integration checkpoint; no hosted deployment or pilot claim)
Date: 2026-10-06

## 1. Existing functionality discovered
Started from eedd2a4 on chore/baseline-stabilization plus 39 modified/deleted paths and untracked infrastructure/lifecycle work. Course upload/extraction/chunking, pgvector, curriculum versions, diagnostics, mastery/scoring, tutor citations and decision/outcome domains existed. Standard lesson assessment was explicitly unavailable. Original source was preserved in coherent snapshot commits ending at 9046dc8. Private uploads and local demo material remain outside commits.

## 2. Changes made
Ratified the focused v1 contract; archived the historical Phase 0 audit. Established npm and exact Python constraints, clean build contexts, safe templates and common server API origin. Compose starts migration once after database readiness and blocks API/worker on failure; web waits on API readiness. API startup no longer invalidates worker jobs. All processes register the same models.

Processing creation and claim are atomic. Lease defaults (heartbeat 15s/expiry 120s) are configurable, versioned, positive and unvalidated. Conditional transaction fencing rejects stale workers after takeover. Provider calls precede fenced artifact persistence. Course versions are keyed by job/retry epoch: interrupted DRAFT/READY artifacts are reused/revalidated, while explicit retry can regenerate a failed version without deleting its diagnostic artifact. Dispatch failure and lease expiry expose actionable manual retry. Bundled curriculum stages are explicitly SKIPPED; empty courses cannot publish. Section grouping and batching retain document separation.

Shared identity/security, evaluator allowlist and nested course/version/lesson/outcome scope are enforced. Browser proxy refuses identity synchronization and retired product domains. OAuth sync failure rejects the session and is visible on sign-in. Legacy pages and old chat/quiz browser APIs are hidden; historical FastAPI models/data remain. Provider constructors are centralized; malformed boolean/empty-claim responses fail closed; operational errors omit raw model/provider payloads. Unconfigured storage refuses ambient AWS credential discovery and returns an explicit 503, with local fallback only for that state. S3 HEAD checksum mode is covered by a stubbed adapter contract, not claimed live Supabase compatibility.

Typed OpenAPI responses and generated TypeScript replace active course payload duplicates. Read-only contract drift checks and required PostgreSQL/Redis checks are in CI. Historical destructive seed/reset utilities require an explicit disposable database; migration preflight blocks populated pre-2f legacy databases before historical table drops.

## 3. Files created/modified
Grouped areas: governing docs/history; dependency/config/Docker/CI; model registry and additive migrations; processing/curriculum; trusted BFF/auth/ownership/provider adapters; domain response schemas/OpenAPI/generated TS; active course/sign-in screens; tests and this report. Full path inventory is below. Redundant pnpm files and an unimported browser API helper were removed; runtime uploads, migrations and learner data were not removed.

## 4. Database/schema changes
Preserved pre-existing migration order: 9c4e2a7b1d65 (vectors) → 4d6a9f38e2b1 (lifecycle) → 6e3f8c29b4d7 (storage intents) → 7b2d9e4f1a63 (telemetry).
New forward migrations:
- 81a4c0d29f63: active-course unique constraint and worker lease/token/heartbeat fields.
- 82b5d1e30a74: durable curriculum job association.
- 83c6e2f41b85: explicit retry epoch and composite artifact uniqueness, retaining failed diagnostics.

29-file chain; head 83c6e2f41b85. Fresh and incremental upgrades executed only against disposable PostgreSQL/pgvector. Existing learner databases were not migrated. ORM comparison passes; the migration-owned HNSW expression index is explicitly excluded from automatic removal and its actual definition is asserted separately. Populated very old pre-2f databases fail safely and require an owner-approved preservation path. Existing competing active jobs would require reconciliation before the unique index can apply; migration does not rewrite them.

## 5. API changes
Existing paths/successful payloads retained. Added explicit response schemas for course, documents/intents, jobs, curriculum/graph/publication, recommendations, tutor stream/content and source retrieval. Job responses add retry_available and an authored interrupted-worker reason. Unconfigured private storage returns a safe RFC7807 503. Evaluator administration defaults closed (server email allowlist); learners can still read their own assigned condition. Wrong nested resources return 404. No learning feature endpoint was added.

## 6. UI changes
Generated API types are consumed by course/dashboard/assessment/source/lesson/tutor screens. Reload/polling supports interrupted-worker retry and cleans up intervals. Local uploads fall back only when private storage is explicitly unconfigured. Sign-in errors are visible. Retired profile/chat/quiz/reader/mission pages redirect out of the course product. Browser API routes cannot mint backend identities or invoke retired product endpoints. Visual redesign remains subsequent work.

## 7. Tests added/updated
Unit/adapter: strict boolean and answer parsing; private-storage checksum contract; no ambient credentials. API: immutable source/role caps and dedup distinction, empty-course rejection, dispatch failure, healthy startup preservation, expired retry, explicit failed-artifact regeneration, evaluator closure, wrong course/version/lesson/outcome paths. Real-service integration: PostgreSQL metadata/indexes, fresh and incremental migrations preserving existing rows, historical destructive-upgrade blocking, simultaneous starts, duplicate deliveries, embedding/edge-provider takeover fencing, DRAFT/READY crash recovery, actual Redis/Celery task delivery, and HTTP upload → review → publish → grounded lesson/source using real PostgreSQL with provider stubs. Web: Node 20-compatible tests for route mapping, API origin, trusted identity and browser path restrictions.

## 8. Commands run
- Isolated image builds: docker build --target test for backend; fresh frontend Docker build; npm ci in frontend image.
- Backend: pip check; ruff check --no-cache .; python -m pytest -p no:cacheprovider --tb=short with REQUIRE_INTEGRATION=1, disposable PGVECTOR_TEST_DATABASE_URL and REDIS_TEST_URL.
- Migrations: alembic upgrade head; incremental f7b3d29e1c64 → head; alembic check; historical ea9facb393a3 populated-table refusal.
- Contracts: scripts/export_openapi.py generation/--check; openapi-typescript generation/--check.
- Web: npm test; npm run typecheck; npm run lint on Node 20; npm run build on host and clean Node 20 Linux image.
- Isolated Compose project: up --build; health/OpenAPI/auth/course/upload/worker-pause/reload HTTP smoke; Next sign-in/error/BFF/legacy-redirect HTTP checks.
- Git: explicit snapshot commits, diff --check, fetch origin, normal local develop integration. No push or history rewrite.

## 9. Executed results
- Backend: **635 passed, zero failed, zero skipped**. One upstream Starlette/AnyIO deprecation warning remains; it is not suppressed or represented as a product defect fix.
- Python dependency consistency and bounded Ruff lint: passed. Broad Python ORM type checking/format conversion is deferred; no claim that it ran.
- PostgreSQL migration/metadata/HNSW checks, concurrency/fencing/retry tests and real Redis/Celery delivery: passed.
- OpenAPI snapshot and TypeScript drift checks: passed.
- Frontend: **6 tests passed** on Node 20; lint and TypeScript passed. Production build passed both on host and clean Node 20 Linux Docker image.
- Compose: migration service completed before API/worker; database/Redis/API readiness worked. API health/database/OpenAPI returned 200, user sync 200, course/paste 201, process dispatch 202. Worker correctly paused at INDEXING with an authored EmbeddingError reason when Gemini was deliberately unconfigured; latest-job reload recovery passed.
- Next HTTP: sign-in 200 with visible error text; browser identity-sync route 404; forged identity headers without a session 401; legacy profile redirected 307.
- Diff whitespace check passed. Secrets/runtime data excluded by explicit staging and ignore/build rules.

Earlier verification failures were corrected before this final result: three existing cap/dedup/batching failures; test-container mount/auth setup mismatches; fixture assumptions about empty courses; migration index reflection; and newly exposed PostgreSQL parent/child flush ordering. No suite was weakened/skipped to obtain the result. Test runtimes are not product latency/load measurements.

## 10. Known limitations
The complete adaptive loop, lesson-specific assessments, mastery/grading/sequencing scope alignment, full claim coverage/semantic grounding, editable graphs and final UX remain next-phase work. Short answers/numeric legacy behavior, hint/retry/decay factors and thresholds still conflict with intended v1; this baseline does not silently change the math. The extractor retains its current 500-page/PDF bound, while target scope intends 200 pages/course; alignment is queued.

Live Gemini/Groq quality/eligibility, real Google OAuth round-trip, Supabase Storage compatibility, Upstash TLS behavior, hosted deployment, load/accessibility/security penetration tests and real learner pilot were not executed. Provider tests use stubs; normal runtime factories use real adapters, never fixture AI. HTTP smoke used synthetic accounts/sources and test-only credentials. Historical FastAPI legacy endpoints/models remain for compatibility; browser access is isolated.

npm installation reported 21 dependency advisories in the host dependency tree. Runtime/provider/security patch upgrades require their own verified changes before a hosted pilot; no force upgrade was used. Python 3.11 and Node 20 are the preserved baseline runtimes, not a claim of current lifecycle suitability. GitHub Actions is configured but no hosted CI run or remote push was performed; recorded results are local CI-equivalent execution.

## 11. Downstream unblock
Develop has the reproducible baseline. Next implement source-grounded lesson assessments, then independent one-attempt evidence and policy alignment, full grounding/artifact caching, course-review improvements, academic UX/progress, deployment/privacy hardening and evaluation. Use the generated OpenAPI types; reuse domain services and job leases/artifact keys. Before pilot rollout, triage dependency/runtime advisories and verify real provider/auth/storage contracts.

## 12. Decisions requiring human approval
None outstanding for this authorized baseline. Deployment and pilot work remain separate tasks. Extremely old populated databases and any competing active jobs must be reconciled with their owner before migration; no such learner-state change was attempted.

## 13. Governing conflicts and handling
Scope/stack cuts were explicitly authorized in this chat and recorded in the governing documents first. Neo4j/Judge0/OCR/broad formats and Supabase Auth migration are deferred rather than claimed present. Old numerical/math differences remain documented subsequent work. Existing upload signature protection was retained through the accepted scope revision. Historical migrations were neither deleted nor rewritten. Required owner coordination is represented by this session's authorization across baseline areas; integration is local and normal, not a remote merge/publish.

Source mutation/finalization now share a refreshed course-row lock; a real concurrent HTTP regression verifies the source set cannot change after closure. Uvicorn access logs and Next development request logging are disabled so learner query strings are not recorded. Generation/token usage and SDK-internal retries remain partially uninstrumented; existing call counters must not be treated as complete billing measures.

Two independent read-only reviews checked standards and spec. They found explicit graph-version scope and artifact interruption/fencing gaps; these were repaired and covered by regressions. A later retry concern was resolved with job retry epochs while retaining failed diagnostic versions.

## Source path inventory for stabilization

- `.github/workflows/ci.yml`
- `.gitignore`
- `README.md`
- `SYSTEM_ARCHITECTURE.md`
- `backend/.dockerignore`
- `backend/.env.example`
- `backend/Dockerfile`
- `backend/alembic/env.py`
- `backend/alembic/versions/81a4c0d29f63_worker_leases.py`
- `backend/alembic/versions/82b5d1e30a74_curriculum_job_artifact.py`
- `backend/alembic/versions/83c6e2f41b85_curriculum_retry_epoch.py`
- `backend/app/core/config.py`
- `backend/app/core/disposable_tools.py`
- `backend/app/core/provider_errors.py`
- `backend/app/core/security.py`
- `backend/app/db/base.py`
- `backend/app/db/session.py`
- `backend/app/main.py`
- `backend/app/modules/adaptation/outcome_service.py`
- `backend/app/modules/adaptation/router.py`
- `backend/app/modules/adaptation/schemas.py`
- `backend/app/modules/auth/router.py`
- `backend/app/modules/chat/router.py`
- `backend/app/modules/courses/schemas.py`
- `backend/app/modules/curriculum/extraction.py`
- `backend/app/modules/curriculum/models.py`
- `backend/app/modules/curriculum/router.py`
- `backend/app/modules/curriculum/schemas.py`
- `backend/app/modules/curriculum/service.py`
- `backend/app/modules/curriculum/validation.py`
- `backend/app/modules/documents/chunk_models.py`
- `backend/app/modules/documents/router.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/storage.py`
- `backend/app/modules/evaluation/router.py`
- `backend/app/modules/jobs/models.py`
- `backend/app/modules/jobs/router.py`
- `backend/app/modules/jobs/schemas.py`
- `backend/app/modules/jobs/service.py`
- `backend/app/modules/mastery/diagnostic.py`
- `backend/app/modules/mastery/grading.py`
- `backend/app/modules/mastery/router.py`
- `backend/app/modules/profile/router.py`
- `backend/app/modules/profile/schemas.py`
- `backend/app/modules/retrieval/router.py`
- `backend/app/modules/retrieval/schemas.py`
- `backend/app/modules/tutor/entailment.py`
- `backend/app/modules/tutor/parsing.py`
- `backend/app/modules/tutor/router.py`
- `backend/app/modules/tutor/schemas.py`
- `backend/app/modules/tutor/service.py`
- `backend/app/services/adaptation.py`
- `backend/app/services/providers.py`
- `backend/constraints.txt`
- `backend/openapi.json`
- `backend/pytest.ini`
- `backend/requirements-dev.txt`
- `backend/requirements.txt`
- `backend/reset_table_profile.py`
- `backend/ruff.toml`
- `backend/scripts/export_openapi.py`
- `backend/seed_db.py`
- `backend/test_db.py`
- `backend/tests/api/test_adaptation_history.py`
- `backend/tests/api/test_baseline_boundaries.py`
- `backend/tests/api/test_evaluation_router.py`
- `backend/tests/api/test_ingestion.py`
- `backend/tests/api/test_retrieval.py`
- `backend/tests/conftest.py`
- `backend/tests/integration/test_baseline.py`
- `backend/tests/service/test_adaptation_outcomes.py`
- `backend/tests/service/test_curriculum_validation.py`
- `backend/tests/service/test_jobs_service.py`
- `backend/tests/service/test_pgvector_store.py`
- `backend/tests/unit/test_storage_contract.py`
- `backend/tests/unit/test_tutor_parsing.py`
- `backend/wait-for-db.sh`
- `docker-compose.yml`
- `frontend/.dockerignore`
- `frontend/.env.example`
- `frontend/Dockerfile`
- `frontend/README.md`
- `frontend/__tests__/backend.test.mjs`
- `frontend/__tests__/learning-route.test.mjs`
- `frontend/__tests__/load-ts.mjs`
- `frontend/app/(pages)/courses/[courseId]/assessment/page.tsx`
- `frontend/app/(pages)/courses/[courseId]/learn/page.tsx`
- `frontend/app/(pages)/courses/[courseId]/sources/[chunkId]/page.tsx`
- `frontend/app/(pages)/courses/[courseId]/study/[lessonId]/page.tsx`
- `frontend/app/(pages)/courses/[courseId]/tutor/page.tsx`
- `frontend/app/(pages)/courses/[courseId]/workspace/page.tsx`
- `frontend/app/(pages)/dashboard/page.tsx`
- `frontend/app/(pages)/signin/page.tsx`
- `frontend/app/actions/profile.ts`
- `frontend/app/api/chat/history/route.ts`
- `frontend/app/api/chat/route.ts`
- `frontend/app/api/events/route.ts`
- `frontend/app/api/quiz/route.ts`
- `frontend/app/api/v1/[...path]/route.ts`
- `frontend/auth.ts`
- `frontend/lib/api.ts`
- `frontend/lib/backend.ts`
- `frontend/lib/generated/api.ts`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/pnpm-lock.yaml`
- `frontend/pnpm-workspace.yaml`
- `frontend/proxy.ts`

Additional stabilization paths: backend/app/modules/courses/service.py, backend/main.py, frontend/next.config.ts, docs/BASELINE_REPORT.md, implementation-plan.md.
