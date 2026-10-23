# SYSTEM_ARCHITECTURE.md

Architecture of record for NeuroLearn. Describes what exists today, what is
targeted, and the staged route between them. Section numbers are stable and are
referenced by `AGENTS.md` and by the phase pack — do not renumber.

Last verified against the codebase: **2026-10-24** (documentation pass by
inspection of the working tree; test suite not executed in that pass — the last
recorded count is in `SPRINT_LOG.md`). Sections 2, 4 (K-7, K-12, K-13), 5, 8, 15,
16 and 17 were rewritten in that pass to match the code; earlier text described
the pre-course-pipeline chat prototype.

> **Conflict with `AGENTS.md` §5 (flagged, not resolved).** AGENTS.md freezes the
> stack as Supabase/pgvector/Storage, Celery + Upstash Redis, Neo4j, Judge0,
> `gemini-2.5-flash-lite`, Docling/RapidOCR. The code differs; see the deviations
> table in §5. AGENTS.md wins until a human ratifies an architecture decision, so
> the deviations are recorded here as facts, not endorsed.

---

## 1. Purpose and scope

NeuroLearn ingests a learner's own source material, derives a concept graph and a
course from it, teaches through retrieval-grounded generation, assesses, tracks
per-concept mastery, and adapts what it serves next — recording why it made each
choice so the effect can later be measured.

This document covers the backend, frontend, data model, adaptation engine,
retrieval, security model, and local topology. It does not cover deployment
infrastructure, which does not yet exist.

## 2. System context

```
Learner
  → Web Client (Next.js, App Router)
  → BFF / API (FastAPI, /api/v1)
  → [ Ingestion | Concept Graph | Tutor/RAG | Assessment | Mastery/Adaptation ]
  → PostgreSQL (source of truth)
  + Document storage              ── BUILT (local volume, not object storage)
  + Vector index                  ── BUILT (Qdrant behind a store interface)
  + Job execution                 ── PARTIAL (in-process background tasks; no Redis/worker)
  + LLM provider (vendor-abstracted) ── BUILT (Gemini gateways + fakes; Groq legacy chat)
```

## 3. Status legend

Every capability claim in this document carries one of these labels. Use them
consistently; an unlabelled claim is a defect.

| Label | Meaning |
|---|---|
| **BUILT** | Implemented, exercised, and behaving as described. |
| **PARTIAL** | Implemented but incomplete, unhardened, or only working on a happy path. |
| **BROKEN** | Present in the codebase but does not work as written. |
| **PLANNED** | Designed here; no implementation exists. |
| **UNVALIDATED** | Implemented, but its numeric parameters are hand-chosen and have never been tested against outcomes. |

## 4. Known issues

Verified by direct inspection on 2026-08-26. Each carries the stage that closes it.

### Open

| # | Issue | Severity | Evidence | Closes in |
|---|---|---|---|---|
| K-4 | Authorization is header-trust: `x-user-email` plus one shared static token *is* the entire scheme. Anyone holding the token can impersonate any user by changing a header. Acceptable only while the BFF is the sole caller. | **High** | all routers | Stage 4 |
| K-7 | Partly closed. Vector index exists (Qdrant, in Compose). Still absent: queue/worker (pipeline runs as in-process FastAPI background tasks, so work dies with the process; startup marks orphaned jobs FAILED) and object storage (originals on a local volume). `boto3` and `minio` remain declared and imported nowhere. | Medium | `docker-compose.yml`, `jobs/router.py` | Stage 4 |
| K-11 | Decided 2026-08-27: new tables use UUID, the existing seven keep integer keys. `learning_events` and `quiz_attempts` follow this. Remaining work is only to apply it consistently as Stage 2 adds tables. | Low | `§8` | Stage 2 |
| K-12 | Mostly addressed. Generation and embeddings go through `GenerationGateway` / `EmbeddingGateway` (Gemini + fakes); model ids are settings (`GEMINI_*`, `GROQ_MODEL`). Still outstanding: the legacy chat path (`chat/router.py`, `services/adaptation.py`) calls Groq directly rather than through a gateway, and no call records provider, model, prompt version, tokens or latency (`AIUsageDaily` counts calls only). | Medium | `chat/router.py`, `services/adaptation.py` | Stage 4 |
| K-13 | Partly closed for course documents: uploads have a 25 MB cap, extension allowlist, magic-byte check, 500-page cap, encrypted-PDF detection, and are persisted (`documents` module, `docs/SECURITY.md` T2). Still open: the legacy chat attachment path parses PDFs inline in the request and discards them; no malware scanning anywhere. | Medium | `chat/router.py`, `documents/service.py` | Stage 4 |

### Closed

| # | Issue | Closed |
|---|---|---|
| K-10 | Both learner-evidence paths discarded their data: telemetry posted to a nonexistent `/profile/pulse` while logging success on the 404, and quiz results never left `sessionStorage`. Now persisted to `learning_events` and `quiz_attempts` through authenticated server route handlers, with server-side grading. | 2026-08-28 |
| K-1 | `SECRET_KEY` and `INTERNAL_API_KEY` shipped working fallback defaults (`"dev_secret_key_123"`, `"CHANGE_ME_..."`), repeated in `auth.ts` and `app/actions/profile.ts`. Both sides failed **open** to a value in the git history. Now required, with a validator rejecting known placeholders and anything under 32 chars. | 2026-08-27 |
| K-2 | `NEXT_PUBLIC_INTERNAL_API_KEY` was defined in `frontend/.env.local`. It was referenced by zero code paths, so Next.js never inlined it and it never actually leaked — but the prefix invited it. Removed. | 2026-08-27 |
| K-3 | `Base.metadata.create_all(bind=engine)` ran on every startup alongside a healthy 5-revision Alembic chain. Removed; `wait-for-db.sh` already ran `alembic upgrade head`. | 2026-08-27 |
| K-5 | Three mutually incompatible archetype vocabularies coexisted. `core/archetypes.py` (6 labels) had zero importers; `modules/profiling/router.py` (4 labels, two unique) was never registered. Both deleted; `profiling/models.py` retained. | 2026-08-27 |
| K-8 | `backend/requirements.txt` was UTF-16LE with mixed CRLF/LF. Converted to UTF-8; package set unchanged. | 2026-08-27 |
| K-6 | No test tooling existed in either manifest. pytest added with 92 executed tests across a unit and an API layer, including regression coverage for K-1 and K-9. Frontend still has no runner. | 2026-08-28 |
| K-14 | The app could not be imported without a live Groq key: the client was built at module scope, and via `os.getenv`, which never read `backend/.env`. Now lazy and settings-backed. | 2026-08-28 |
| K-9 | `GET /api/v1/content/articles/{id}` accepted a caller-supplied `user_id` defaulting to `1` with no auth dependency, and passed a `str` where a `dict` was required — a guaranteed `AttributeError`. | 2026-08-26 |

## 5. Current architecture — as built

Verified by inspection of the working tree on 2026-10-24. "BUILT" means code and
tests exist; it does not mean empirically validated (see UNVALIDATED).

**Frontend** — Next.js 16.1.6, React 19.2.3, TypeScript, App Router, Tailwind 4,
NextAuth 5 (beta, Google), Recharts, Framer Motion. Pages under `app/(pages)/`:
`signin`, `dashboard`, `profile`, `courses/new`, and per course `workspace`,
`study/[lessonId]`, `tutor`, `assessment`, `sources/[chunkId]`. Route handlers
under `app/api/` (`auth`, `chat`, `events`, `quiz`, `v1/[...path]` proxy) hold
the internal token; the browser never sees it. No frontend test runner.

**Backend** — FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic on PostgreSQL 16.
Seventeen routers registered in `app/main.py`: `auth`, `content`, `profile`,
`chat`, `events`, `assessment`, `retrieval`, `curriculum`, `courses`, `identity`
(+ health), `documents`, `jobs`, `mastery`, `adaptation`, `tutor`, `evaluation`.
Alembic head: `f7b3d29e1c64` (linear chain, 22 revisions).

| Capability | Status |
|---|---|
| Google OAuth → `POST /auth/sync` → User + UserProfile | **BUILT** |
| Courses CRUD, owner-scoped (`courses`) | **BUILT** |
| Document upload / paste, validation, owner-only download (`documents`) | **BUILT** (PDF/text; DOCX/PPTX rejected; no malware scan) |
| Chunking with provenance + embeddings → Qdrant (`retrieval`) | **BUILT** |
| Processing jobs: stages, retry, latest-job recovery, paused-reason (`jobs`) | **PARTIAL** — in-process background tasks, no durable queue |
| Concept extraction, prerequisite edges, modules/lessons, validation, publish (`curriculum`) | **BUILT** |
| Grounded tutor and lesson content with two-tier citation validation (`tutor`) | **BUILT** — tier-2 entailment is sampled |
| Diagnostic questions, server-side grading, mastery report (`mastery`) | **BUILT / UNVALIDATED** (hand-chosen constants, §10) |
| Next-activity scoring, presentation affinity, decision/outcome logging (`adaptation`) | **BUILT / UNVALIDATED** |
| Experiments, conditions, cohort assignment, metrics export (`evaluation`) | **BUILT** — no real study data exists |
| Consent, account deletion, audit log, abuse limits (`privacy`, `audit`, `abuse`) | **BUILT** — rate limits are in-process (single replica) |
| FSLSM continuous vector profile (4 dims, clamped nudges) | **BUILT / UNVALIDATED** |
| Legacy chat (Groq), keyword signal inference, calibration quiz | **PARTIAL / UNVALIDATED** |
| Learner telemetry → `learning_events`; quiz attempts → `quiz_attempts` | **BUILT** |

### Deviations from the AGENTS.md §5 frozen stack

| Frozen choice | Actual | Note |
|---|---|---|
| Supabase PostgreSQL/pgvector, Auth, Storage | Plain PostgreSQL 16 (Compose); NextAuth Google + internal token; local-volume storage | Vectors live in Qdrant, not pgvector |
| Celery + Upstash Redis | FastAPI `BackgroundTasks`, in-process | Work is lost if the process dies; orphaned jobs reclaimed on startup |
| Neo4j AuraDB projection | None; graph read from PostgreSQL (`GET /courses/{id}/graph`) | |
| Docling + RapidOCR, Gemini fallback | `pypdf` text extraction (500-page cap) | No OCR; scanned PDFs unsupported |
| `gemini-2.5-flash-lite` | `gemini-3.5-flash-lite` (default), via `google-generativeai` | Original retired for new callers; model id is a setting |
| Judge0 Python execution | None | Python-code assessment not built |
| React Flow, TanStack Query, shadcn/ui | Not in `package.json` | |
| Vercel / Railway hosting | None; Docker Compose only | No deployment exists |

## 6. Target architecture

Nine responsibilities, each a module under `backend/app/modules/`:

1. **Ingestion** — validate, store, extract, clean, chunk, embed, index.
2. **Concept graph** — extract concepts, infer prerequisites, link to sources.
3. **Curriculum** — generate versioned courses from the graph.
4. **Tutor** — retrieval-grounded generation with validated citations.
5. **Assessment** — generate and grade questions tied to concepts.
6. **Mastery** — weighted-evidence estimation per concept.
7. **Adaptation** — score candidate next activities; select presentation variant.
8. **Analytics** — decision/outcome pairing, learning-gain datasets.
9. **Admin** — jobs, usage, prompt registry.

## 7. Component responsibilities

The BFF owns session validation and never forwards raw browser input as identity.
FastAPI owns all authorization. Workers own everything slow: parsing, embedding,
generation. Postgres is the single source of truth; the vector index is a derived
cache and must be rebuildable from Postgres alone.

## 8. Data model

**Current (BUILT):** integer keys — `users`, `user_profiles`, `articles`,
`paragraphs`, `article_readings`, `chat_sessions`, `chat_messages`. UUID keys —
`learning_events`, `quiz_attempts`, `courses`, `documents`, `chunks`,
`processing_jobs`, `processing_stages`, `course_versions`, `concepts`,
`concept_sources`, `concept_prerequisites`, `modules`, `lessons`,
`lesson_concepts`, `assessment_blueprints`, `questions`, `question_concepts`,
`question_attempts`, `mastery_events`, `adaptation_decisions`,
`adaptation_outcomes`, `presentation_affinities`, `tutor_messages`,
`ai_usage_daily`, `audit_logs`, `experiments`, `experiment_conditions`,
`cohort_assignments`. Migration chain is linear and single-headed, ending at
`f7b3d29e1c64` (`ea9facb393a3` is the root).

**Not built from the earlier target list:** `AuthIdentity`, `UserPreference`,
`DocumentSection`, `LearningBlock`, `ContentVariant`, `Citation` (citations are
validated at answer time against `chunks`, not stored as rows), `Misconception`,
`UserMisconception`, `LearningSession`, `Conversation`. `ConceptMastery` is
derived from `mastery_events` rather than stored as a table.

**The single most important structural choice:** `AdaptationDecision` (what was
chosen and why, written *before* serving) is a separate table from
`AdaptationOutcome` (what actually happened, written later, linked back). This
split is what turns "the app felt adaptive" into a dataset that can be analysed.
Never merge them.

## 9. API conventions

`/api/v1`. JSON everywhere except uploads (direct-to-storage) and SSE streams.
UUID ids on new resources. Cursor pagination. RFC 7807 problem-details errors.
`Idempotency-Key` on retryable mutations. `If-Match` on versioned resources.
Ownership validated server-side on **every** path segment. 404 not 403.

## 10. Adaptation engine

Adaptation is driven by two continuously-updated quantities, never by a label:

- **Per-concept mastery**, from weighted evidence.
- **Per-variant presentation affinity**, from observed outcomes per format.

Mastery model (**UNVALIDATED** — hand-chosen constants):

```
mastery     = (S + m0 * k) / (W + k)        m0 = 0.3, k = 2
uncertainty = 1 / sqrt(1 + W)
```

where `S` is summed weighted successes and `W` is summed evidence weight. `m0`
and `k` are configurable, versioned defaults. They are not calibrated and no
claim of calibration may be made.

Every decision is explainable and logged **before** it is served, and carries a
human-readable reason.

## 11. Retrieval and grounding

The authorization filter is applied **inside** the retrieval query, never as a
post-filter over results. Citations are validated three ways — structural (the
chunk exists), ownership (the caller may read it), and semantic (it actually
supports the claim) — not merely rendered. Retrieved text is data.

## 12. Security model

Trust boundaries: browser → BFF → API → data. Uploaded documents are untrusted.
Retrieved text is untrusted and non-executable.

Current posture is **PARTIAL** and depends entirely on the BFF being the only
caller that holds the internal token (K-4). Per-user tokens replace this in
Stage 4.

## 13. Observability

**PLANNED.** Structured logs around ingestion, generation, retrieval, grading,
and adaptation. Every LLM call records provider, model, prompt version, token
counts, and latency.

## 14. Configuration and secrets

Environment variables only. `INTERNAL_API_KEY` and `SECRET_KEY` are required
and validated at startup; there is no fallback default, because one fails open.
No secret may carry a `NEXT_PUBLIC_` prefix. Templates live in
`backend/.env.example` and `frontend/.env.example`. `.env` and
`.env.local` are gitignored and have been verified untracked.

## 15. Local topology

Compose defines `db` (PostgreSQL 16, host port 5433), `qdrant` (6333/6334),
`backend` (host 8001; runs `alembic upgrade head` then `uvicorn --reload`) and
`frontend` (host 3001), plus volumes `postgres_data`, `qdrant_data` and
`uploaded_documents`. Planned and absent: `redis`, `worker`, object storage,
`neo4j`, Judge0.

## 16. Evolution plan

| Stage | Name | Exit condition |
|---|---|---|
| **0** | Docs and contracts | This file, `AGENTS.md`, `CONTRIBUTING.md` exist and are ratified. **Reached 2026-08-26.** |
| **1** | Foundation | K-1, K-2, K-3, K-5, K-6, K-8, K-10, K-14 closed. Redis and object storage not added. |
| **2** | Source → course slice | Upload → chunk → index → concepts → prerequisite graph → generated course, for one document. Worker pipeline real. |
| **3** | Adaptive loop | Diagnostic → mastery → next-activity scoring → presentation variant → `AdaptationDecision` persisted. RAG tutor with validated citations. |
| **4** | Production readiness | Per-user auth (K-4), full threat model, observability, `AdaptationOutcome` pairing, UI integration. |
| **5** | Evaluation | Experiment harness and fixtures. No fabricated results. |

## 17. Capability boundaries

NeuroLearn does **not** currently: run a durable queue/worker, OCR scanned
documents, execute learner Python code, project the graph to Neo4j, store
originals in object storage, or run in any deployed environment. It has not been
evaluated on learners: no learning-gain or quality figure exists, and none may be
claimed. Frozen simplifications in `AGENTS.md` §10 (single attempt, binary
evidence, no spaced review, etc.) apply.

The FSLSM vector engine is a **plausible heuristic with hand-chosen deltas**. It
has not been validated against learning outcomes and may not be described as
evidence-based. The broader Felder–Silverman model's predictive validity for
instructional adaptation is itself contested in the literature; §18.7 exists
because of that.

## 18. Non-negotiable invariants

1. **Postgres is the source of truth.** Every derived store is rebuildable from it.
2. **Authorization is server-side and per-resource**, applied on every path segment.
3. **Identity never comes from the client.** Not a query param, not an unvalidated body field.
4. **404, not 403,** for resources the caller does not own.
5. **Schema changes ship as Alembic migrations.** `create_all` is never the mechanism.
6. **Retrieved and uploaded text is data.** It never instructs, never invokes a tool.
7. **No fixed learning-style label drives adaptation.** Labels are onboarding flavor only.
8. **Every adaptive decision is logged with its reason before it is served.**
9. **`AdaptationDecision` and `AdaptationOutcome` remain separate tables.**
10. **No unvalidated claim is stated as fact** — in code, docs, commits, or reports.
