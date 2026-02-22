export interface PlannerRequest {
  home_city: string;
  destination_city: string;
  num_days: number;
  budget: number;
  interests: string[];
}

export interface PlaceActivity {
  time: string;
  place_name: string;
  reason_for_time_choice: string;
  image_url?: string;
  start_minutes?: number;
  end_minutes?: number;
  description?: string;
  area?: string;
  [key: string]: unknown;
}

export interface MealActivity {
  time: string;
  meal_type: string;
  outlet: string;
  signature_dish: string;
  area: string;
  reason_selected?: string;
  start_minutes?: number;
  end_minutes?: number;
  [key: string]: unknown;
}

export type TimelineItem = PlaceActivity | MealActivity;

export interface DayItinerary {
  day: number;
  title: string;
  day_time_window?: string;
  geographic_flow: string;
  walking_distance: string;
  timeline: TimelineItem[];
  estimated_day_cost?: number;
  [key: string]: unknown;
}

export interface HotelRecommendation {
  area: string;
  reason: string;
  [key: string]: unknown;
}

export interface Itinerary {
  title: string;
  hotel_recommendation: HotelRecommendation;
  days: DayItinerary[];
  total_estimated_cost?: number;
  within_budget?: boolean;
  budget_summary?: {
    total_budget?: number;
    estimated_spend?: number;
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

export interface ItineraryMetadata {
  total_latency_ms?: number;
  num_places_discovered?: number;
  num_clusters?: number;
  mandatory_top_places?: string[];
  budget?: number;
  destination_city?: string;
  [key: string]: unknown;
}

export interface FullItineraryResponse {
  itinerary: Itinerary;
  metadata: ItineraryMetadata;
}

export interface PlaceDetailRequest {
  time: string;
  place: string;
  reason_for_time_choice: string;
  image_url?: string;
  destination_city: string;
}

export interface PlaceDetailLanguageOutput {
  text: string;
  audio_file: string;
  audio_url: string;
}

export interface PlaceDetailResponse {
  place: string;
  destination_city: string;
  local_language: string;
  local_text?: string;
  constraints?: string[];
  special_cautions?: string[];
  outputs: {
    english?: PlaceDetailLanguageOutput;
    hindi?: PlaceDetailLanguageOutput;
    local?: PlaceDetailLanguageOutput;
  };
  cached: boolean;
}
