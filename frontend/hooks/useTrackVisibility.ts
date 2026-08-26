// frontend/app/hooks/useTrackVisibility.ts
import { useEffect, useState, useCallback, useRef } from "react";

export function useTrackVisibility(threshold = 0.5) {
  const [isVisible, setIsVisible] = useState(false);
  const [secondsViewed, setSecondsViewed] = useState(0);
  
  // We use a ref to hold the observer so we can clean it up properly
  const observerRef = useRef<IntersectionObserver | null>(null);

  // This callback ref reliably attaches the observer when the DOM node mounts
  const elementRef = useCallback((node: HTMLElement | null) => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    if (node) {
      observerRef.current = new IntersectionObserver(
        ([entry]) => {
          setIsVisible(entry.isIntersecting);
        },
        { threshold }
      );
      observerRef.current.observe(node);
    }
  }, [threshold]);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    // Only run the timer if the element is visible AND the browser tab is active
    const checkVisibilityAndRun = () => {
      if (isVisible && !document.hidden) {
        interval = setInterval(() => {
          setSecondsViewed((prev) => prev + 1);
        }, 1000);
      } else {
        clearInterval(interval);
      }
    };

    // Run initially
    checkVisibilityAndRun();

    // Listen for tab switching to pause/resume the timer
    document.addEventListener("visibilitychange", checkVisibilityAndRun);

    return () => {
      clearInterval(interval);
      document.removeEventListener("visibilitychange", checkVisibilityAndRun);
    };
  }, [isVisible]);

  return { elementRef, secondsViewed, isVisible };
}