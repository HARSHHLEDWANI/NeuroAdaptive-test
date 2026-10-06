# Baseline implementation and downstream work

Approved 2026-10-06; current agent is authorized to execute all baseline areas. Member 3 coordinates integration/migrations, Member 2 processing/providers, Member 1 web/contracts. Existing paths and migrations are preserved.

| Task | Dependencies | Owner | Pass condition |
|---|---|---|---|
| B00 contract | none | integration | scope/architecture/instructions agree |
| B01 preservation | B00 | integration | source checkpoint; runtime data excluded |
| B02 setup | B01 | Members 1/3 | repeatable installation/startup; safe templates |
| B03 schema | B02 | Member 3 | fresh and incremental PostgreSQL migration checks |
| B04 worker | B03 | Members 2/3 | atomic claims/leases; safe duplicate/restart/retry |
| B05 boundaries | B03 | all | trusted identity, nested ownership, legacy isolation |
| B06 contracts | B05 | Members 1/3 | OpenAPI responses/generated TS; drift check |
| B07 checkpoint | B04–B06 | all | required tests/lint/types/build and baseline report |

## Subsequent product milestones
1. Source-grounded lesson-specific MCQ/short-answer assessments.
2. One-attempt evidence, mastery/sequencing alignment and enforced next activity.
3. Complete claim coverage/semantic grounding and validated artifact caching.
4. Editable course outline and source-gap review; presentation feedback.
5. Focused academic UX and progress views.
6. Hosted private deployment, privacy deletion/pilot hardening.
7. Technical baselines and consenting descriptive pilot; correct black book against exact tested snapshot.

Integrate through develop; promote only executed green checkpoints. Historical migrations, learner records and published branch history remain intact.
