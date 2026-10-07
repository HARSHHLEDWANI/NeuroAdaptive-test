# Implementation gaps

Baseline: code inspected on `develop`, 2026-10-07. No app, tests, build, lint,
provider checks, or learner study executed here. Existing documentation was not read.
“Present” means code exists, not that runtime behavior is proven.

Paths below are relative to repository root.

| Area | Present / code evidence | Required change |
| --- | --- | --- |
| Identity/dashboard | `frontend/auth.ts`; `frontend/app/(pages)/dashboard/page.tsx` | Retain Google flow; unify actions with saved learning state |
| Setup/processing | `backend/app/modules/documents/service.py`; `jobs/service.py`; frontend `courses/[courseId]/workspace/page.tsx` | Reuse pipeline; define safe replacement when finalized sources fail |
| Review/publish | `curriculum/router.py` supports lesson renames and publication | Add module rename; optional grounded prerequisite warnings |
| Subjects/links | Inspected `courses/models.py` has no subject/link fields | New ownership-scoped relationships and matching/evidence policy |
| Curriculum | `curriculum/service.py` extracts concepts, builds/validates versions, creates blueprints | Reuse; blueprints are not generated lesson assessments |
| Diagnostic | `mastery/service.py`, `diagnostic.py`; assessment page | Persist resumable sets; support skip/retry; small graphs may yield fewer questions than the PDF's stated minimum |
| Lesson assessment | Assessment page explicitly rejects standard lesson mode | Add activity-scoped generation, question sets, feedback, resume |
| Grading/evidence | `mastery/grading.py`, `models.py`, `service.py` support grading and evidence | Durable pending grading; attempt deduplication; delayed-feedback contract; rubric results/reporting |
| Mastery | `mastery/engine.py` computes weighted prior/uncertainty/decay | Agree policies; expose honest bands/evidence strength; no calibration claim |
| Selection | `adaptation/service.py`, `scoring.py`, `policy.py` rank and persist decisions | Durable unfinished-activity priority; unknown/weak distinction; eligibility rules |
| Activity navigation | `frontend/lib/learning-route.ts` resolves all activity types to lesson links | Distinct experiences; preserve decision ID and selected format |
| Teaching/tutor | `tutor/service.py`; study/tutor/source pages | Consistent teaching structure; contextual side panels; assessment restriction |
| Presentation | Study page sends learner-button success before assessment | Replace learning-effectiveness signal with attributed graded outcomes |
| Progress/resume | Evidence/decision records exist; inspected models lack explicit assessment-set/activity progress lifecycle | Durable reading position, fixed questions, coverage, completion |
| Account controls | `identity/router.py`, `privacy/service.py`; existing profile UI | Wire product settings; review deletion/retention for every new entity |
| Legacy experience | `chat/router.py`, `content/router.py`, profile use learning-style data | Decide navigation placement; don't present it as the new course adaptation |

Module paths without full prefixes above refer to `backend/app/modules/`.

## PDF mismatches relevant to this plan

- PDF claims a complete repeated assessment loop; lesson assessments remain missing.
- PDF describes whole-response abstention on any citation failure; tutor code retries,
  strips failed claims, and may retain surviving content. Safeguard choice is still open.
- PDF remediation bonus differs from code; neither value is empirically validated.
- PDF describes forced exploration of every format; code periodically chooses a runner-up.
- PDF's reported test/live/injection results have not been reproduced on this checkout.
- PDF limits study files to two; inspected upload service allows five. Upload policy needs
  an explicit decision, not silent adoption of either number.

## Contract/dependency warning

Activity lifecycle, assessment sets, subjects/links, rubric feedback, and grading reports
may need schema/API changes. Design contracts and migrations before consumers; regenerate
OpenAPI-derived frontend types. Existing safeguards must be reviewed for new paths,
especially cross-course retrieval and pending grading. No infrastructure change is chosen here.

