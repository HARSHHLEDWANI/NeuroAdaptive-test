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

## Decisions still open

| Decision | Must be settled before |
| --- | --- |
| Mastery bands, evidence-strength labels, completion criteria, and decay policy | Progress/selection acceptance |
| Question count, rubric scoring, difficulty, and fresh-question checks | Assessment release |
| Reliable cross-course concept matching and evidence reuse | Linked-course integration |
| Missing-prerequisite detection and supporting evidence for warnings | Prerequisite-warning release |
| Grading-issue review ownership, retention, and correction behavior | Report-grading-issue release |
| What ends an activity whose assessment stays unavailable | Full recovery acceptance |
| Architecture, safeguard policy, budgets, and deployment | Dependent implementation |

Existing numeric constants are unvalidated defaults, not approved calibration.
Future tunable numbers need named, versioned, configurable policies.

## Scope and authority

This folder records the conversation's product decisions. It does not silently
replace repository operating instructions or authorize architecture/safeguard
changes. Those discussions remain separate. No existing Markdown was read for
this work, as requested; the gap report uses code and the earlier PDF review.

Potential policy conflicts to resolve explicitly: cross-course sources/evidence
versus current-course-only grounding; selected-prerequisite remediation versus
nonblocking prerequisite access; visible recommendation reasons versus the PDF's
no-explanation scope; evidence decay versus the previously supplied scope limits;
source replacement during failed setup versus current source finalization.

