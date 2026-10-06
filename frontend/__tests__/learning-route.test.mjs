import assert from "node:assert/strict";
import test from "node:test";
import { studyHrefForRecommendation } from "../lib/learning-route.ts";

const courseId = "course-1";
const structure = {
  modules: [
    {
      lessons: [
        { id: "lesson-1", concepts: [{ concept_id: "concept-1" }] },
        { id: "lesson-2", concepts: [{ concept_id: "concept-2" }] },
      ],
    },
  ],
};

test("a recommended lesson opens its study page", () => {
  assert.equal(
    studyHrefForRecommendation(courseId, { lesson_id: "lesson-2", concept_ids: ["concept-2"] }, structure),
    "/courses/course-1/study/lesson-2",
  );
});

test("a concept recommendation opens the lesson containing that concept", () => {
  assert.equal(
    studyHrefForRecommendation(courseId, { lesson_id: null, concept_ids: ["concept-2"] }, structure),
    "/courses/course-1/study/lesson-2",
  );
});

test("an unmapped recommendation does not silently choose a different lesson", () => {
  assert.equal(
    studyHrefForRecommendation(courseId, { lesson_id: null, concept_ids: ["missing"] }, structure),
    null,
  );
});
