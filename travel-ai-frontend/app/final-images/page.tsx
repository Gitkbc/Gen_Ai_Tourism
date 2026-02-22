"use client";

import PlaceIcon from "@/components/PlaceIcon";
import Link from "next/link";
import { useMemo, useState } from "react";
import { PlaceActivity } from "@/types/itinerary";
import Image from "next/image";

const STORAGE_KEY = "travel_ai_state_v1";

interface PlacePreview extends PlaceActivity {
  dayLabel: string;
}

function isPlace(activity: unknown): activity is PlaceActivity {
  if (!activity || typeof activity !== "object") {
    return false;
  }
  const record = activity as Record<string, unknown>;
  return typeof record.place_name === "string";
}

export default function FinalImagesPage() {
  const places = useMemo<PlacePreview[]>(() => {
    if (typeof window === "undefined") {
      return [];
    }

    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return [];
      }

      const parsed = JSON.parse(raw) as {
        itineraryData?: {
          itinerary?: {
            days?: Array<{
              day?: number;
              timeline?: unknown[];
            }>;
          };
        };
      };

      const days = parsed?.itineraryData?.itinerary?.days;
      if (!Array.isArray(days)) {
        return [];
      }

      return days.flatMap((day, dayIndex) => {
        const timeline = Array.isArray(day.timeline) ? day.timeline : [];
        return timeline
          .filter(isPlace)
          .map((place) => ({
            ...place,
            dayLabel: `Day ${day.day ?? dayIndex + 1}`,
          }));
      });
    } catch {
      return [];
    }
  }, []);

  const [selectedIndex, setSelectedIndex] = useState(0);
  const selected = places[selectedIndex] ?? null;

  return (
    <div className="flex h-screen min-h-screen flex-col bg-gradient-to-br from-gray-950 via-black to-slate-900 text-white">
      <header className="sticky top-0 z-40 border-b border-cyan-400/10 bg-black/70 backdrop-blur-xl">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <Image
              src="/Gen_ai_tourism.png"
              alt="Travel OS"
              width={40}
              height={40}
              className="rounded-full"
            />
            <div>
              <p className="text-xs uppercase tracking-widest text-cyan-300">
                Travel OS
              </p>
              <h1 className="text-lg font-semibold text-white">
                Final Destination Images
              </h1>
            </div>
          </div>
          <nav className="flex items-center gap-2 rounded-full border border-white/10 bg-gray-800/50 p-1">
            <Link
              href="/"
              className="rounded-full px-4 py-1.5 text-sm font-medium text-gray-300 transition-colors hover:text-white"
            >
              Input
            </Link>
            <Link
              href="/"
              className="rounded-full px-4 py-1.5 text-sm font-medium text-gray-300 transition-colors hover:text-white"
            >
              Itinerary
            </Link>
            <span className="rounded-full bg-cyan-500 px-4 py-1.5 text-sm font-semibold text-black">
              Final Images
            </span>
          </nav>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto grid h-full w-full max-w-7xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-2 lg:px-8">
          <article className="flex flex-col rounded-2xl border border-white/10 bg-gray-900/50 p-4 shadow-lg backdrop-blur-sm">
            {selected ? (
              <>
                <div className="flex flex-1 items-center justify-center rounded-xl border border-white/10 bg-black/30 p-4">
                  <PlaceIcon
                    placeName={selected.place_name}
                    size="xl"
                    showLabel
                  />
                </div>
                <div className="mt-4 rounded-xl border border-white/10 bg-black/30 p-4">
                  <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
                    {selected.dayLabel} &bull; {selected.time}
                  </p>
                  <h2 className="mt-2 text-2xl font-bold text-white">
                    {selected.place_name}
                  </h2>
                  <p className="mt-2 text-sm text-gray-300">
                    {selected.reason_for_time_choice}
                  </p>
                </div>
              </>
            ) : (
              <div className="flex h-full items-center justify-center rounded-2xl border-2 border-dashed border-gray-700/80 bg-black/30 text-center text-gray-400">
                <p>
                  No place data yet.
                  <br />
                  Generate an itinerary first.
                </p>
              </div>
            )}
          </article>

          <aside className="flex flex-col rounded-2xl border border-white/10 bg-gray-900/50 p-4 shadow-lg backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-cyan-300">
              Places
            </h2>
            <div className="no-scrollbar mt-3 flex-1 space-y-2 overflow-y-auto">
              {places.length ? (
                places.map((place, index) => (
                  <button
                    key={`${place.dayLabel}-${place.place_name}-${index}`}
                    onClick={() => setSelectedIndex(index)}
                    className={`w-full rounded-xl border p-3 text-left transition-all duration-200 ${
                      selectedIndex === index
                        ? "border-cyan-400/50 bg-cyan-500/20 shadow-md"
                        : "border-gray-700/80 bg-gray-800/50 hover:border-gray-600 hover:bg-gray-700/50"
                    }`}
                  >
                    <p className="text-xs font-semibold text-cyan-300">
                      {place.dayLabel}
                    </p>
                    <p className="mt-1 font-semibold text-white">
                      {place.place_name}
                    </p>
                    <p className="mt-1 text-xs text-gray-400">{place.time}</p>
                  </button>
                ))
              ) : (
                <div className="flex h-full items-center justify-center rounded-xl border-2 border-dashed border-gray-700/80 bg-black/30 text-sm text-gray-500">
                  <p>No places available.</p>
                </div>
              )}
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
