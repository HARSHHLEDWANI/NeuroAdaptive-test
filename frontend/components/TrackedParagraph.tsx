"use client";

import { useEffect } from "react";
import { useTrackVisibility } from "@/hooks/useTrackVisibility";

interface Props {
  text: string;
  paragraphId: number;
}

export default function TrackedParagraph({ text, paragraphId }: Props) {
  const { elementRef, secondsViewed } = useTrackVisibility(0.6);

  useEffect(() => {
    // Only send a pulse every 5 seconds
    if (secondsViewed > 0 && secondsViewed % 5 === 0) {
      
      const sendPulse = async () => {
        try {
          await fetch("http://localhost:8000/api/v1/profile/pulse", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              paragraph_id: paragraphId,
              seconds: 5,
              dimension: "textual" // Since this is a text paragraph
            }),
          });
          console.log(`✅ Pulse saved for Paragraph ${paragraphId}`);
        } catch (error) {
          console.error("❌ Failed to send pulse:", error);
        }
      };

      sendPulse();
    }
  }, [secondsViewed, paragraphId]);

  return (
    <div ref={elementRef} className="transition-colors duration-500 rounded p-2 hover:bg-blue-50/50">
      <p className="text-lg text-gray-800 leading-relaxed">{text}</p>
    </div>
  );
}