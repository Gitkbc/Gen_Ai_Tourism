"use client";

import MealCard from "@/components/MealCard";
import PlaceCard from "@/components/PlaceCard";
import { DayItinerary, MealActivity, PlaceActivity, TimelineItem } from "@/types/itinerary";

interface DayCardProps {
  day: DayItinerary;
  onPlaceSelect: (place: PlaceActivity) => void;
}

function isMealItem(item: TimelineItem): item is MealActivity {
  return (
    typeof (item as MealActivity).meal_type === "string" ||
    typeof (item as MealActivity).signature_dish === "string" ||
    typeof (item as MealActivity).outlet === "string"
  );
}

function getStartHour(item: TimelineItem): number {
  if (typeof item.start_minutes === "number" && Number.isFinite(item.start_minutes)) {
    return Math.max(0, Math.min(23, Math.floor(item.start_minutes / 60)));
  }

  const raw = item.time?.split("-")[0]?.trim();
  if (!raw) {
    return 0;
  }

  const [h] = raw.split(":").map(Number);
  if (!Number.isFinite(h)) {
    return 0;
  }

  return Math.max(0, Math.min(23, h));
}

export default function DayCard({ day, onPlaceSelect }: DayCardProps) {
  const rawTimeline = Array.isArray(day.timeline) ? day.timeline : [];
  const timeline = [...rawTimeline].sort((a, b) => {
    const aStart = typeof a.start_minutes === "number" ? a.start_minutes : Number.MAX_SAFE_INTEGER;
    const bStart = typeof b.start_minutes === "number" ? b.start_minutes : Number.MAX_SAFE_INTEGER;
    return aStart - bStart;
  });

  const hoursWithEvents = new Set(timeline.map((item) => getStartHour(item)));

  return (
    <section className="rounded-2xl border border-white/10 bg-[#10131a]/95 p-4 shadow-[0_20px_40px_rgba(0,0,0,0.45)] animate-fade-in sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-2.5 sm:items-center sm:gap-3">
        <div>
          <h3 className="text-lg font-semibold text-white sm:text-xl">{day.title || `Day ${day.day}`}</h3>
          <p className="mt-1 text-xs leading-6 text-gray-300 sm:text-sm">{day.geographic_flow}</p>
          {day.day_time_window ? (
            <p className="mt-2 text-xs uppercase tracking-[0.16em] text-cyan-200/90">
              Active Window: {day.day_time_window}
            </p>
          ) : null}
        </div>
        <span className="rounded-full border border-cyan-300/30 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-100">
          Walking: {day.walking_distance}
        </span>
      </div>



      <div className="relative mt-5 space-y-4 border-l border-white/10 pl-4 sm:mt-6 sm:space-y-5 sm:pl-5">
        {timeline.length ? (
          timeline.map((item, index) => (
            <div key={`${item.time}-${index}`} className="relative">
              <span className="absolute -left-[22px] top-4 h-2.5 w-2.5 rounded-full bg-cyan-300 sm:-left-[28px]" />
              {isMealItem(item) ? (
                <MealCard meal={item} />
              ) : (
                <PlaceCard place={item as PlaceActivity} onSelect={onPlaceSelect} />
              )}
            </div>
          ))
        ) : (
          <p className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-gray-400">
            No timeline blocks received for this day.
          </p>
        )}
      </div>
    </section>
  );
}
