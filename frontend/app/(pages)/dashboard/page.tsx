"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { signOut, useSession } from "next-auth/react";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight, BookOpen, Brain, FileText, LogOut, Plus, RefreshCcw } from "lucide-react";
import { StateWrapper } from "@/components/StateWrapper";

type JobSummary = { id: string; status: string; current_stage?: string | null };
type Course = { id: string; title: string; goal?: string | null; status: string; source_count: number; latest_job?: JobSummary | null; latest_review_version_id?: string | null; active_version_id?: string | null };

const statusCopy: Record<string, string> = {
  DRAFT: "Add sources to begin", PROCESSING: "Sources are being processed",
  REVIEW_READY: "Your generated course is ready to review", PUBLISHED: "Published and ready to learn",
  NEEDS_INPUT: "Needs a source correction", FAILED: "Processing needs attention",
};

function actionFor(course: Course) {
  if (course.status === "PUBLISHED") return { label: "Continue learning", href: `/courses/${course.id}/learn` };
  if (course.status === "REVIEW_READY") return { label: "Review course", href: `/courses/${course.id}/workspace` };
  if (course.status === "PROCESSING") return { label: "View progress", href: `/courses/${course.id}/workspace` };
  return { label: course.source_count ? "Finish setup" : "Add sources", href: `/courses/${course.id}/workspace` };
}

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const response = await fetch("/api/v1/courses");
      if (!response.ok) throw new Error(response.status === 401 ? "Unauthorized" : "We could not load your courses.");
      setCourses(await response.json());
    } catch (cause) { setError(cause instanceof Error ? cause.message : "We could not load your courses."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { if (status === "unauthenticated") router.replace("/signin"); if (status === "authenticated") void load(); }, [status, router, load]);
  if (status === "loading" || !session) return null;
  return <main className="min-h-screen bg-[#F4F1EA] pb-20 text-black font-[family-name:var(--font-kodchasan)]">
    <nav className="sticky top-0 z-20 flex items-center justify-between border-b-2 border-black bg-white px-6 py-4">
      <Link href="/dashboard" className="flex items-center gap-3 font-black"><span className="grid size-10 place-items-center border-2 border-black bg-purple-500 text-white shadow-[3px_3px_0_#000]"><Brain /></span>NEUROLEARN</Link>
      <button onClick={() => signOut({ callbackUrl: "/signin" })} className="flex items-center gap-2 border-2 border-black bg-[#FF6B6B] px-4 py-2 font-bold shadow-[3px_3px_0_#000]"><LogOut size={16} />Sign out</button>
    </nav>
    <section className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-10 flex flex-wrap items-end justify-between gap-6"><div><p className="mb-2 font-bold uppercase tracking-[.2em] text-purple-700">Your source-to-course workspace</p><h1 className="text-4xl font-black md:text-6xl">All your courses.</h1><p className="mt-3 max-w-xl font-medium text-zinc-600">Each course keeps its own source set, processing record, review gate, and learning path.</p></div><Link href="/courses/new" className="flex items-center gap-2 border-2 border-black bg-[#FF9F1C] px-5 py-3 font-black shadow-[4px_4px_0_#000]"><Plus />Create course</Link></div>
      <StateWrapper isLoading={loading} isError={Boolean(error)} errorMessage={error} isUnauthorized={error === "Unauthorized"} isEmpty={!loading && !error && courses.length === 0} emptyMessage="Create a course, then add your own study material to start the source-grounded flow." onRetry={load}>
        <div className="grid gap-5 md:grid-cols-2">{courses.map((course) => { const action = actionFor(course); return <article key={course.id} className="border-2 border-black bg-white p-6 shadow-[6px_6px_0_#000]"><div className="mb-5 flex items-start justify-between gap-4"><div><p className="mb-1 text-xs font-black uppercase tracking-widest text-purple-700">{course.status.replace("_", " ")}</p><h2 className="text-2xl font-black">{course.title}</h2></div><BookOpen className="shrink-0" /></div><p className="min-h-12 font-medium text-zinc-600">{course.goal || "No learning goal recorded."}</p><div className="my-5 grid grid-cols-2 border-2 border-black text-sm font-bold"><span className="border-r-2 border-black p-3"><FileText className="mr-2 inline size-4" />{course.source_count} source{course.source_count === 1 ? "" : "s"}</span><span className="p-3">{statusCopy[course.status] || "Course state unavailable"}</span></div>{course.latest_job?.current_stage && <p className="mb-4 flex items-center gap-2 text-sm font-bold"><RefreshCcw className="size-4" />{course.latest_job.current_stage.replaceAll("_", " ")}</p>}<Link href={action.href} prefetch={false} className="flex w-full items-center justify-between border-2 border-black bg-black px-4 py-3 font-black text-white">{action.label}<ArrowRight /></Link></article>; })}</div>
      </StateWrapper>
    </section>
  </main>;
}
