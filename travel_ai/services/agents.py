import json
import re
import time
from typing import Any, Dict, List

from travel_ai.services.data_loader import load_city_dataset
from travel_ai.services.llm_service import generate_content
from travel_ai.utils.logger import get_logger

logger = get_logger("agents")


def _clean_json(raw: str) -> Dict[str, Any]:
    raw = raw.strip().replace("```json", "").replace("```", "").strip()
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_match:
        raise ValueError(f"No valid JSON object found in the raw string:\n{raw}")

    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to decode JSON: {json_match.group(0)}")
        raise ValueError(f"Invalid JSON format: {exc}") from exc


def _canonical_name(name: str) -> str:
    return " ".join(str(name or "").strip().lower().split())


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _is_valid_lat_lng(place: Dict[str, Any]) -> bool:
    return isinstance(place.get("lat"), (int, float)) and isinstance(place.get("lng"), (int, float))


def rank_places_for_visit(
    places: List[Dict[str, Any]],
    user_interests: List[str],
    top_n: int = 4,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Rank discovered places and return mandatory top places.
    The top 4 are used as must-cover places in itinerary generation.
    """
    interest_tokens = [str(i).strip().lower() for i in user_interests if str(i).strip()]
    ranked: List[Dict[str, Any]] = []

    for place in places:
        name = str(place.get("name", "")).strip()
        if not name:
            continue
        category = str(place.get("category", "")).strip()
        rating = _safe_float(place.get("rating"), 4.0)
        text = f"{name} {category}".lower()

        interest_hits = sum(1 for token in interest_tokens if token in text)
        score = rating * 20 + (interest_hits * 8)

        ranked.append(
            {
                "name": name,
                "category": category,
                "rating": round(rating, 2),
                "score": round(score, 2),
            }
        )

    ranked.sort(key=lambda item: (item["score"], item["rating"]), reverse=True)
    mandatory = ranked[:max(top_n, 0)]
    return {"ranked_places": ranked, "mandatory_top_places": mandatory}


def _normalize_discovered_places(
    seed_places: List[Dict[str, Any]], additional_places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    merged_places: List[Dict[str, Any]] = []
    seen_names = set()

    for source in [seed_places, additional_places]:
        for place in source:
            name = str(place.get("name", "")).strip()
            canonical = _canonical_name(name)
            if not canonical or canonical in seen_names or not _is_valid_lat_lng(place):
                continue
            merged_places.append(
                {
                    "name": name,
                    "lat": _safe_float(place.get("lat")),
                    "lng": _safe_float(place.get("lng")),
                    "category": place.get("category", ""),
                    "rating": _safe_float(place.get("rating"), 0.0),
                    "ticket_price": _safe_float(place.get("ticket_price"), 0.0),
                    "speciality": place.get("speciality", ""),
                    "local_note": place.get("local_note", ""),
                    "best_time": place.get("best_time", ""),
                    "effort_type": place.get("effort_type", ""),
                    "image_url": place.get("image_url", ""),
                }
            )
            seen_names.add(canonical)

    return merged_places


SYSTEM_PROMPT_DISCOVERY = """
You are an Indian local travel intelligence expert with 20+ years of lived experience.
You are given a list of verified place names in a city; do NOT repeat them.
Suggest additional culturally meaningful places within a 25km radius.

Prioritize:
- Old city cores, bazaars, peths/pols/chowks
- Historic temples (>100 years old)
- Forts, hills, viewpoints
- Ghats, stepwells, riverfront sites
- Museums and freedom movement sites

Avoid malls and generic modern attractions.
Do not suggest locations outside the 25km radius unless culturally critical.

Return STRICT JSON:
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
    verified_place_names = [p.get("name", "") for p in seed_places if p.get("name")]

    llm_input = {
        "city": city,
        "verified_place_names": verified_place_names,
        "user_interests": request_data.get("interests", []),
    }

    start = time.time()
    additional_places: List[Dict[str, Any]] = []
    try:
        response = await generate_content(SYSTEM_PROMPT_DISCOVERY, json.dumps(llm_input))
        additional_places = _clean_json(response).get("additional_places", [])
    except Exception as exc:
        logger.warning(f"Discovery augmentation failed for {city}: {exc}")

    merged_places = _normalize_discovered_places(seed_places, additional_places)
    logger.info(f"Discovery latency: {(time.time() - start) * 1000:.2f}ms")
    return {"places": merged_places}


async def cluster_priority_agent(
    clusters: List[List[Dict[str, Any]]], user_interests: List[str], num_days: int
) -> Dict[str, Any]:
    system_prompt = """
You are a senior Indian city guide. Organize place clusters into day-level priorities.

Rules:
1. Do not mix high-effort outskirts places with dense old-city walking in one day.
2. Temples and forts in morning, museums/heritage afternoon, markets evening.
3. Minimize cross-city traffic and backtracking.
4. Respect the exact number of days requested.

Return STRICT JSON:
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
        json.dumps({"clusters": clusters, "user_interests": user_interests, "num_days": num_days}),
    )
    return _clean_json(response)


async def optimization_agent(
    discovery_output: Dict[str, Any], budget_feedback: Dict[str, Any]
) -> Dict[str, Any]:
    system_prompt = """
You are an Indian travel budget optimizer.
Return STRICT JSON:
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
        json.dumps({"places": discovery_output.get("places", []), "budget_feedback": budget_feedback}),
    )
    return _clean_json(response)
