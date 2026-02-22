"use client";

import PlaceIcon from "@/components/PlaceIcon";
import { PlaceActivity } from "@/types/itinerary";

interface PlaceCardProps {
  place: PlaceActivity;
  onSelect: (place: PlaceActivity) => void;
}

export default function PlaceCard({ place, onSelect }: PlaceCardProps) {
  const mapUrl = `https://www.google.com/maps?q=${encodeURIComponent(
    place.place_name,
  )}`;

  return (
    <article
      onClick={() => onSelect(place)}
      className="
        cursor-pointer
        rounded-xl sm:rounded-2xl
        border border-white/10
        bg-gradient-to-br from-gray-900 to-gray-800
        p-3 sm:p-4
        shadow-md sm:shadow-lg
        transition-all duration-300
        sm:hover:scale-[1.02]
        sm:hover:border-cyan-400/50
        sm:hover:shadow-cyan-400/20
        w-full
        max-w-full
      "
    >
      {/* Header Row */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="rounded-full bg-cyan-500/10 px-2 sm:px-3 py-1 text-[11px] sm:text-xs font-medium text-cyan-300">
          {place.time}
        </p>

        <span className="rounded-full bg-gray-700 px-2 sm:px-3 py-1 text-[11px] sm:text-xs font-medium text-gray-300">
          Place
        </span>
      </div>

      {/* Icon */}
      <div className="mt-3 sm:mt-4 flex justify-center sm:justify-start">
        <PlaceIcon placeName={place.place_name} size="lg" />
      </div>

      {/* Title */}
      <h4 className="mt-3 sm:mt-4 text-base sm:text-lg font-semibold text-white leading-snug">
        {place.place_name}
      </h4>

      {/* Description */}
      <p className="mt-2 text-xs sm:text-sm text-gray-400 leading-relaxed">
        {place.reason_for_time_choice}
      </p>

      {/* Button */}
      <a
        href={mapUrl}
        target="_blank"
        rel="noopener noreferrer"
        onClick={(event) => event.stopPropagation()}
        className="
          mt-4
          block
          w-full
          rounded-lg
          bg-cyan-500
          py-2
          text-center
          text-xs sm:text-sm
          font-semibold
          text-black
          transition-colors duration-300
          hover:bg-cyan-400
        "
      >
        View on Map
      </a>
    </article>
  );
}