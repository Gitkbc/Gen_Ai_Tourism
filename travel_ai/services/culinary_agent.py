import json
from typing import Any, Dict, List

from travel_ai.prompts.system_prompts import SYSTEM_PROMPT_CULINARY_INTELLIGENCE
from travel_ai.services.agents import _clean_json
from travel_ai.services.llm_service import generate_content
from travel_ai.utils.logger import get_logger

logger = get_logger("culinary_agent")


def _normalize_food_outlet(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": str(item.get("name", "")).strip(),
        "area_or_neighborhood": str(item.get("area_or_neighborhood", "")).strip(),
        "signature_dishes": item.get("signature_dishes", []) if isinstance(item.get("signature_dishes"), list) else [],
        "meal_slots": item.get("meal_slots", []) if isinstance(item.get("meal_slots"), list) else [],
        "legacy_score": float(item.get("legacy_score", 0.0) or 0.0),
        "cuisine": str(item.get("cuisine", "")).strip(),
    }


def _sanitize_culinary_payload(payload: Dict[str, Any], city: str) -> Dict[str, Any]:
    food_outlets_raw = payload.get("food_outlets", [])
    food_outlets = []
    seen = set()
    for outlet in food_outlets_raw:
        normalized = _normalize_food_outlet(outlet)
        canonical = normalized["name"].strip().lower()
        if not canonical or canonical in seen:
            continue
        food_outlets.append(normalized)
        seen.add(canonical)

    return {
        "city": city,
        "breakfast_signatures": payload.get("breakfast_signatures", []),
        "lunch_style": payload.get("lunch_style", []),
        "snack_signatures": payload.get("snack_signatures", []),
        "dinner_style": payload.get("dinner_style", []),
        "legacy_establishments": payload.get("legacy_establishments", []),
        "heritage_food_clusters": payload.get("heritage_food_clusters", []),
        "food_outlets": food_outlets,
    }


async def culinary_agent(city: str, user_interests: List[str]) -> Dict[str, Any]:
    user_prompt = json.dumps({"city": city, "user_interests": user_interests})
    try:
        response = await generate_content(SYSTEM_PROMPT_CULINARY_INTELLIGENCE, user_prompt)
        parsed = _clean_json(response)
        return _sanitize_culinary_payload(parsed, city)
    except Exception as exc:
        logger.warning(f"Culinary intelligence generation failed for {city}: {exc}")
        return {
            "city": city,
            "breakfast_signatures": [],
            "lunch_style": [],
            "snack_signatures": [],
            "dinner_style": [],
            "legacy_establishments": [],
            "heritage_food_clusters": [],
            "food_outlets": [],
        }
