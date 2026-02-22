"use client";

import PlaceIcon from "@/components/PlaceIcon";
import { useEffect, useMemo, useRef, useState } from "react";
import { fetchPlaceDetailTTS } from "@/services/api";
import { PlaceActivity, PlaceDetailResponse } from "@/types/itinerary";

interface PlaceModalProps {
  place: PlaceActivity | null;
  destinationCity: string;
  onClose: () => void;
}

type LanguageKey = "english" | "hindi" | "local";

const LANGUAGE_LABELS: Record<LanguageKey, string> = {
  english: "English",
  hindi: "Hindi",
  local: "Local",
};

function SpeakerIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="currentColor"
      aria-hidden
    >
      <path d="M3 10v4h4l5 4V6L7 10H3zm13.5 2a3.5 3.5 0 0 0-2.06-3.2v6.4A3.5 3.5 0 0 0 16.5 12zm-2.06-8.2v2.08a7 7 0 0 1 0 12.24v2.08a9 9 0 0 0 0-16.4z" />
    </svg>
  );
}

export default function PlaceModal({
  place,
  destinationCity,
  onClose,
}: PlaceModalProps) {
  const [detailData, setDetailData] = useState<PlaceDetailResponse | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] =
    useState<LanguageKey>("english");
  const [typedText, setTypedText] = useState("");

  const typingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    return () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  useEffect(() => {
    if (!place) {
      return;
    }

    let active = true;

    fetchPlaceDetailTTS({
      time: place.time,
      place: place.place_name,
      reason_for_time_choice: place.reason_for_time_choice,
      image_url: place.image_url ?? "",
      destination_city: destinationCity,
    })
      .then((result) => {
        if (!active) {
          return;
        }
        setTypedText("");
        setDetailData(result);
      })
      .catch((requestError) => {
        if (!active) {
          return;
        }
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Failed to fetch place details.",
        );
      })
      .finally(() => {
        if (!active) {
          return;
        }
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [destinationCity, place]);

  const activeText = useMemo(() => {
    if (!detailData) {
      return "";
    }
    if (selectedLanguage === "local") {
      return detailData.local_text ?? detailData.outputs.local?.text ?? "";
    }
    return detailData.outputs[selectedLanguage]?.text ?? "";
  }, [detailData, selectedLanguage]);

  useEffect(() => {
    if (loading || !activeText) {
      return;
    }

    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
      typingIntervalRef.current = null;
    }

    const fullText = activeText;
    let cursor = 0;

    typingIntervalRef.current = setInterval(() => {
      cursor += 1;
      setTypedText(fullText.slice(0, cursor));
      if (cursor >= fullText.length && typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
        typingIntervalRef.current = null;
      }
    }, 18);

    return () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
        typingIntervalRef.current = null;
      }
    };
  }, [activeText, loading]);

  if (!place) {
    return null;
  }

  const mapQuery = encodeURIComponent(place.place_name);
  const mapUrl = `https://www.google.com/maps?q=${mapQuery}`;
  const embedUrl = `https://www.google.com/maps?q=${mapQuery}&output=embed`;

  const handlePlayAudio = (language: LanguageKey) => {
    const source = detailData?.outputs[language]?.audio_url;
    if (!source) {
      return;
    }

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }

    const nextAudio = new Audio(source);
    audioRef.current = nextAudio;
    void nextAudio.play();
  };

  const languageButtons = (Object.keys(LANGUAGE_LABELS) as LanguageKey[]).filter(
    (language) =>
      language === "local"
        ? Boolean(detailData?.local_text || detailData?.outputs.local?.text)
        : Boolean(detailData?.outputs[language]),
  );
  const audioLanguages = (["english", "hindi"] as LanguageKey[]).filter(
    (language) => Boolean(detailData?.outputs[language]?.audio_url),
  );
  const constraints = detailData?.constraints ?? [];
  const specialCautions = detailData?.special_cautions ?? [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md animate-fade-in">
      <div className="relative max-h-full w-full max-w-4xl overflow-y-auto rounded-2xl border border-white/10 bg-gray-900/90 shadow-2xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-white/10 bg-gray-900/90 p-4 backdrop-blur-md">
          <div>
            <h2 className="text-xl font-semibold text-white">
              {place.place_name}
            </h2>
            <p className="mt-1 text-sm text-cyan-300">
              Scheduled at {place.time}
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-full bg-gray-800 p-2 text-white transition-colors duration-300 hover:bg-gray-700"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="grid gap-6 p-4 lg:grid-cols-2">
          <div className="space-y-4">
            <div className="rounded-xl border border-white/10 bg-black/30 p-4">
              <PlaceIcon placeName={place.place_name} size="lg" />
            </div>

            <div className="rounded-xl border border-white/10 bg-black/30 p-4">
              <p className="text-sm text-gray-300">
                {place.reason_for_time_choice}
              </p>
            </div>

            <iframe
              title={place.place_name}
              src={embedUrl}
              className="h-48 w-full rounded-xl border border-white/10 sm:h-60"
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
            />

            {constraints.length ? (
              <div className="rounded-xl border border-yellow-400/25 bg-yellow-500/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-yellow-200">
                  Constraints
                </p>
                <ul className="mt-2 space-y-1.5 text-sm text-yellow-100/90">
                  {constraints.map((constraint, index) => (
                    <li key={`constraint-${index}`}>• {constraint}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            {specialCautions.length ? (
              <div className="rounded-xl border border-rose-400/25 bg-rose-500/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-rose-200">
                  Special Cautions
                </p>
                <ul className="mt-2 space-y-1.5 text-sm text-rose-100/90">
                  {specialCautions.map((caution, index) => (
                    <li key={`caution-${index}`}>• {caution}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            <a
              href={mapUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block w-full rounded-lg bg-cyan-500 py-2.5 text-center text-sm font-semibold text-black transition-colors duration-300 hover:bg-cyan-400"
            >
              Open in Google Maps
            </a>
          </div>

          <div className="rounded-xl border border-cyan-400/20 bg-gradient-to-b from-cyan-500/10 to-transparent p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
                Local Story Narration
              </p>
              {!loading && detailData ? (
                <span
                  className={`rounded-full border px-2 py-0.5 text-[11px] ${
                    detailData.cached
                      ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-200"
                      : "border-sky-400/30 bg-sky-500/10 text-sky-200"
                  }`}
                >
                  {detailData.cached ? "Cached" : "Fresh"}
                </span>
              ) : null}
            </div>

            {loading && (
              <div className="mt-4 rounded-xl bg-gray-800/50 p-4 text-center">
                <p className="text-sm text-gray-300">
                  Getting the local information...
                </p>
                <div className="mt-3 flex justify-center gap-2">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300"></span>
                  <span
                    className="h-2 w-2 animate-pulse rounded-full bg-cyan-300"
                    style={{ animationDelay: "150ms" }}
                  ></span>
                  <span
                    className="h-2 w-2 animate-pulse rounded-full bg-cyan-300"
                    style={{ animationDelay: "300ms" }}
                  ></span>
                </div>
              </div>
            )}

            {error && (
              <p className="mt-4 rounded-xl border border-red-500/30 bg-red-500/20 p-3 text-sm text-red-300">
                {error}
              </p>
            )}

            {!loading && detailData && (
              <>
                <div className="mt-4 flex flex-wrap gap-2">
                  {languageButtons.map((language) => (
                    <button
                      key={language}
                      onClick={() => {
                        setSelectedLanguage(language);
                        setTypedText("");
                      }}
                      className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors duration-300 ${
                        selectedLanguage === language
                          ? "bg-cyan-500 text-black"
                          : "bg-gray-700 text-white hover:bg-gray-600"
                      }`}
                    >
                      {language === "local" && detailData.local_language
                        ? detailData.local_language
                        : LANGUAGE_LABELS[language]}
                    </button>
                  ))}
                </div>

                <div className="mt-4 min-h-[120px] rounded-xl bg-black/30 p-4">
                  <p className="text-sm leading-relaxed text-gray-200">
                    {typedText}
                  </p>
                </div>

                <div className="mt-4 space-y-2">
                  {audioLanguages.map((language) => (
                    <div
                      key={`audio-${language}`}
                      className="flex items-center justify-between rounded-lg bg-gray-800/50 p-2.5"
                    >
                      <p className="text-sm text-gray-300">
                        {language === "local" && detailData.local_language
                          ? detailData.local_language
                          : LANGUAGE_LABELS[language]}{" "}
                        Audio
                      </p>
                      <button
                        onClick={() => handlePlayAudio(language)}
                        className="flex items-center gap-2 rounded-md bg-cyan-500/20 px-3 py-1.5 text-xs font-semibold text-cyan-300 transition-colors duration-300 hover:bg-cyan-500/30"
                      >
                        <SpeakerIcon />
                        <span>Play</span>
                      </button>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
