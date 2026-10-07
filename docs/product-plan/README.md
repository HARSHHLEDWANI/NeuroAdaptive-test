# NeuroLearn product plan

Status: agreed product direction, not a description of completed implementation.
Date: 2026-10-07. Code baseline inspected: `develop`; no application execution.

## Read in this order

| File | Use it to answer |
| --- | --- |
| [user-flows.md](user-flows.md) | What does the student do from arrival to completion? |
| [screens.md](screens.md) | What appears on each screen, and what actions are available? |
| [learning-rules.md](learning-rules.md) | How do teaching, assessment, mastery, and selection behave? |
| [implementation-gap.md](implementation-gap.md) | What can we reuse, and what is missing? |
| [build-plan.md](build-plan.md) | What should we implement first, and how do we demonstrate it? |

## Product commitment

Turn the student's own material into a reviewable course, grounded teaching,
assessment evidence, and a guided next activity. Finish repeated learning cycles
before expanding feature breadth. Show source support and uncertainty; do not
claim improved learning without a suitable study.

Agreed boundaries:

- Continue studying selects the activity; the outline is available to inspect.
- Diagnostic is optional. Reading completion is separate from understanding.
- MCQ and short answer are the planned assessment types.
- Published sources stay fixed. Subjects and links to earlier courses are optional.
- Missing prerequisite coverage warns, but does not block publication.
- Tutor and source viewer sit beside the activity; tutor help is unavailable during assessments.
- Completion separates lesson coverage from demonstrated understanding.
- Optional practice after completion is selected by the app.

## Deployment and preparation decisions

Selected target, not a verified deployment:

| Component | Target / role |
| --- | --- |
| Web | Next.js on Vercel |
| API | FastAPI on Railway |
| Workers | Celery on Railway; asynchronous processing, preparation, and grading |
| Queue coordination | Redis on Railway; Upstash is excluded |
| Product data | Supabase PostgreSQL with pgvector; authoritative progress/jobs/evidence |
| Original sources | Private Supabase Storage; owner-authorized access for API/workers |
| AI | Configurable Gemini generation and embeddings; no automatic provider fallback |

Prepare the first lesson and assessment as soon as required source/outline artifacts
are valid. Studying starts after outline publication and first-activity readiness;
it does not wait for all lessons or variants. Save validated content, reuse variants,
and progressively prepare likely next activities. Prioritize waiting students,
then first-course readiness, then speculative preparation. Background work must
leave capacity for interactive requests.

The speed goal is responsive deployed interactions, not an unmeasured latency
claim. Measure preparation, saved-content loading, tutor validation, and grading.
Demo both a real prepared course and a fresh upload through the production path.

## Safeguards agreed

- Teaching/answers use the current course and explicitly linked earlier courses only.
- Check source ownership/existence and semantic support for every factual claim.
  Remove unsupported claims; abstain if the remainder cannot answer adequately.
- Private storage requires server-side ownership checks; files are not public.
- Bounded preparation, retries, and AI allowances; saved content/progress remain
  accessible when generation pauses. Pending grading is not incorrect evidence.
- Required learning records are separate from optional interaction tracking.
- Authorized grading reviewers can correct judgments, preserving originals and
  recomputing affected evidence without counting another attempt.
- Before publication, replacement preserves valid files and rebuilds dependent
  artifacts. Published sources stay fixed.

## Decisions still open

| Decision | Must be settled before |
| --- | --- |
| Mastery bands, evidence-strength labels, completion criteria, and decay policy | Progress/selection acceptance |
| Question count, rubric scoring, difficulty, and fresh-question checks | Assessment release |
| Reliable cross-course concept matching and evidence reuse | Linked-course integration |
| Missing-prerequisite detection and supporting evidence for warnings | Prerequisite-warning release |
| Reviewer access, review operations, retention, and correction propagation | Report-grading-issue release |
| What ends an activity whose assessment stays unavailable | Full recovery acceptance |
| Preparation limits, AI budgets, job timeouts, fair capacity, and retry bounds | Worker/deployment acceptance |
| Provider eligibility, region/network configuration, and storage credentials | Hosted verification |
| Retention/deletion details and complete answer claim coverage | Safeguard acceptance |

Existing numeric constants are unvalidated defaults, not approved calibration.
Future tunable numbers need named, versioned, configurable policies.

## Scope and authority

This folder records approved product/architecture decisions, not authorization to
begin implementation or evidence that they exist. Operational rules for migrations,
contracts, ownership, and honest reporting still apply. Only this planning folder
was read during the update; historical Markdown was not consulted.

Explicit scope revisions: linked-course grounding/evidence, visible factual selection
reasons, replacement before publication, support checks for all factual claims, and
authorized grading review. Railway Redis replaces Upstash. These revisions supersede
earlier product descriptions where they conflict; revise contracts before implementing.
Evidence decay/completion interaction remains open. Prerequisite remediation is
app-selected work, not a publication block for missing source coverage.

