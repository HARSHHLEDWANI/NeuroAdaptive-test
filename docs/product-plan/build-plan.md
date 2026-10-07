# Build plan

Ordered work packages, not authorization to start code changes. Reuse existing modules.
Resolve dependencies before beginning a package; architecture/safeguards remain separate.

## Before implementation

- Agree ownership, operating instructions, and architecture/safeguard decisions that block
  the selected package. Reconcile scope conflicts listed in [README.md](README.md).
- Inspect affected code/tests. Establish explicit activity, assessment, answer, grading,
  and completion contracts rather than treating a recommendation as progress.
- Every schema change needs a new Alembic migration. Update OpenAPI first and regenerate
  frontend types; avoid parallel handwritten response contracts.
- No new infrastructure/dependencies, migration deletion, data deletion, or history rewrite
  is implied by these tasks.

## Implementation order

| ID | Work package | Depends on | Demonstrated pass condition |
| --- | --- | --- | --- |
| P1 | Activity/assessment lifecycle and saved progress contracts | Policy review | States distinguish reading, submission, pending grading, graded assessment, mastery; reload returns same unfinished work |
| P2 | Grounded MCQ lesson assessment and reliable submission | P1; question policy | Unseen upload produces lesson and supported question set; submissions lock exactly once; restart resumes same questions; feedback withheld until set submitted |
| P3 | Results, evidence, progress, and next-activity integration | P2; mastery policy | Real graded answers update relevant concepts once; reading does not; results show changes; Continue uses recorded selection and saved progress |
| P4 | Remediation, targeted practice, and challenge experiences | P3; eligibility policy | Weak/mixed/strong evidence reaches the appropriate distinct activity; fresh questions; no unsupported prerequisite teaching |
| P5 | Short-answer grading and issue reporting | P2–P3; rubric/review policy | Rubric feedback has sources; failed grading remains pending; retries don't duplicate evidence; dispute saved with original judgment |
| P6 | Course overview and workspace integration | P3–P5 | Outline inspection cannot launch alternatives; tutor/sources open alongside teaching/results; tutor unavailable during assessment; format and position preserved |
| P7 | Setup/review/recovery and account UX | P1; replacement/retention policy | Module/lesson renames persist; diagnostic skip/retry works; failures recover without false completion; settings/reset/deletion handle new records |
| P8 | Subjects and explicitly linked earlier courses | P3; cross-course/matching policy | Unit 2 can use supported Unit 1 evidence/source links; uncertain match offers optional check; standalone path works; foreign courses inaccessible |
| P9 | Completion, full polish, and acceptance evidence | P4–P8; completion policy | Coverage differs from mastery; sufficient evidence leads to summary and optional guided practice; no unfinished advertised action |

Build MCQ end-to-end first, then add short answers and the full agreed scope. Intermediate
checkpoints are not product completion. Finalize layout/styling across screens after the
state contracts are stable; include responsive, empty, loading, and recovery states.

## Verification per package

| Layer | Highest useful seam |
| --- | --- |
| Unit | Selection/eligibility, mastery, evidence attribution, matching decisions |
| Contract | Provider schemas; assessment/results/progress APIs; generated frontend types |
| Integration | Owned REST flows; migrations; durable resume; duplicate submission/grading; approved linked retrieval |
| Pipeline | Deterministic provider fixtures; stage retries and invalid artifacts |
| Browser | Upload/review/diagnostic/study/assessment/results/resume/complete and failure recovery |

Run focused relevant checks, affected contracts/integration, format/lint/types, and build
where practical. Use provider adapters/stubs in automated tests; never spend quota
accidentally. Keep checks distinguishable as executed, inspection-only, or blocked.

## Final acceptance

- Two unseen native-text document sets complete repeated teaching → assessment → mastery
  → recommendation cycles through production paths, with recorded provenance/decisions.
- Demonstrate diagnostic skip, interruption/resume, weak-answer remediation, practice,
  challenge, pending grading, unsupported content, and optional completion practice.
- Demonstrate Unit 1 → Unit 2 linking separately, plus the standalone course path.
- Verify ownership and approved citation/safeguard behavior, including new paths.
- No fake runtime output, mastery, or traces; no learner-content/answer/secret leakage
  in logs or commits.
- Report actual commands/results, limitations, migrations, and unresolved decisions.
  Automated checks establish specified behavior, not learning gain.

If learner evaluation is pursued, define usability and educational measures separately.
Do not reuse the PDF's historical counts as current acceptance evidence.

