"use client";

import { FormEvent, useMemo, useState } from "react";
import { PlannerRequest } from "@/types/itinerary";

interface PlannerModalProps {
  open: boolean;
  loading: boolean;
  error: string | null;
  onSubmit: (payload: PlannerRequest) => Promise<void>;
}

const DEFAULT_FORM: PlannerRequest = {
  home_city: "Mumbai",
  destination_city: "Pune",
  num_days: 3,
  budget: 25000,
  interests: ["history", "architecture"],
};

export default function PlannerModal({
  open,
  loading,
  error,
  onSubmit,
}: PlannerModalProps) {
  const [homeCity, setHomeCity] = useState(DEFAULT_FORM.home_city);
  const [destinationCity, setDestinationCity] = useState(
    DEFAULT_FORM.destination_city,
  );
  const [numDays, setNumDays] = useState(DEFAULT_FORM.num_days);
  const [budget, setBudget] = useState(DEFAULT_FORM.budget);
  const [interestsText, setInterestsText] = useState(
    DEFAULT_FORM.interests.join(", "),
  );

  const interestsPreview = useMemo(
    () =>
      interestsText
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    [interestsText],
  );

  if (!open) return null;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    await onSubmit({
      home_city: homeCity.trim(),
      destination_city: destinationCity.trim(),
      num_days: Math.max(1, Number(numDays) || DEFAULT_FORM.num_days),
      budget: Number(budget),
      interests: interestsPreview,
    });
  };

  const estimatedPerDay =
    numDays > 0 ? Math.round(Number(budget) / Number(numDays)) : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-md">
      <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl border border-white/10 bg-gradient-to-br from-white/5 to-white/10 p-6 shadow-2xl backdrop-blur-xl sm:p-10">
        
        {/* Header */}
        <div>
          <p className="text-xs uppercase tracking-widest text-cyan-400">
            Intelligent Travel Planner
          </p>
          <h1 className="mt-3 text-2xl font-semibold text-white sm:text-3xl">
            Design Your Journey
          </h1>
          <p className="mt-2 text-sm text-gray-400 sm:text-base">
            Provide key details and our AI will optimize routes, timing, food,
            and budget intelligently.
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          
          {/* Cities */}
          <div className="grid gap-4 sm:grid-cols-2">
            <InputField
              label="Home City"
              value={homeCity}
              onChange={setHomeCity}
            />
            <InputField
              label="Destination City"
              value={destinationCity}
              onChange={setDestinationCity}
            />
          </div>

          {/* Days + Budget */}
          <div className="grid gap-4 sm:grid-cols-2">
            <InputField
              label="Number of Days"
              type="number"
              min={1}
              value={numDays}
              onChange={(val) => setNumDays(Number(val))}
            />

            <div className="space-y-2">
              <label className="text-sm text-gray-300">Budget (INR)</label>
              <input
                required
                min={1}
                type="number"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-white outline-none transition-all duration-300 focus:border-cyan-400"
              />
              {estimatedPerDay > 0 && (
                <p className="text-xs text-gray-400">
                  ≈ ₹{estimatedPerDay.toLocaleString("en-IN")} per day
                </p>
              )}
            </div>
          </div>

          {/* Interests */}
          <div className="space-y-2">
            <label className="text-sm text-gray-300">
              Interests (comma separated)
            </label>
            <input
              required
              value={interestsText}
              onChange={(event) => setInterestsText(event.target.value)}
              placeholder="history, architecture, food, temples"
              className="w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-white outline-none transition-all duration-300 focus:border-cyan-400"
            />

            {/* Preview Chips */}
            <div className="flex flex-wrap gap-2 pt-2">
              {interestsPreview.map((interest) => (
                <span
                  key={interest}
                  className="rounded-full border border-cyan-400/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200"
                >
                  {interest}
                </span>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <p className="rounded-lg border border-red-400/40 bg-red-500/10 px-4 py-2 text-sm text-red-300">
              {error}
            </p>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-500 px-4 py-3 font-semibold text-black transition-all duration-300 hover:scale-[1.02] hover:bg-cyan-400 disabled:opacity-60"
          >
            {loading ? (
              <>
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-black/30 border-t-black" />
                Generating Intelligent Plan...
              </>
            ) : (
              "Generate Smart Itinerary"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

/* Reusable Input */
function InputField({
  label,
  value,
  onChange,
  type = "text",
  min,
}: {
  label: string;
  value: string | number;
  onChange: (value: string) => void;
  type?: string;
  min?: number;
}) {
  return (
    <div className="space-y-2">
      <label className="text-sm text-gray-300">{label}</label>
      <input
        required
        type={type}
        min={min}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-white outline-none transition-all duration-300 focus:border-cyan-400"
      />
    </div>
  );
}