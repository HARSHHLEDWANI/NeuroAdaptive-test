# Screen contracts

Proposed screens; route names and visual styling are not prescribed.

| Screen | Essential content | Actions |
| --- | --- | --- |
| Sign in | Product purpose; Google sign-in; recoverable auth error | Sign in |
| Dashboard | Course title/state/progress; first-course empty state | Create course; Finish setup / Review outline / Continue studying |
| Course setup | Name, goal, files, validation; optional subject and previous-course link | Add/remove sources before locking; Prepare course |
| Processing | Current/completed stages; understandable failure reason | Back to dashboard; Review outline when ready; Retry / Replace source |
| Outline review | Modules, lessons, objectives, prerequisite relationships; coverage warnings | Rename modules/lessons; Publish |
| Diagnostic introduction | Purpose, question count, submission rules, meaning of skipping | Take diagnostic; Skip for now |
| Course overview | Inspectable outline; concept labels/evidence strength; coverage; current activity and reason | Continue studying; inspect outline/progress; Back to dashboard |
| Activity workspace | Title, purpose/reason; activity-specific content; saved position | Format switch; tutor/source panels; Ready for questions or Start questions; Back to course |
| Assessment | One MCQ/short-answer question; count/progress; submission/pending states | Submit answer; Next question; Back to course |
| Results | Correctness or pending judgment; expected reasoning; rubric points; sources; concept changes; next step | Continue; Ask tutor; Report grading issue; Retry grading; Back to course |
| Completion | Coverage and demonstrated understanding; limits of the estimate | Return to dashboard; Optional practice |
| Account settings | Tracking preference; independent presentation reset; account controls | Save; Reset preferences; Sign out; Delete account |

## Workspace

- One shared activity shell; meaningful teaching/question content changes by activity type.
- Main content: objective, explanation, example, recap for teaching activities.
- Concise, detailed, worked example, analogy formats retain the same learning objective.
- Tutor receives course/activity context. Sources open supporting passages with document
  and page where available; TXT/Markdown use headings/locations without invented pages.
- Tutor/source panels preserve activity position. Responsive behavior must retain this
  context on smaller screens.
- No selector for alternative activities; outline inspection does not launch lessons.

## Assessment and results

- Tutor assistance disabled during assessments, available on results.
- Answers lock only after confirmed submission. Retry must not create a second attempt.
- Correctness/explanations withheld until the question set is submitted, including on
  resume. Grading-pending questions remain clearly pending.
- Reading finished, assessment submitted, grading finished, and understanding demonstrated
  are separate states, not one Complete Lesson button.

## Shared states

Every data-dependent screen needs loading, empty, failure/retry, and unavailable
handling. Show actionable learner language, not raw provider errors. Preserve entered
work and saved progress. Foreign/deleted resources must not expose private content.

## Progress vocabulary

Not assessed; Needs attention; Developing; Proficient; Mastered. Explain each label
briefly and show limited evidence / more supporting evidence under an agreed policy.
Do not show precise mastery percentages as established knowledge. Keep lesson coverage
and concept understanding separate.

