"use client";

import { HotelRecommendation } from "@/types/itinerary";

interface HotelCardProps {
  hotel: HotelRecommendation;
}

export default function HotelCard({ hotel }: HotelCardProps) {
  const searchUrl = `https://www.google.com/maps/search/hotels+near+${encodeURIComponent(hotel.area)}`;

  return (
    <section className="rounded-2xl border border-cyan-300/20 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 p-4 text-center shadow-xl transition-all duration-300 hover:scale-[1.02] sm:p-6">
      <h3 className="text-lg font-semibold text-white sm:text-xl">Hotel Recommendation</h3>
      <p className="mt-3 text-base text-cyan-100">Area: {hotel.area}</p>
      <p className="mt-2 text-sm text-gray-300">{hotel.reason}</p>

      <a
        href={searchUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-5 inline-flex w-full justify-center rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-black transition-all duration-300 hover:scale-[1.02] hover:bg-cyan-400 sm:w-auto"
      >
        Search Nearby Hotels
      </a>
    </section>
  );
}
