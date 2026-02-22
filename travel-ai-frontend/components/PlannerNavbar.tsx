"use client";

import Image from "next/image";

interface PlannerNavbarProps {
  activeView: "input" | "itinerary";
  hasItinerary: boolean;
  onInputClick: () => void;
  onItineraryClick: () => void;
  onFinalImagesClick: () => void;
}

export default function PlannerNavbar({
  activeView,
  hasItinerary,
  onInputClick,
  onItineraryClick,
  onFinalImagesClick,
}: PlannerNavbarProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-cyan-400/10 bg-black/65 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <div className="flex items-center gap-3">
          <Image
            src="/Gen_ai_tourism.png"
            alt="Travel OS"
            width={40}
            height={40}
            className="rounded-full"
          />
          <div>
            <p className="text-xs uppercase tracking-[0.22em] text-cyan-300/80">
              Travel OS
            </p>
            <p className="text-sm text-gray-200 sm:text-base">
              Intelligent Journey Studio
            </p>
          </div>
        </div>

        <nav className="no-scrollbar flex w-full items-center gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-white/5 p-1 sm:w-auto">
          <button
            onClick={onInputClick}
            className={`shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition-all duration-300 ${
              activeView === "input"
                ? "bg-cyan-500 text-black"
                : "text-gray-300 hover:bg-white/10 hover:text-white"
            }`}
          >
            Input
          </button>
          <button
            onClick={onItineraryClick}
            className={`shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition-all duration-300 ${
              activeView === "itinerary"
                ? "bg-cyan-500 text-black"
                : "text-gray-300 hover:bg-white/10 hover:text-white"
            } ${hasItinerary ? "" : "opacity-60"}`}
          >
            Itinerary
          </button>
          <button
            onClick={onFinalImagesClick}
            className="shrink-0 rounded-xl px-4 py-2 text-sm font-semibold text-gray-300 transition-all duration-300 hover:bg-white/10 hover:text-white"
          >
            Final Plan
          </button>
        </nav>
      </div>
    </header>
  );
}
