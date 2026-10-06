import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { auth } from "@/auth";
import { internalHeaders } from "@/lib/internal-auth";
import { studyHrefForRecommendation } from "@/lib/learning-route";

const BACKEND_URL =
  process.env.INTERNAL_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "http://backend:8000";

function Unavailable({ courseId }: { courseId: string }) {
  return (
    <main className="min-h-screen bg-[#F4F1EA] px-6 py-16 text-center text-black">
      <h1 className="text-2xl font-bold">Your next activity is unavailable right now</h1>
      <p className="mt-3">Your published course is saved. Please try again shortly.</p>
      <div className="mt-6 flex justify-center gap-4">
        <Link href={`/courses/${courseId}/learn`} className="border-2 border-black bg-[#FF9F1C] px-5 py-3 font-bold">Try again</Link>
        <Link href="/dashboard" className="border-2 border-black bg-white px-5 py-3 font-bold">Dashboard</Link>
      </div>
    </main>
  );
}

export default async function LearnPage({ params }: { params: Promise<{ courseId: string }> }) {
  const session = await auth();
  if (!session?.user?.email) redirect("/signin");

  const { courseId } = await params;
  const headers = internalHeaders(session.user.email);
  const courseUrl = `${BACKEND_URL}/api/v1/courses/${courseId}`;
  let courseResponse: Response;
  try {
    courseResponse = await fetch(courseUrl, { headers, cache: "no-store" });
  } catch {
    return <Unavailable courseId={courseId} />;
  }
  if (courseResponse.status === 404) notFound();
  if (!courseResponse.ok) return <Unavailable courseId={courseId} />;

  const course = await courseResponse.json();
  if (course.status !== "PUBLISHED") redirect(`/courses/${courseId}/workspace`);

  let activityResponse: Response;
  let structureResponse: Response;
  try {
    [activityResponse, structureResponse] = await Promise.all([
      fetch(`${courseUrl}/next-activity`, { headers, cache: "no-store" }),
      fetch(`${courseUrl}/structure`, { headers, cache: "no-store" }),
    ]);
  } catch {
    return <Unavailable courseId={courseId} />;
  }
  if (!activityResponse.ok || !structureResponse.ok) return <Unavailable courseId={courseId} />;

  const activity = await activityResponse.json();
  const structure = await structureResponse.json();
  const studyHref = studyHrefForRecommendation(courseId, activity.recommended, structure);
  if (!studyHref) return <Unavailable courseId={courseId} />;
  redirect(studyHref);
}
