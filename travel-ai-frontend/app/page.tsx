"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ItineraryDashboard from "@/components/ItineraryDashboard";
import PlannerModal from "@/components/PlannerModal";
import PlannerNavbar from "@/components/PlannerNavbar";
import PlaceModal from "@/components/PlaceModal";
import ProcessingScreen from "@/components/ProcessingScreen";
import { fetchFullItinerary } from "@/services/api";
import {
  FullItineraryResponse,
  PlaceActivity,
  PlannerRequest,
} from "@/types/itinerary";

const STORAGE_KEY = "travel_ai_state_v1";

type PlannerView = "input" | "itinerary";

interface PersistedState {
  itineraryData: FullItineraryResponse | null;
  selectedDayIndex: number;
  activeView: PlannerView;
}

export default function Home() {
  const router = useRouter();
  const [isHydrated, setIsHydrated] = useState(false);
  const [showModal, setShowModal] = useState(true);
  const [loading, setLoading] = useState(false);
  const [itineraryData, setItineraryData] =
    useState<FullItineraryResponse | null>(null);
  const [selectedPlace, setSelectedPlace] = useState<PlaceActivity | null>(
    null,
  );
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<PlannerView>("input");

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        setShowModal(true);
        setActiveView("input");
        return;
      }

      const parsed = JSON.parse(raw) as PersistedState;

      if (parsed?.itineraryData) {
        setItineraryData(parsed.itineraryData);
        setSelectedDayIndex(parsed.selectedDayIndex ?? 0);
        setActiveView(parsed.activeView ?? "itinerary");
        setShowModal(parsed.activeView === "input");
      } else {
        setShowModal(true);
        setActiveView("input");
      }
    } finally {
      setIsHydrated(true);
    }
  }, []);

  useEffect(() => {
    if (!isHydrated) return;

    const payload: PersistedState = {
      itineraryData,
      selectedDayIndex,
      activeView,
    };

    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }, [activeView, isHydrated, itineraryData, selectedDayIndex]);

  const handleSubmit = async (payload: PlannerRequest) => {
    setLoading(true);
    setShowModal(false);
    setError(null);

    try {
      const data = await fetchFullItinerary(payload);
      setItineraryData({
        ...data,
        metadata: {
          ...data.metadata,
          destination_city: payload.destination_city,
        },
      });
      setSelectedDayIndex(0);
      setActiveView("itinerary");
    } catch (err) {
      setError("Unable to generate itinerary.");
      setActiveView("input");
      setShowModal(true);
    } finally {
      setLoading(false);
    }
  };

  if (!isHydrated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black text-gray-300">
        Initializing planner...
      </div>
    );
  }

  if (loading) return <ProcessingScreen />;

  return (
    <div className="relative min-h-screen overflow-hidden bg-black text-white">
      
      {/* Background Glow */}
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div className="absolute left-0 top-0 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-blue-500/20 blur-3xl" />
      </div>

      <PlannerNavbar
        activeView={activeView}
        hasItinerary={Boolean(itineraryData)}
        onInputClick={() => {
          setActiveView("input");
          setShowModal(true);
        }}
        onItineraryClick={() => {
          if (!itineraryData) {
            setShowModal(true);
            return;
          }
          setActiveView("itinerary");
          setShowModal(false);
        }}
        onFinalImagesClick={() => router.push("/final-images")}
      />

      <PlannerModal
        open={showModal}
        loading={loading}
        error={error}
        onSubmit={handleSubmit}
      />

      <main className="relative">
        {itineraryData && activeView === "itinerary" ? (
          <>
            <ItineraryDashboard
              data={itineraryData}
              selectedDayIndex={selectedDayIndex}
              onSelectDay={setSelectedDayIndex}
              onSelectPlace={setSelectedPlace}
            />

            <PlaceModal
              place={selectedPlace}
              destinationCity={String(
                itineraryData.metadata.destination_city ?? "",
              )}
              onClose={() => setSelectedPlace(null)}
            />
          </>
        ) : (
          <section className="flex min-h-[calc(100vh-80px)] items-center justify-center p-6">
            <div className="w-full max-w-4xl rounded-3xl border border-white/10 bg-white/5 p-10 text-center shadow-2xl backdrop-blur-xl">
              
              <p className="text-xs uppercase tracking-widest text-cyan-400">
                Intelligent Travel OS
              </p>

              <h1 className="mt-6 text-4xl font-bold leading-tight sm:text-5xl">
                Design Journeys<br />With Geographic Intelligence
              </h1>

              <p className="mx-auto mt-6 max-w-2xl text-gray-400 sm:text-lg">
                Our AI clusters landmarks, optimizes routes, balances budget,
                and aligns cultural timing — creating a structured, realistic,
                and premium travel experience.
              </p>

              <button
                onClick={() => {
                  setShowModal(true);
                  setActiveView("input");
                }}
                className="mt-10 rounded-full bg-cyan-500 px-10 py-3 text-lg font-semibold text-black transition-all duration-300 hover:scale-105 hover:bg-cyan-400"
              >
                Start Planning
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}