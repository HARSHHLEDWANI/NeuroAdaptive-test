"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { submitCalibrationAction } from "@/app/actions/profile"; // <-- Import the Server Action

const questions = [
  {
    id: "pref",
    text: "When learning something complex, what's your first instinct?",
    options: [
      { label: "Look for a diagram or flowchart", dimension: "visual", points: 20 },
      { label: "Read a detailed explanation", dimension: "textual", points: 20 },
      { label: "Check the logic or code samples", dimension: "logic", points: 20 },
    ],
  },
  {
    id: "depth",
    text: "How much detail do you usually want upfront?",
    options: [
      { label: "Just the 'TL;DR' (Too Long; Didn't Read)", dimension: "textual", points: 5 },
      { label: "A comprehensive deep dive", dimension: "depth", points: 25 },
    ],
  },
];

export default function CalibrationQuiz() {
  const [step, setStep] = useState(0);
  const router = useRouter();

  const handleSelection = async (dimension: string, points: number) => {
    try {
      // Calls the secure server action instead of exposing keys in the browser
      await submitCalibrationAction(dimension, points);

      if (step < questions.length - 1) {
        setStep((prev) => prev + 1);
      } else {
        router.refresh();
      }
    } catch (error) {
      console.error("Calibration failed:", error);
    }
  };

  const current = questions[step];

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl border border-blue-100">
        <div className="mb-6">
          <span className="text-xs font-bold text-blue-600 uppercase tracking-widest">
            Mission Calibration
          </span>
          <h2 className="text-2xl font-bold text-gray-900 mt-1">
            {current.text}
          </h2>
        </div>

        <div className="space-y-3">
          {current.options.map((opt, idx) => (
            <button
              key={idx}
              onClick={() => handleSelection(opt.dimension, opt.points)}
              className="w-full text-left p-4 rounded-xl border-2 border-gray-100 hover:border-blue-500 hover:bg-blue-50 transition-all font-medium text-gray-700"
            >
              {opt.label}
            </button>
          ))}
        </div>

        <div className="mt-8 flex gap-1 justify-center">
          {questions.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 w-8 rounded-full ${
                i === step ? "bg-blue-600" : "bg-gray-200"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}