"use client";

import DayCard from "@/components/DayCard";
import HotelCard from "@/components/HotelCard";
import { FullItineraryResponse, PlaceActivity } from "@/types/itinerary";

interface ItineraryDashboardProps {
  data: FullItineraryResponse;
  selectedDayIndex: number;
  onSelectDay: (index: number) => void;
  onSelectPlace: (place: PlaceActivity) => void;
}

export default function ItineraryDashboard({
  data,
  selectedDayIndex,
  onSelectDay,
  onSelectPlace,
}: ItineraryDashboardProps) {
  const { itinerary, metadata } = data;

  const days = Array.isArray(itinerary.days) ? itinerary.days : [];
  const currentDay = days[selectedDayIndex] ?? days[0];

  const topPlaces = Array.isArray(metadata?.mandatory_top_places)
    ? metadata.mandatory_top_places
    : [];

  const formatCurrency = (value: number | undefined) =>
    typeof value === "number" && Number.isFinite(value)
      ? value.toLocaleString("en-IN", {
          style: "currency",
          currency: "INR",
          maximumFractionDigits: 0,
        })
      : "N/A";

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-950 via-black to-gray-900 text-white">
      <main className="flex-1 p-4 sm:p-6 lg:p-8">
        <div className="mx-auto grid w-full max-w-7xl grid-cols-1 gap-6 lg:grid-cols-12">
          
          {/* ================= SIDEBAR ================= */}
          <aside className="space-y-6 lg:col-span-4">
            
            {/* Overview */}
            <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-5 shadow-lg">
              <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
                Overview
              </p>
              <h1 className="mt-2 text-xl sm:text-2xl font-bold text-white">
                {itinerary.title}
              </h1>
              <p className="mt-2 text-sm text-gray-300">
                Generated route across {days.length} day(s) with intelligent sequencing.
              </p>
            </div>

            {/* Hotel */}
            <HotelCard hotel={itinerary.hotel_recommendation} />

            {/* Budget */}
            <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-5 shadow-lg">
              <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
                Budget Summary
              </p>

              <div className="mt-3 space-y-2">
                <p className="text-sm text-gray-300">
                  Planned Budget:{" "}
                  <span className="font-semibold text-white">
                    {formatCurrency(
                      Number(
                        metadata?.budget ??
                          itinerary?.budget_summary?.total_budget,
                      ),
                    )}
                  </span>
                </p>

                <p className="text-sm text-gray-300">
                  Estimated Spend:{" "}
                  <span className="font-semibold text-white">
                    {formatCurrency(
                      Number(
                        itinerary?.total_estimated_cost ??
                          itinerary?.budget_summary?.estimated_spend,
                      ),
                    )}
                  </span>
                </p>
              </div>

              <p
                className={`mt-4 inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${
                  itinerary?.within_budget
                    ? "bg-emerald-500/10 text-emerald-300"
                    : "bg-red-500/10 text-red-300"
                }`}
              >
                <span
                  className={`h-2 w-2 rounded-full ${
                    itinerary?.within_budget
                      ? "bg-emerald-500"
                      : "bg-red-500"
                  }`}
                />
                {itinerary?.within_budget ? "Within budget" : "Over budget"}
              </p>
            </div>

            {/* Planner Insights */}
            <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-5 shadow-lg">
              <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
                Planner Insights
              </p>

              <div className="mt-3 space-y-2 text-sm">
                <p>
                  Places Discovered:{" "}
                  <span className="font-semibold text-white">
                    {metadata?.num_places_discovered ?? "N/A"}
                  </span>
                </p>

                <p>
                  Clusters:{" "}
                  <span className="font-semibold text-white">
                    {metadata?.num_clusters ?? "N/A"}
                  </span>
                </p>

                <p>
                  Latency:{" "}
                  <span className="font-semibold text-white">
                    {typeof metadata?.total_latency_ms === "number"
                      ? `${(metadata.total_latency_ms / 1000).toFixed(1)}s`
                      : "N/A"}
                  </span>
                </p>
              </div>

              {topPlaces.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
                    Top Places
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {topPlaces.map((place) => (
                      <span
                        key={place}
                        className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-300"
                      >
                        {place}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </aside>

          {/* ================= MAIN SECTION ================= */}
          <section className="flex flex-col gap-6 lg:col-span-8">
            
            {/* Day Selector */}
            <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-3 shadow-lg">
              <div className="flex snap-x snap-mandatory gap-2 overflow-x-auto">
                {days.map((day, index) => (
                  <button
                    key={`${day.day}-${index}`}
                    onClick={() => onSelectDay(index)}
                    className={`shrink-0 snap-start rounded-full px-4 py-2 text-sm font-medium transition-colors duration-300 ${
                      index === selectedDayIndex
                        ? "bg-cyan-500 text-black"
                        : "bg-gray-800/50 text-gray-300 hover:bg-gray-700/50"
                    }`}
                  >
                    Day {day.day || index + 1}
                  </button>
                ))}
              </div>
            </div>

            {/* Estimated Day Cost */}
            {currentDay?.estimated_day_cost && (
              <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-4 text-sm text-gray-300 shadow-lg">
                Estimated Day Cost:{" "}
                <span className="font-semibold text-white">
                  {formatCurrency(currentDay.estimated_day_cost)}
                </span>
              </div>
            )}

            {/* Day Content */}
            {currentDay && (
              <div>
                <DayCard
                  day={currentDay}
                  onPlaceSelect={onSelectPlace}
                />
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}