import {
  FullItineraryResponse,
  PlaceDetailRequest,
  PlaceDetailResponse,
  PlannerRequest,
} from "@/types/itinerary";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error("NEXT_PUBLIC_API_BASE_URL is not defined");
}

const API_URL = `${API_BASE_URL}/planner/full-itinerary`;
const PLACE_DETAIL_TTS_URL = `${API_BASE_URL}/planner/place-detail-tts`;

function toArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? (value as Record<string, unknown>[]) : [];
}

function toStringValue(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function toNumberValue(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function toBooleanValue(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function parseStartTime(raw: string): number {
  const start = raw.split("-")[0]?.trim();
  if (!start) return Number.MAX_SAFE_INTEGER;
  const [h, m] = start.split(":").map(Number);
  if (!Number.isFinite(h) || !Number.isFinite(m)) return Number.MAX_SAFE_INTEGER;
  return h * 60 + m;
}

function parseEndTime(raw: string): number {
  const end = raw.split("-")[1]?.trim();
  if (!end) return Number.MAX_SAFE_INTEGER;
  const [h, m] = end.split(":").map(Number);
  if (!Number.isFinite(h) || !Number.isFinite(m)) return Number.MAX_SAFE_INTEGER;
  return h * 60 + m;
}

function normalizeResponse(payload: unknown): FullItineraryResponse {
  const root =
    payload && typeof payload === "object"
      ? (payload as Record<string, unknown>)
      : {};
  const itineraryRaw =
    root.itinerary && typeof root.itinerary === "object"
      ? (root.itinerary as Record<string, unknown>)
      : {};
  const rawDays = toArray(
    itineraryRaw.days ??
      itineraryRaw.day_plans ??
      itineraryRaw.plan ??
      itineraryRaw.schedule,
  );

  const normalizedDays = rawDays.map((day, index) => {
    const scheduleBlocks = toArray(day.schedule_blocks ?? day.timeline ?? day.activities);
    const foodHalts = toArray(day.food_halts);
    const normalizedPlaces = scheduleBlocks.map((block) => ({
      ...block,
      time: toStringValue(block.time, ""),
      start_minutes: parseStartTime(toStringValue(block.time, "")),
      end_minutes: parseEndTime(toStringValue(block.time, "")),
      place_name: toStringValue(
        block.place_name ?? block.place,
        "Planned stop",
      ),
      reason_for_time_choice: toStringValue(
        block.reason_for_time_choice,
        "Recommended by itinerary engine.",
      ),
      image_url: toStringValue(block.image_url, ""),
    }));
    const normalizedMeals = foodHalts.map((halt) => ({
      ...halt,
      time: toStringValue(halt.time, ""),
      start_minutes: parseStartTime(toStringValue(halt.time, "")),
      end_minutes: parseEndTime(toStringValue(halt.time, "")),
      meal_type: toStringValue(halt.meal_type, "Meal"),
      outlet: toStringValue(halt.outlet, "Recommended outlet"),
      signature_dish: toStringValue(halt.signature_dish, "Chef special"),
      area: toStringValue(halt.area, "City Center"),
      reason_selected: toStringValue(halt.reason_selected, ""),
    }));
    const timeline = [...normalizedPlaces, ...normalizedMeals].sort(
      (a, b) =>
        toNumberValue(a.start_minutes, Number.MAX_SAFE_INTEGER) -
        toNumberValue(b.start_minutes, Number.MAX_SAFE_INTEGER),
    );
    const walkingKm = toNumberValue(day.total_walking_km_estimate, NaN);

    return {
      ...day,
      day: toNumberValue(day.day, index + 1),
      title: toStringValue(day.title, `Day ${index + 1}`),
      day_time_window: toStringValue(day.day_time_window, ""),
      geographic_flow: toStringValue(
        day.geographic_flow ?? day.geographic_flow_explanation,
        "Optimized local flow",
      ),
      walking_distance:
        Number.isFinite(walkingKm) && walkingKm > 0 ? `${walkingKm.toFixed(1)} km` : "N/A",
      timeline,
      estimated_day_cost: toNumberValue(day.estimated_day_cost, 0),
    };
  });

  const hotelRaw =
    itineraryRaw.hotel_recommendation &&
    typeof itineraryRaw.hotel_recommendation === "object"
      ? (itineraryRaw.hotel_recommendation as Record<string, unknown>)
      : {};

  const metadata =
    root.metadata && typeof root.metadata === "object"
      ? (root.metadata as Record<string, unknown>)
      : {};

  return {
    itinerary: {
      ...itineraryRaw,
      title: toStringValue(itineraryRaw.title, "Your AI Travel Itinerary"),
      hotel_recommendation: {
        area: toStringValue(hotelRaw.area, "Central Area"),
        reason: toStringValue(
          hotelRaw.reason,
          "Chosen for connectivity and access to key places.",
        ),
      },
      days: normalizedDays,
      total_estimated_cost: toNumberValue(itineraryRaw.total_estimated_cost, 0),
      within_budget: toBooleanValue(itineraryRaw.within_budget, false),
    },
    metadata,
  };
}

export async function fetchFullItinerary(
  payload: PlannerRequest,
): Promise<FullItineraryResponse> {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Failed to generate itinerary.");
  }

  const data = (await response.json()) as unknown;
  return normalizeResponse(data);
}

function withAbsoluteAudioUrl(url: string): string {
  if (!url) {
    return "";
  }
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  return `${API_BASE_URL}${url}`;
}

function toStringArray(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean);
  }
  if (typeof value === "string" && value.trim()) {
    return [value.trim()];
  }
  return [];
}

function normalizePlaceDetailResponse(payload: unknown): PlaceDetailResponse {
  const root =
    payload && typeof payload === "object"
      ? (payload as Record<string, unknown>)
      : {};
  const rawOutputs =
    root.outputs && typeof root.outputs === "object"
      ? (root.outputs as Record<string, unknown>)
      : {};

  const normalizeLanguageOutput = (value: unknown) => {
    if (!value || typeof value !== "object") {
      return undefined;
    }
    const output = value as Record<string, unknown>;
    return {
      text: toStringValue(output.text, ""),
      audio_file: toStringValue(output.audio_file, ""),
      audio_url: withAbsoluteAudioUrl(toStringValue(output.audio_url, "")),
    };
  };

  return {
    place: toStringValue(root.place, ""),
    destination_city: toStringValue(root.destination_city, ""),
    local_language: toStringValue(root.local_language, "Local"),
    local_text: toStringValue(root.local_text, ""),
    constraints: toStringArray(root.constraints),
    special_cautions: toStringArray(root.special_cautions),
    outputs: {
      english: normalizeLanguageOutput(rawOutputs.english),
      hindi: normalizeLanguageOutput(rawOutputs.hindi),
      local: normalizeLanguageOutput(rawOutputs.local),
    },
    cached: toBooleanValue(root.cached, false),
  };
}

export async function fetchPlaceDetailTTS(
  payload: PlaceDetailRequest,
): Promise<PlaceDetailResponse> {
  const response = await fetch(PLACE_DETAIL_TTS_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Failed to fetch place details.");
  }

  const data = (await response.json()) as unknown;
  return normalizePlaceDetailResponse(data);
}
