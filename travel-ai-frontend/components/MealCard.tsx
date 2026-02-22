"use client";

import { MealActivity } from "@/types/itinerary";

interface MealCardProps {
  meal: MealActivity;
}

export default function MealCard({ meal }: MealCardProps) {
  return (
    <article className="rounded-2xl border border-amber-300/35 bg-[#1f1a12] p-3.5 shadow-[0_10px_30px_rgba(0,0,0,0.4)] transition-all duration-300 hover:scale-[1.02] sm:p-4">
      <div className="flex flex-wrap items-center justify-between gap-2.5">
        <p className="text-sm font-semibold text-amber-100">{meal.meal_type}</p>
        <span className="rounded-full border border-amber-200/25 bg-amber-200/10 px-2 py-1 text-xs text-amber-100">
          {meal.time}
        </span>
      </div>
      <p className="mt-2 text-sm font-semibold text-white sm:text-base">{meal.outlet}</p>
      <p className="mt-1 text-xs text-amber-100/90 sm:text-sm">
        Signature Dish: {meal.signature_dish}
      </p>
      <p className="mt-1 text-xs text-amber-100/90 sm:text-sm">Area: {meal.area}</p>
      {meal.reason_selected ? (
        <p className="mt-2 text-[11px] text-amber-100/80 sm:text-xs">{meal.reason_selected}</p>
      ) : null}
    </article>
  );
}
