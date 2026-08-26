"use client";

import { useEffect } from "react";
import { useTrackVisibility } from "@/hooks/useTrackVisibility";

interface Props {
  code: string;
  language: string;
  id: number;
}

export default function TrackedCodeBlock({ code, language, id }: Props) {
  // Logic tracking usually requires higher focus, so we use a 0.7 threshold
  const { elementRef, secondsViewed } = useTrackVisibility(0.7);

  useEffect(() => {
    if (secondsViewed > 0 && secondsViewed % 5 === 0) {
      const sendPulse = async () => {
        try {
          await fetch("http://localhost:8000/api/v1/profile/pulse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              paragraph_id: id,
              seconds: 5,
              dimension: "logic" // This triggers the logic_preference score
            }),
          });
          console.log(`⚙️ Logic Pulse saved for Block ${id}`);
        } catch (error) {
          console.error("❌ Failed to send logic pulse:", error);
        }
      };
      sendPulse();
    }
  }, [secondsViewed, id]);

  return (
    <div ref={elementRef} className="my-6 rounded-lg bg-gray-900 p-4 shadow-lg border-l-4 border-blue-500">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-mono text-gray-400 uppercase">{language}</span>
        <span className="text-[10px] text-gray-600 font-mono">{secondsViewed}s analyzed</span>
      </div>
      <pre className="text-blue-300 font-mono text-sm overflow-x-auto">
        <code>{code}</code>
      </pre>
    </div>
  );
}