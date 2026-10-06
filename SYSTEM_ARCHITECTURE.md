# NeuroLearn — System Architecture

Scope revision accepted 2026-10-06. This describes the baseline in progress; docs/BASELINE_REPORT.md records executed checks.

## Status language
Implemented = code exists; Partial = code exists with gaps; Absent = no implementation; Unverified = behavior has not been executed in the reported environment. Numeric mastery/scoring defaults are unvalidated, even when tests pass.

## Current topology
Browser → Next.js/Google NextAuth → same-origin BFF → FastAPI → PostgreSQL/pgvector.
API → Redis/Celery → worker → private storage/text extraction/Gemini gateways → PostgreSQL.
The storage adapter supports S3-compatible Supabase private storage; compatibility must be tested separately from local disk. Neo4j and Judge0 are absent and deferred. Legacy Groq chat and learning-style tables remain historical state, isolated from learner navigation.

## Present capabilities and gaps
Course/source ownership, text extraction, chunk provenance, embeddings/retrieval, curriculum versions, diagnostic questions, mastery math, candidate scoring, tutor citations and decision/outcome models are present. Standard lesson assessments are absent. Source-only tutor validation is partial; source/page presentation and complete claim coverage need product work. Current mastery hints/retries/decay, numeric tolerance/partial scores and candidate filters conflict with revised scope. These are not calibrated educational measures.

## Data and processes
Domain modules remain under backend/app/modules. PostgreSQL owns product state and prerequisite edges. Alembic evolves schema; API, migrations and Celery use one model registry. Redis is coordination only. APIs authenticate trusted BFF identity, validate input, call services and translate errors. Course/owner predicates belong inside queries.

Processing jobs are committed before dispatch. Atomic course-level creation and worker leases/fencing prevent competing publication. Lease defaults (15-second heartbeat, 120-second expiry) are configurable, versioned and unvalidated. API restart never invalidates healthy workers. Dispatch/provider failures are durable and manually retryable; stale workers cannot write after ownership changes.

## Contracts and trust
FastAPI OpenAPI defines API responses and generated TypeScript types. Uploaded/retrieved text is untrusted data. Provider gateways own SDK calls. Logs contain identifiers, timing/counts and error categories, not prompts, documents, answers or signed URLs. Evaluator access defaults closed. Models/data required by historical relationships remain registered.

## Provider/configuration assumptions
Existing generation setting is gemini-3.5-flash-lite; embeddings gemini-embedding-001. The old code comment asserting universal retirement of 2.5 is not verified and is removed. This baseline does not claim model availability or substitute providers. Verify official model eligibility and configured account before live deployment; record the result here. No fallback provider is added.

## Target deployment
Vercel web; Railway API/worker; Supabase PostgreSQL/pgvector/private Storage; Upstash Redis. Google NextAuth/BFF identity remains the current implementation; Supabase Auth migration is deferred. Local Compose is the reproducible development topology. A hosted deployment/pilot is subsequent work.

## Invariants
No runtime fixture courses or fake AI. No schema evolution via create_all. No migration rewrites or user-data deletion. Publication follows validation. Owner isolation returns 404. Mastery and recommendations remain deterministic; decisions and subsequent outcomes stay separate. Unimplemented features remain visibly unavailable.
