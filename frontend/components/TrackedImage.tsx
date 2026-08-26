"use client";

import { useEffect } from "react";
import { useTrackVisibility } from "@/hooks/useTrackVisibility";
import Image from "next/image";

interface Props {
  src: string;
  alt: string;
  id: number;
}

export default function TrackedImage({ src, alt, id }: Props) {
  // Use a higher threshold (0.8) for images to ensure they are mostly on-screen
  const { elementRef, secondsViewed } = useTrackVisibility(0.8);

  useEffect(() => {
    if (secondsViewed > 0 && secondsViewed % 5 === 0) {
      const sendPulse = async () => {
        try {
          await fetch("http://localhost:8000/api/v1/profile/pulse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              paragraph_id: id, // We reuse this field for simplicity
              seconds: 5,
              dimension: "visual" // CRITICAL: This triggers the visual_affinity score
            }),
          });
          console.log(`📸 Visual Pulse saved for Image ${id}`);
        } catch (error) {
          console.error("❌ Failed to send visual pulse:", error);
        }
      };
      sendPulse();
    }
  }, [secondsViewed, id]);

  return (
    <div ref={elementRef} className="my-8 flex flex-col items-center">
      <div className="relative w-full h-[400px] rounded-lg overflow-hidden border-4 border-transparent hover:border-blue-200 transition-all">
        <Image 
          src={src} 
          alt={alt} 
          fill 
          className="object-cover"
        />
      </div>
      <p className="text-sm text-gray-500 mt-2 italic">{alt}</p>
      {/* Debugging helper */}
      <div className="text-[10px] text-gray-300">{secondsViewed}s viewed</div>
    </div>
  );
}