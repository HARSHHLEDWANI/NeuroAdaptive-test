"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Brain, ChevronRight, CheckCircle2 } from "lucide-react";
import { submitCalibration, overrideUserArchetype } from "./actions";
import {
  SCENARIO_QUESTIONS,
  MICRO_QUESTIONS,
  AB_OPTIONS,
  type Delta,
} from "./data";

// ─── Types ────────────────────────────────────────────────────────────────────

type Phase = "intro" | "scenario" | "micro" | "ab_test" | "reveal";
type Dim = "visual" | "structural" | "active" | "logic";
type Scores = Record<Dim, number>;
type ArchetypeKey = "THE_VISUALIZER" | "THE_ARCHITECT" | "THE_SPRINTER" | "THE_DEBUGGER" | "THE_PIONEER";

// ─── Static data ──────────────────────────────────────────────────────────────

const ARCHETYPE_META: Record<ArchetypeKey, { title: string; desc: string; color: string }> = {
  THE_VISUALIZER: {
    title: "The Visualizer",
    desc: "You think in pictures. Diagrams, maps, and spatial patterns are how ideas become real for you.",
    color: "bg-[#FFD6A5]",
  },
  THE_ARCHITECT: {
    title: "The Architect",
    desc: "You need the blueprint before the bricks. You master the structure before diving into the details.",
    color: "bg-[#CBF3F0]",
  },
  THE_SPRINTER: {
    title: "The Sprinter",
    desc: "You learn by doing. Trial, error, and fast feedback loops are how things actually click for you.",
    color: "bg-[#FF6B6B]",
  },
  THE_DEBUGGER: {
    title: "The Debugger",
    desc: "You're methodical and precise. You need to understand the *why* at every single step.",
    color: "bg-[#9BF6FF]",
  },
  THE_PIONEER: {
    title: "The Pioneer",
    desc: "You're balanced across all dimensions — highly adaptable with no strong single preference.",
    color: "bg-[#C3B1E1]",
  },
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

const EMPTY_SCORES: Scores = { visual: 0, structural: 0, active: 0, logic: 0 };

function applyDelta(scores: Scores, delta: Delta): Scores {
  const next = { ...scores };
  for (const [dim, val] of Object.entries(delta) as [Dim, number][]) {
    next[dim] = (next[dim] ?? 0) + val;
  }
  return next;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function ProgressBar({ current, total }: { current: number; total: number }) {
  return (
    <div className="w-full h-3 bg-white border-2 border-black rounded-full overflow-hidden mb-8 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
      <div
        className="h-full bg-black transition-all duration-500"
        style={{ width: `${(current / total) * 100}%` }}
      />
    </div>
  );
}

function OptionCard({
  text,
  selected,
  onClick,
}: {
  text: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-5 border-4 border-black rounded-2xl font-bold text-base transition-all flex items-center justify-between gap-4
        ${selected
          ? "bg-black text-white shadow-none translate-x-1 translate-y-1"
          : "bg-white hover:bg-[#F4F1EA] shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] active:translate-y-1 active:shadow-none"
        }`}
    >
      <span>{text}</span>
      {selected && <CheckCircle2 className="w-5 h-5 flex-shrink-0" />}
    </button>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function MissionPage() {
  const router = useRouter();

  const [phase, setPhase] = useState<Phase>("intro");
  const [scenarioStep, setScenarioStep] = useState(0);
  const [microStep, setMicroStep] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [accumulatedScores, setAccumulatedScores] = useState<Scores>(EMPTY_SCORES);
  const [abChoice, setAbChoice] = useState<"visual" | "logical" | "neutral">("neutral");
  const [assignedArchetype, setAssignedArchetype] = useState<ArchetypeKey | null>(null);
  const [showOverride, setShowOverride] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Total steps across parts A + B for the progress bar
  const TOTAL_STEPS = SCENARIO_QUESTIONS.length + MICRO_QUESTIONS.length + 1; // +1 for A/B
  const currentStep =
    phase === "scenario" ? scenarioStep :
    phase === "micro"    ? SCENARIO_QUESTIONS.length + microStep :
    phase === "ab_test"  ? SCENARIO_QUESTIONS.length + MICRO_QUESTIONS.length :
    TOTAL_STEPS;

  // ── Handlers ─────────────────────────────────────────────────────────────────

  function handleOptionSelect(idx: number) {
    setSelectedOption(idx);
  }

  function handleNext() {
    if (selectedOption === null) return;

    if (phase === "scenario") {
      const delta = SCENARIO_QUESTIONS[scenarioStep].options[selectedOption].delta;
      const newScores = applyDelta(accumulatedScores, delta);
      setAccumulatedScores(newScores);
      setSelectedOption(null);

      if (scenarioStep < SCENARIO_QUESTIONS.length - 1) {
        setScenarioStep((s) => s + 1);
      } else {
        setPhase("micro");
      }
      return;
    }

    if (phase === "micro") {
      const delta = MICRO_QUESTIONS[microStep].options[selectedOption].delta;
      const newScores = applyDelta(accumulatedScores, delta);
      setAccumulatedScores(newScores);
      setSelectedOption(null);

      if (microStep < MICRO_QUESTIONS.length - 1) {
        setMicroStep((s) => s + 1);
      } else {
        setPhase("ab_test");
      }
    }
  }

  async function handleAbChoice(choice: "visual" | "logical") {
    setAbChoice(choice);
    setIsSubmitting(true);

    const result = await submitCalibration({
      accumulated_scores: accumulatedScores,
      ab_choice: choice,
    });

    if (result.success && result.archetype) {
      setAssignedArchetype(result.archetype as ArchetypeKey);
      setPhase("reveal");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      alert("Something went wrong saving your profile. Please try again.");
    }
    setIsSubmitting(false);
  }

  async function handleOverride(archetype: string) {
    setIsSubmitting(true);
    const result = await overrideUserArchetype(archetype);
    if (result.success) {
      router.push("/dashboard");
    } else {
      alert("Failed to update. Please try again.");
      setIsSubmitting(false);
    }
  }

  // ── Render: Intro ─────────────────────────────────────────────────────────────

  if (phase === "intro") {
    return (
      <div className="min-h-screen bg-[#F4F1EA] text-black font-[family-name:var(--font-kodchasan)] flex items-center justify-center px-6 py-16">
        <div className="max-w-2xl w-full">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-black text-white px-4 py-2 text-sm font-bold mb-8 border-2 border-black shadow-[3px_3px_0px_0px_rgba(255,159,28,1)]">
              <Brain className="w-4 h-4" />
              Cognitive Calibration
            </div>
            <h1 className="text-5xl md:text-6xl font-black mb-6 leading-tight tracking-tight">
              Let's map{" "}
              <span className="underline decoration-[#FF9F1C] decoration-4">
                how you think.
              </span>
            </h1>
            <p className="text-lg font-medium text-gray-700 max-w-xl mx-auto">
              Instead of asking how you learn, we observe the decisions you make.
              8 quick scenarios. Under 3 minutes.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-12">
            {[
              { label: "5 Scenarios", sub: "Real decisions, not opinions" },
              { label: "2 Quick Picks", sub: "Format preferences" },
              { label: "1 A/B Test", sub: "See what clicks for you" },
            ].map((item) => (
              <div
                key={item.label}
                className="bg-white border-4 border-black p-5 text-center shadow-[5px_5px_0px_0px_rgba(0,0,0,1)]"
              >
                <div className="text-xl font-black mb-1">{item.label}</div>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  {item.sub}
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => setPhase("scenario")}
            className="w-full bg-black text-white border-4 border-black py-5 font-black text-xl shadow-[8px_8px_0px_0px_rgba(255,159,28,1)] hover:shadow-[4px_4px_0px_0px_rgba(255,159,28,1)] hover:translate-y-1 transition-all flex items-center justify-center gap-3"
          >
            START CALIBRATION
            <ChevronRight className="w-6 h-6" strokeWidth={3} />
          </button>
        </div>
      </div>
    );
  }

  // ── Render: Reveal ────────────────────────────────────────────────────────────

  if (phase === "reveal" && assignedArchetype) {
    const meta = ARCHETYPE_META[assignedArchetype] ?? ARCHETYPE_META.THE_PIONEER;

    return (
      <div className="min-h-screen bg-[#F4F1EA] text-black font-[family-name:var(--font-kodchasan)] flex items-center justify-center px-6 py-16">
        <div className="max-w-2xl w-full">
          <div className="text-center mb-10">
            <div className="inline-block bg-black text-white px-4 py-1.5 text-sm font-bold mb-6 border-2 border-black">
              CALIBRATION COMPLETE
            </div>
            <h1 className="text-4xl md:text-5xl font-black mb-3 leading-tight">
              Your cognitive profile is ready.
            </h1>
          </div>

          <div
            className={`${meta.color} border-4 border-black shadow-[10px_10px_0px_0px_rgba(0,0,0,1)] p-10 mb-8 text-center`}
          >
            <div className="text-xs font-black tracking-[0.2em] uppercase mb-3 opacity-60">
              Primary Archetype
            </div>
            <h2 className="text-5xl font-black mb-5">{meta.title}</h2>
            <p className="text-lg font-semibold max-w-md mx-auto">{meta.desc}</p>
          </div>

          {!showOverride ? (
            <div className="flex flex-col gap-4">
              <button
                onClick={() => router.push("/dashboard")}
                className="w-full bg-black text-white border-4 border-black py-5 font-black text-xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:translate-y-1 hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] transition-all"
              >
                GO TO DASHBOARD →
              </button>
              <button
                onClick={() => setShowOverride(true)}
                className="w-full bg-transparent border-4 border-black py-4 font-bold text-base hover:bg-white transition-all"
              >
                This doesn't feel right — let me pick manually
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <h3 className="font-black text-lg mb-4">Choose your archetype:</h3>
              {(Object.entries(ARCHETYPE_META) as [ArchetypeKey, typeof ARCHETYPE_META[ArchetypeKey]][]).map(
                ([key, data]) => (
                  <button
                    key={key}
                    onClick={() => handleOverride(key)}
                    disabled={isSubmitting}
                    className={`w-full text-left p-4 border-4 border-black ${data.color} shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-y-1 hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all disabled:opacity-50 flex items-center justify-between`}
                  >
                    <div>
                      <div className="font-black text-lg">{data.title}</div>
                      <div className="text-sm font-medium mt-0.5 opacity-70">{data.desc}</div>
                    </div>
                    {key === assignedArchetype && (
                      <span className="bg-black text-white text-[10px] px-2 py-1 font-black ml-4 flex-shrink-0">
                        AI PICK
                      </span>
                    )}
                  </button>
                )
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  // ── Render: A/B Test ──────────────────────────────────────────────────────────

  if (phase === "ab_test") {
    return (
      <div className="min-h-screen bg-[#F4F1EA] text-black font-[family-name:var(--font-kodchasan)] px-6 py-12">
        <div className="max-w-3xl mx-auto">
          <ProgressBar current={currentStep} total={TOTAL_STEPS} />

          <div className="mb-2">
            <span className="text-xs font-black tracking-widest uppercase text-gray-400">
              Final check
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-black mb-3 leading-tight">
            You're learning about recursion. Which explanation clicked for you?
          </h2>
          <p className="text-sm font-semibold text-gray-500 mb-10">
            Don't overthink it — go with your gut.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {AB_OPTIONS.map((opt) => (
              <div
                key={opt.type}
                className="bg-white border-4 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-6 flex flex-col"
              >
                <div className="text-xs font-black tracking-widest uppercase mb-4 opacity-50">
                  {opt.label}
                </div>
                <pre className="font-mono text-sm leading-relaxed bg-[#F4F1EA] border-2 border-black p-4 flex-1 whitespace-pre overflow-x-auto">
                  {opt.content}
                </pre>
                <button
                  onClick={() => !isSubmitting && handleAbChoice(opt.type)}
                  disabled={isSubmitting}
                  className="mt-6 w-full bg-black text-white border-2 border-black py-3 font-black text-sm shadow-[4px_4px_0px_0px_rgba(255,159,28,1)] hover:shadow-[2px_2px_0px_0px_rgba(255,159,28,1)] hover:translate-y-1 transition-all disabled:opacity-50"
                >
                  {isSubmitting ? "ANALYZING..." : "THIS ONE MADE MORE SENSE →"}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ── Render: Scenario + Micro Questions ────────────────────────────────────────

  const isScenario = phase === "scenario";
  const questions = isScenario ? SCENARIO_QUESTIONS : MICRO_QUESTIONS;
  const step = isScenario ? scenarioStep : microStep;
  const currentQuestion = questions[step];

  return (
    <div className="min-h-screen bg-[#F4F1EA] text-black font-[family-name:var(--font-kodchasan)] px-6 py-12">
      <div className="max-w-2xl mx-auto">
        <ProgressBar current={currentStep + 1} total={TOTAL_STEPS} />

        <div className="mb-2">
          <span className="text-xs font-black tracking-widest uppercase text-gray-400">
            {isScenario
              ? `Scenario ${scenarioStep + 1} of ${SCENARIO_QUESTIONS.length}`
              : `Quick check ${microStep + 1} of ${MICRO_QUESTIONS.length}`}
          </span>
        </div>

        <h2 className="text-2xl md:text-3xl font-black mb-10 leading-tight">
          {currentQuestion.question}
        </h2>

        <div className="flex flex-col gap-4 mb-12">
          {currentQuestion.options.map((opt, idx) => (
            <OptionCard
              key={idx}
              text={opt.text}
              selected={selectedOption === idx}
              onClick={() => handleOptionSelect(idx)}
            />
          ))}
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleNext}
            disabled={selectedOption === null}
            className={`flex items-center gap-3 px-8 py-4 border-4 border-black font-black text-lg transition-all
              ${selectedOption === null
                ? "bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed"
                : "bg-[#FF9F1C] shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-y-1 active:translate-y-2 active:shadow-none"
              }`}
          >
            {isScenario && scenarioStep === SCENARIO_QUESTIONS.length - 1
              ? "QUICK CHECKS"
              : !isScenario && microStep === MICRO_QUESTIONS.length - 1
              ? "FINAL TEST"
              : "NEXT"}
            <ChevronRight className="w-5 h-5" strokeWidth={3} />
          </button>
        </div>
      </div>
    </div>
  );
}
