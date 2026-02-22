"use client";

import { useEffect, useState } from "react";

const messages = [
  "Analyzing geographic clusters...",
  "Optimizing travel flow...",
  "Balancing cultural depth with pacing...",
  "Allocating budget intelligently...",
  "Mapping restaurants near final stops...",
  "Finalizing your personalized route..."
];

export default function ProcessingScreen() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % messages.length);
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  return (
    <section className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-black via-gray-950 to-gray-900 px-6 text-center text-white">
      
      <div className="w-full max-w-3xl rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-xl sm:p-10">
        
        {/* Video */}
        <video
          className="h-[220px] w-full rounded-2xl object-cover sm:h-[320px]"
          src="/processing.mp4"
          autoPlay
          muted={false}
          loop
          playsInline
          preload="auto"
        />

        {/* Title */}
        <h2 className="mt-8 text-xl sm:text-2xl font-semibold tracking-wide text-gray-100">
          Your Intelligent Journey Is Being Designed
        </h2>

        {/* Dynamic Status Text */}
        <p className="mt-4 text-sm sm:text-base text-gray-400 transition-opacity duration-500">
          {messages[index]}
        </p>

        {/* Animated Dots */}
        <div className="mt-6 flex items-center justify-center gap-2">
          <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-cyan-400" />
          <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-cyan-400 [animation-delay:150ms]" />
          <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-cyan-400 [animation-delay:300ms]" />
        </div>

        {/* Progress Bar */}
        <div className="mt-8 h-2 w-full overflow-hidden rounded-full bg-white/10">
          <div className="h-full w-full animate-[progress_4s_linear_infinite] bg-gradient-to-r from-transparent via-cyan-400/70 to-transparent" />
        </div>

        {/* Footer Note */}
        <p className="mt-6 text-xs text-gray-500">
          This usually takes 8–15 seconds depending on route complexity.
        </p>
      </div>
    </section>
  );
}
