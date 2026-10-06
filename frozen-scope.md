# NeuroLearn — Revised v1 Scope

Accepted by the project owner on 2026-10-06. This replaces the broad seven-day prototype scope; AGENTS.md governs implementation. SYSTEM_ARCHITECTURE.md distinguishes code present from executed verification.

## Product
An undergraduate CS learner uploads their own notes, reviews a generated course, studies a system-selected activity, answers a checkpoint, and receives an inspectable recommendation from concept evidence. Source content is data, never instructions. No learning-style label drives adaptation.

## Intended learner flow
Google sign-in → course goal/confidence → notes and optional syllabus → asynchronous processing → review/correct outline and prerequisite links → publish → optional diagnostic → grounded lesson and course-scoped tutor → one-shot MCQ/short answer → mastery/uncertainty → deterministic next activity and short evidence-based reason → progress.

A missing syllabus uses detected structure or an inferred outline, labeled as inferred; it does not establish external syllabus completeness. Unsupported topics are visible gaps, not filled from general model knowledge. Learners may switch presentation formats and rate usefulness, but cannot choose another next activity. Progress describes concept evidence and source coverage, never a predicted exam result.

## Inputs and limits
Native-text PDF, TXT, Markdown; optional one syllabus plus up to five study files. Retain 25 MB/file and 200 pages/course as intended limits; any implementation discrepancy is tracked. Scanned PDFs must request readable sources, not silently succeed. Sources become immutable at processing finalization.

## State and reliability
PostgreSQL is authoritative for courses, concepts, edges, mastery, questions, decisions and outcomes. pgvector stores chunk embeddings. Celery/Redis dispatches processing. Private originals use storage adapters; local development may use private disk storage. Jobs/stages are durable and idempotent. Only validated, nonempty course versions are reviewable/publishable. A provider failure pauses for manual retry, without fallback.

## Learning defaults and known conflicts
One attempt, no hints/retries; binary mastery evidence; LLM-estimated difficulty is unvalidated. Intended completion threshold is mastery >= 0.80 and uncertainty <= 0.30. No forgetting decay, schedules, exam dates or spaced review. Existing hint/retry/decay factors, numeric/partial grading, thresholds and candidate gating disagree with this target: record them, repair in subsequent product work rather than silently changing the math during the baseline.

## Baseline boundary
B00–B07 establish reproducible setup, preservation, migrations, worker ownership, security boundaries, generated API types and verified existing course seams. Lesson-specific assessments, complete grounding redesign, mastery/sequencing alignment, graph editing and visual redesign are later work. Baseline completion does not establish a complete adaptive loop or pilot readiness.

## Evaluation target (later)
Two unseen native-text sets complete the full loop. Technical baselines compare retrieval against vector-only search and simulated recommendations against fixed course order, without a claim of learning superiority. Recruit 10–15 consenting learners for two sessions across several days; report individual generated pre/post results and usability observations descriptively. No causal, population-level or pooled learning-gain claim. Freeze metrics before evaluation and label synthetic results.

## Deferred
Neo4j, Judge0/Python, numeric assessments, images/scans/OCR, DOCX/PPTX, general-knowledge tutoring, provider failover, mobile/offline, gamification and instructor authoring. Keep historical schemas/data; do not delete migrations or learner records to implement a scope cut.
