// All calibration question data lives here.
// Scoring is computed on the frontend by accumulating deltas,
// then the raw totals are sent to the backend for normalization + archetype assignment.

export type Dim = "visual" | "structural" | "active" | "logic";
export type Delta = Partial<Record<Dim, number>>;

export type Option = {
  text: string;
  delta: Delta;
};

export type Question = {
  id: string;
  question: string;
  options: Option[];
};

// ─── Part A: Scenario Questions ───────────────────────────────────────────────
// Each question gives 15–18 points to the dominant dimension.
// Starting baseline is 15 per dimension (set server-side).

export const SCENARIO_QUESTIONS: Question[] = [
  {
    id: "q_new_topic",
    question: "You're about to learn a completely new, complex topic. What's your first move?",
    options: [
      { text: "Sketch a diagram showing how the pieces connect",           delta: { visual: 15, structural: 5 } },
      { text: "Find a step-by-step guide and work through it methodically", delta: { logic: 15, structural: 8 } },
      { text: "Jump straight in and experiment to see what happens",        delta: { active: 18 } },
      { text: "Watch a short overview video first",                         delta: { visual: 10, active: 5 } },
    ],
  },
  {
    id: "q_stuck",
    question: "You've been stuck on the same concept for 20 minutes. What do you do?",
    options: [
      { text: "Find a diagram or visual that explains it differently", delta: { visual: 18 } },
      { text: "Break the problem into smaller logical pieces",         delta: { logic: 18 } },
      { text: "Try a completely different approach — just start doing", delta: { active: 18 } },
      { text: "Find a high-level summary that puts it in context",     delta: { structural: 18 } },
    ],
  },
  {
    id: "q_exam",
    question: "You have 45 minutes before an important exam. You:",
    options: [
      { text: "Review annotated diagrams and concept maps",       delta: { visual: 15, structural: 5 } },
      { text: "Work through formulas and key proofs from scratch", delta: { logic: 18 } },
      { text: "Grind practice problems until the pattern clicks",  delta: { active: 18 } },
      { text: "Skim chapter summaries for the key ideas",          delta: { structural: 18 } },
    ],
  },
  {
    id: "q_flatpack",
    question: "Flatpack furniture arrives with no manual. You:",
    options: [
      { text: "Find an assembly video and follow it visually",               delta: { visual: 18 } },
      { text: "Lay out all parts and identify them before starting",         delta: { logic: 10, structural: 12 } },
      { text: "Start assembling immediately and adjust as problems appear",  delta: { active: 18, structural: -8 } },
    ],
  },
  {
    id: "q_programming",
    question: "You're learning a new programming language. Your instinct is to:",
    options: [
      { text: "Draw flowcharts and data-flow diagrams before writing code",     delta: { visual: 15, structural: 5 } },
      { text: "Read the docs carefully and implement each part step by step",   delta: { logic: 12, structural: 8 } },
      { text: "Clone an existing project and hack it until it does what I need", delta: { active: 18 } },
      { text: "Deeply understand the language's core design philosophy first",   delta: { structural: 15, logic: 5 } },
    ],
  },
];

// ─── Part B: Micro Preference Questions ──────────────────────────────────────
// Smaller boosts (+5 to +6). Two quick binary choices.

export const MICRO_QUESTIONS: Question[] = [
  {
    id: "mq_explanation",
    question: "When you receive a long explanation, you prefer:",
    options: [
      { text: "A short summary first — I'll ask for detail if I need it", delta: { structural: 6 } },
      { text: "The full explanation from beginning to end — no shortcuts",  delta: { logic: 6 } },
    ],
  },
  {
    id: "mq_learning_order",
    question: "When learning something new, you naturally:",
    options: [
      { text: "Want to see a concrete example first, then understand the theory", delta: { active: 6, visual: 4 } },
      { text: "Prefer to fully understand the theory before trying to apply it",  delta: { structural: 6, logic: 4 } },
    ],
  },
];

// ─── Part C: A/B Test ─────────────────────────────────────────────────────────
// Same concept (recursion) shown in two different formats.
// User picks whichever clicked for them → +5 to visual or logic.

export const AB_OPTIONS: Array<{
  label: string;
  type: "visual" | "logical";
  content: string;
  delta: Delta;
}> = [
  {
    label: "Option A — The Diagram",
    type: "visual",
    content:
      "factorial(3)\n  └─► factorial(2)\n        └─► factorial(1)\n              └─► factorial(0) → returns 1\n              ↩  returns 1 × 1 = 1\n        ↩  returns 2 × 1 = 2\n  ↩  returns 3 × 2 = 6",
    delta: { visual: 5 },
  },
  {
    label: "Option B — The Walkthrough",
    type: "logical",
    content:
      "Step 1: factorial(3) calls factorial(2) and pauses.\nStep 2: factorial(2) calls factorial(1) and pauses.\nStep 3: factorial(1) calls factorial(0) and pauses.\nStep 4: factorial(0) hits the base case → returns 1.\nStep 5: factorial(1) resumes → returns 1 × 1 = 1.\nStep 6: factorial(2) resumes → returns 2 × 1 = 2.\nStep 7: factorial(3) resumes → returns 3 × 2 = 6.",
    delta: { logic: 5 },
  },
];
