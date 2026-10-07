# User flows

Proposed lifecycle. Screen content lives in [screens.md](screens.md); learning
behavior lives in [learning-rules.md](learning-rules.md).

## First course

1. Sign in with Google; arrive at an empty dashboard.
2. Create a course: name, learning goal, sources. Optionally choose a subject and
   explicitly link an earlier course owned by the student.
3. Check files, then prepare the course. Processing is asynchronous; leaving is safe.
4. Review modules, lessons, objectives, and prerequisites. Rename modules/lessons.
   Missing prerequisite coverage is a warning; publishing remains optional and available
   if the course otherwise passes validation.
5. Publish. Sources become fixed for the published course.
6. Take the diagnostic or skip. Skipping leaves concepts Not assessed.
7. Reach course overview. Continue studying opens the selected activity.

## Repeated learning cycle

1. See the activity's purpose and a factual selection reason.
2. For new lessons/remediation, study with format switches, tutor, and citations.
   For practice/challenges, start questions without mandatory teaching first.
3. Ready for questions records reading completion, not mastery.
4. Answer one question at a time. Successful submission locks that answer.
5. After the question set finishes, review answers, explanations, sources, and
   concept changes. Pending grading is visibly unresolved, never a wrong answer.
6. Continue opens the next selected activity, or leave with progress saved.
7. Weak evidence leads to practice; demonstrated misunderstanding leads to focused
   remediation. Follow-up uses fresh questions.

## Return and interruption

| Situation | Return behavior |
| --- | --- |
| Setup unfinished | Finish setup with saved inputs/files |
| Processing underway | Current durable processing state |
| Outline ready | Review outline |
| Teaching interrupted | Same activity, saved place and format |
| Assessment interrupted | Same question set; submitted answers locked |
| Grading pending | Saved answer, Awaiting grading, Retry grading |
| Assessment finished | Saved results; Continue selects/resumes the next activity |

Browsing the outline never starts another activity. Back to course saves progress.
Refresh/navigation must not generate replacement questions or new activities.

## Recovery

| Failure | Student action | Preserved state |
| --- | --- | --- |
| Temporary processing failure | Retry | Sources and reusable completed work |
| Unreadable source during setup | Replace source | Other valid sources; invalidate dependent artifacts safely |
| Diagnostic generation failure | Retry or Skip for now | Course |
| Teaching generation failure | Retry; inspect sources | Activity/place; no completion inferred |
| Valid questions unavailable | Retry or Back to course | Activity incomplete; no invented evidence |
| Answer submission failure | Retry submission | Entered answer; no confirmed lock |
| Grading failure | Retry grading | Submitted answer; no mastery update |
| Disputed grading | Report grading issue | Original question, answer, judgment for authorized review |

## Unit 1 followed by Unit 2

Student optionally groups both courses under one subject and links Unit 1 when
creating Unit 2. Grouping alone grants no source/evidence reuse. A reliable concept
match may inform selection; uncertain matches offer an optional prerequisite check.
Missing source coverage is not proof of missing knowledge. Earlier material can
support teaching only through the explicit link and approved scoping policy.

## Completion and account lifecycle

All lessons covered is a coverage milestone. Course completion also requires the
agreed sufficient-understanding criteria (still open). Show a completion summary;
further practice is optional and app-selected. No automatic loss of that milestone
from decay is specified yet.

Account controls: tracking preference, presentation reset, sign-out, deletion.
Minimal tracking must retain the state necessary to deliver and resume learning.
Deletion behavior/retention are subject to the later safeguard review.

