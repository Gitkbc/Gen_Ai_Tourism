import json
import re
import time
from typing import Dict, Any, List

from travel_ai.services.llm_service import generate_content
from travel_ai.utils.logger import get_logger
from travel_ai.services.data_loader import load_city_dataset

logger = get_logger("agents")


# ==========================================================
# JSON CLEANER
# ==========================================================

def _clean_json(raw: str) -> Dict[str, Any]:
    """
    Cleans and parses a string to extract a JSON object.
    """
    raw = raw.strip().replace("```json", "").replace("```", "").strip()

    # Find the JSON object within the string
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_match:
        raise ValueError(f"No valid JSON object found in the raw string:\n{raw}")

    json_str = json_match.group(0)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {json_str}")
        raise ValueError(f"Invalid JSON format: {e}") from e


# ==========================================================
# DISCOVERY AGENT (INDIA SPECIFIC)
# ==========================================================

SYSTEM_PROMPT_DISCOVERY = """
You are an Indian local travel intelligence expert with 20+ years of lived experience.
You think like a heritage researcher, a local resident, and someone who regularly walks old city lanes.
You are given a list of verified places; do NOT repeat them. Your job is to suggest additional culturally meaningful places within a 25km radius.

Prioritize:
- Old city cores (peths, pols, chowks, bazaars)
- Historic temples (>100 years old)
- Forts and hill viewpoints
- River ghats and stepwells
- Local markets
- Sites related to the freedom movement
- Traditional food streets

Avoid:
- Malls and generic modern attractions
- Duplicate entries
- Locations outside the 25km radius unless they are of major historical significance.

Return STRICT JSON in the following format:
{
  "additional_places": [
    {
      "name": "string",
      "lat": float,
      "lng": float,
      "category": "string",
      "rating": float,
      "ticket_price": float,
      "speciality": "string",
      "local_note": "string",
      "best_time": "string",
      "effort_type": "string",
      "image_url": "string"
    }
  ]
}
JSON only.
"""


async def discovery_agent(request_data: Dict[str, Any]) -> Dict[str, Any]:
    city = request_data["destination_city"]
    city_data = load_city_dataset(city)
    seed_places = city_data.get("places", [])

    llm_input = {
        "city": city,
        "verified_places": seed_places,
        "user_interests": request_data.get("interests", []),
    }

    start = time.time()
    response = await generate_content(SYSTEM_PROMPT_DISCOVERY, json.dumps(llm_input))
    parsed = _clean_json(response)
    additional_places = parsed.get("additional_places", [])

    # Deduplicate places to ensure no overlaps
    seed_names = {p["name"].strip().lower() for p in seed_places}
    merged_places = seed_places.copy()
    for place in additional_places:
        name = place.get("name", "").strip().lower()
        if name and name not in seed_names:
            merged_places.append(place)
            seed_names.add(name)

    logger.info(f"Discovery latency: {(time.time() - start) * 1000:.2f}ms")
    return {"places": merged_places}


# ==========================================================
# CLUSTER PRIORITY AGENT (INDIA LOGIC)
# ==========================================================

async def cluster_priority_agent(
    clusters: List[List[Dict[str, Any]]], user_interests: List[str], num_days: int
) -> Dict[str, Any]:
    system_prompt = """
You are a senior Indian city guide. Your task is to organize clusters of places into a daily schedule.

Rules:
1. Do NOT mix high-effort outskirts activities with walkable old city heritage in the same day.
2. Schedule temples for the morning.
3. Schedule forts and treks for the early morning.
4. Schedule markets for the evening.
5. Plan routes to avoid cross-city traffic and improve efficiency.
6. Adhere strictly to the number of days specified.
7. Group geographically coherent areas together.

Return STRICT JSON in the following format:
{
  "days": [
    {
      "day": int,
      "theme": "string",
      "logic": "string",
      "places": [
        {
          "name": "string",
          "suggested_time": "Morning | Afternoon | Evening",
          "reason": "string"
        }
      ],
      "extra_constraints": ["string"]
    }
  ]
}
"""
    response = await generate_content(
        system_prompt,
        json.dumps(
            {"clusters": clusters, "user_interests": user_interests, "num_days": num_days}
        ),
    )
    return _clean_json(response)


# ==========================================================
# OPTIMIZATION AGENT
# ==========================================================

async def optimization_agent(
    discovery_output: Dict[str, Any], budget_feedback: Dict[str, Any]
) -> Dict[str, Any]:
    system_prompt = """
You are an Indian travel budget optimizer. Your goal is to refine a list of places to fit a budget.

Rules:
- Do NOT remove culturally critical landmarks.
- Prioritize removing optional modern spots first.
- Maintain the geographic coherence of the itinerary.
- Adhere strictly to the budget constraints.

Return STRICT JSON in the following format:
{
  "optimized_places": [
    {
      "name": "string",
      "category": "string",
      "estimated_cost": float,
      "reason_for_inclusion": "string"
    }
  ]
}
"""
    response = await generate_content(
        system_prompt,
        json.dumps(
            {"places": discovery_output.get("places", []), "budget_feedback": budget_feedback}
        ),
    )
    return _clean_json(response)


# ==========================================================
# FINAL ITINERARY AGENT (INDIA SPECIFIC)
# ==========================================================

async def final_itinerary_agent(
    priority_output: Dict,
    discovery_places: List[Dict],
    original_request: Dict,
    transport_estimate: Dict,
    food_options: List[Dict],
) -> Dict:
    system_prompt = """
You are a strict Indian local heritage itinerary architect.

CRITICAL RULES:
1. NEVER schedule two high-effort outskirts activities on the same day.
2. If a hill is near the city center (e.g., Parvati Hill), combine it with visits to nearby markets.
3. Isolate major trek-forts (e.g., Sinhagad) on a separate day.
4. Add a minimum of one food halt per day.
5. Limit sightseeing to a maximum of four places per day.
6. Use real, publicly accessible image URLs (from Wikipedia, TripAdvisor, or official sites only).
7. Follow the Indian daily rhythm: Morning (temples, forts), Afternoon (museums, heritage sites), Evening (markets, bazaars).
8. A note on temple dress code is mandatory.
9. Do NOT invent new places.
10. Calculate daily cost as: sum of ticket prices + ₹700 for food + ₹700 for local transport.

Return STRICT JSON in the following format:
{
  "itinerary": {
    "title": "string",
    "overview": "string",
    "days": [
      {
        "day": int,
        "title": "string",
        "logic": "string",
        "schedule": "string",
        "places_visited": [
          {
            "name": "string",
            "image_url": "string",
            "category": "string",
            "best_time": "string",
            "ticket_price": float,
            "speciality": "string"
          }
        ],
        "food_halts": [
          {
            "time": "string",
            "outlet": "string",
            "cuisine": "string",
            "price_level": "string",
            "area": "string",
            "highlights": ["string"],
            "booking_tips": "string",
            "source_url": "string"
          }
        ],
        "estimated_day_cost": float,
        "extra_notes": ["string"]
      }
    ],
    "total_estimated_cost": float,
    "transport_summary": {},
    "within_budget": true
  }
}
"""
    input_data = {
        "priority": priority_output,
        "places": discovery_places,
        "food_options": food_options,
        "request": original_request,
        "transport": transport_estimate,
    }

    # Log the payload for debugging
    try:
        user_prompt_json = json.dumps(input_data, indent=2)
        logger.debug(f"Final itinerary agent payload:\n{user_prompt_json}")
    except TypeError as e:
        logger.error(f"Failed to serialize input_data to JSON: {e}")
        # Optionally, log the problematic data structure if possible
        # logger.error(f"Input data structure: {input_data}")
        raise

    response = await generate_content(system_prompt, user_prompt_json)
    return _clean_json(response)


# ==========================================================
# LOGISTICS ITINERARY AGENT
# ==========================================================

async def itinerary_agent(
    priority_plan: Dict[str, Any], original_request: Dict[str, Any]
) -> Dict[str, Any]:
    system_prompt = f"""
You are a Senior Indian Travel Logistics Planner.

Budget: {original_request.get("budget", 25000)} INR.

Rules:
1. Deduct a 15% emergency buffer from the budget.
2. Account for traffic variability in India.
3. Respect temple dress codes.
4. Avoid unrealistic time compression.
5. Use realistic Indian entry fees.

Return STRICT JSON in the following format:
{{
  "total_budget_breakdown": {{
    "transport_est": float,
    "food_and_entry_est": float,
    "remaining_buffer": float
  }},
  "days": [
    {{
      "day": int,
      "cluster_logic": "string",
      "activities": [
        {{
          "time_slot": "string",
          "place_name": "string",
          "entry_fee": float,
          "clothing_restriction": "string",
          "travel_note": "string",
          "activity_description": "string"
        }}
      ]
    }}
  ]
}}
"""
    response = await generate_content(
        system_prompt,
        json.dumps({"priority_plan": priority_plan, "original_request": original_request}),
    )
    return _clean_json(response)