/** Resolve an API selected activity to a lesson in the published structure. */
export function studyHrefForRecommendation(
  courseId: string,
  recommended: unknown,
  structure: unknown,
): string | null {
  if (!recommended || typeof recommended !== "object") return null;
  if (!structure || typeof structure !== "object") return null;

  const activity = recommended as Record<string, unknown>;
  const courseStructure = structure as Record<string, unknown>;
  if (!Array.isArray(courseStructure.modules)) return null;

  const conceptIds = Array.isArray(activity.concept_ids)
    ? activity.concept_ids.filter((id): id is string => typeof id === "string")
    : [];

  for (const courseModule of courseStructure.modules) {
    if (!courseModule || typeof courseModule !== "object") continue;
    const lessons = (courseModule as Record<string, unknown>).lessons;
    if (!Array.isArray(lessons)) continue;

    for (const lesson of lessons) {
      if (!lesson || typeof lesson !== "object") continue;
      const row = lesson as Record<string, unknown>;
      if (typeof row.id !== "string") continue;
      if (row.id === activity.lesson_id) {
        return `/courses/${courseId}/study/${row.id}`;
      }
    }
  }

  for (const courseModule of courseStructure.modules) {
    if (!courseModule || typeof courseModule !== "object") continue;
    const lessons = (courseModule as Record<string, unknown>).lessons;
    if (!Array.isArray(lessons)) continue;

    for (const lesson of lessons) {
      if (!lesson || typeof lesson !== "object") continue;
      const row = lesson as Record<string, unknown>;
      if (typeof row.id !== "string" || !Array.isArray(row.concepts)) continue;
      if (row.concepts.some((concept: unknown) =>
        concept && typeof concept === "object" &&
        typeof (concept as Record<string, unknown>).concept_id === "string" &&
        conceptIds.includes((concept as Record<string, unknown>).concept_id as string)
      )) {
        return `/courses/${courseId}/study/${row.id}`;
      }
    }
  }

  return null;
}
