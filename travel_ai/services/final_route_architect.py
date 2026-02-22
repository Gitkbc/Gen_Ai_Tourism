import json
import math
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

from travel_ai.prompts.system_prompts import SYSTEM_PROMPT_FINAL_ROUTE_ARCHITECT
from travel_ai.services.agents import _clean_json
from travel_ai.services.llm_service import generate_content

MEAL_SLOTS: List[Tuple[str, str]] = [
    ("Breakfast", "08:00-09:00"),
    ("Lunch", "13:00-14:00"),
    ("Snacks", "16:30-17:30"),
    ("Dinner", "20:00-21:00"),
]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _canonical_name(name: str) -> str:
    return " ".join(str(name or "").strip().lower().split())


def _parse_start_hour(time_range: str) -> float:
    try:
        start = time_range.split("-")[0].strip()
        parsed = datetime.strptime(start, "%H:%M")
        return parsed.hour + parsed.minute / 60
    except Exception:
        return 9.0


def _format_slot(start_minutes: int, duration_minutes: int) -> str:
    end_minutes = start_minutes + duration_minutes
    sh, sm = divmod(start_minutes, 60)
    eh, em = divmod(end_minutes, 60)
    return f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}"


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return earth_radius_km * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def _is_high_effort(place: Dict[str, Any]) -> bool:
    text = f"{place.get('name', '')} {place.get('category', '')} {place.get('effort_type', '')}".lower()
    keywords = ["fort", "trek", "hill", "outskirts", "high_effort", "peak", "sanctuary"]
    return any(keyword in text for keyword in keywords)


def _is_extended_visit(place: Dict[str, Any]) -> bool:
    text = f"{place.get('name', '')} {place.get('category', '')}".lower()
    keywords = ["hill", "viewpoint", "cityscape", "fort", "trek", "sunset point", "peak"]
    return any(keyword in text for keyword in keywords)


def _build_place_index(discovery_places: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for place in discovery_places:
        name = str(place.get("name", "")).strip()
        lat = place.get("lat")
        lng = place.get("lng")
        canonical = _canonical_name(name)
        if not canonical or not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            continue
        out[canonical] = {
            "name": name,
            "lat": _safe_float(lat),
            "lng": _safe_float(lng),
            "ticket_price": _safe_float(place.get("ticket_price"), 0.0),
            "category": place.get("category", ""),
            "effort_type": place.get("effort_type", ""),
            "rating": _safe_float(place.get("rating"), 0.0),
            "image_url": str(place.get("image_url", "")).strip(),
        }
    return out


def _sorted_allowed_places(place_index: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    places = list(place_index.values())
    places.sort(key=lambda p: (p["lat"], p["lng"]))
    return [
        {
            "name": p["name"],
            "lat": p["lat"],
            "lng": p["lng"],
            "category": p["category"],
            "ticket_price": p["ticket_price"],
            "effort_type": p["effort_type"],
        }
        for p in places
    ]


def _slim_priority_payload(priority_output: Dict[str, Any]) -> Dict[str, Any]:
    slim_days = []
    for day in priority_output.get("days", []):
        slim_days.append(
            {
                "day": day.get("day"),
                "theme": day.get("theme", ""),
                "places": [p.get("name", "") for p in day.get("places", []) if p.get("name")],
            }
        )
    return {"days": slim_days}


def _build_food_index(culinary_intel: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    for item in culinary_intel.get("food_outlets", []):
        name = str(item.get("name", "")).strip()
        canonical = _canonical_name(name)
        if not canonical:
            continue
        idx[canonical] = {
            "name": name,
            "area_or_neighborhood": str(item.get("area_or_neighborhood", "")).strip(),
            "signature_dishes": item.get("signature_dishes", []) if isinstance(item.get("signature_dishes"), list) else [],
            "meal_slots": [str(slot).strip() for slot in item.get("meal_slots", []) if str(slot).strip()],
            "cuisine": str(item.get("cuisine", "")).strip(),
        }
    return idx


def _pick_fallback_outlet(food_index: Dict[str, Dict[str, Any]], meal_type: str) -> Dict[str, str]:
    for outlet in food_index.values():
        if meal_type in outlet.get("meal_slots", []):
            dish = outlet["signature_dishes"][0] if outlet["signature_dishes"] else outlet.get("cuisine", "Local specialty")
            return {
                "outlet": outlet["name"],
                "signature_dish": dish,
                "area": outlet.get("area_or_neighborhood", "City Center") or "City Center",
            }
    for outlet in food_index.values():
        dish = outlet["signature_dishes"][0] if outlet["signature_dishes"] else outlet.get("cuisine", "Local specialty")
        return {
            "outlet": outlet["name"],
            "signature_dish": dish,
            "area": outlet.get("area_or_neighborhood", "City Center") or "City Center",
        }
    return {"outlet": "Local iconic eatery", "signature_dish": "Regional specialty", "area": "City Center"}


def _enforce_four_meals(day_food_halts: List[Dict[str, Any]], food_index: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    normalized_by_meal: Dict[str, Dict[str, str]] = {}
    for halt in day_food_halts:
        meal_type = str(halt.get("meal_type", "")).strip().title()
        outlet_canonical = _canonical_name(halt.get("outlet", ""))
        if meal_type not in dict(MEAL_SLOTS):
            continue
        if outlet_canonical and outlet_canonical in food_index:
            outlet = food_index[outlet_canonical]
            dish = str(halt.get("signature_dish", "")).strip()
            if not dish:
                dish = outlet["signature_dishes"][0] if outlet["signature_dishes"] else (outlet.get("cuisine") or "Local specialty")
            normalized_by_meal[meal_type] = {
                "time": dict(MEAL_SLOTS)[meal_type],
                "meal_type": meal_type,
                "outlet": outlet["name"],
                "signature_dish": dish,
                "area": str(halt.get("area", "")).strip() or outlet.get("area_or_neighborhood", "City Center") or "City Center",
                "reason_selected": str(halt.get("reason_selected", "")).strip()
                or "Chosen for local legacy and route proximity.",
            }

    final_meals = []
    for meal_type, slot in MEAL_SLOTS:
        meal = normalized_by_meal.get(meal_type)
        if not meal:
            fallback = _pick_fallback_outlet(food_index, meal_type)
            meal = {
                "time": slot,
                "meal_type": meal_type,
                "outlet": fallback["outlet"],
                "signature_dish": fallback["signature_dish"],
                "area": fallback["area"],
                "reason_selected": "Auto-filled to enforce mandatory 4-meal structure.",
            }
        final_meals.append(meal)
    return final_meals


def _mean_lat_lng(place_index: Dict[str, Dict[str, Any]]) -> Tuple[float, float]:
    values = list(place_index.values())
    if not values:
        return 0.0, 0.0
    lat = sum(p["lat"] for p in values) / len(values)
    lng = sum(p["lng"] for p in values) / len(values)
    return lat, lng


def _sanitize_day_blocks(
    blocks: List[Dict[str, Any]],
    place_index: Dict[str, Dict[str, Any]],
    center_lat: float,
    center_lng: float,
) -> List[Dict[str, str]]:
    valid_blocks = []
    for block in blocks[:4]:
        canonical = _canonical_name(block.get("place", ""))
        if canonical not in place_index:
            continue
        valid_blocks.append(
            {
                "time": str(block.get("time", "")).strip() or "09:00-10:30",
                "place": place_index[canonical]["name"],
                "reason_for_time_choice": str(block.get("reason_for_time_choice", "")).strip()
                or "Aligned with traffic and site rhythm.",
            }
        )

    if not valid_blocks:
        return []

    # Prevent >8km spread in same half-day.
    grouped: Dict[str, List[Dict[str, str]]] = {"morning": [], "afternoon": []}
    for block in valid_blocks:
        key = "morning" if _parse_start_hour(block["time"]) < 13 else "afternoon"
        grouped[key].append(block)

    pruned_blocks: List[Dict[str, str]] = []
    for key in ["morning", "afternoon"]:
        current = []
        for block in grouped[key]:
            candidate = place_index[_canonical_name(block["place"])]
            if not current:
                current.append(block)
                continue
            within_limit = True
            for existing in current:
                existing_place = place_index[_canonical_name(existing["place"])]
                if _haversine(
                    candidate["lat"], candidate["lng"], existing_place["lat"], existing_place["lng"]
                ) > 8.0:
                    within_limit = False
                    break
            if within_limit:
                current.append(block)
        pruned_blocks.extend(current)

    # Isolate >15km high-effort places into separate day: keep only first such place for the day.
    isolated = []
    for block in pruned_blocks:
        place = place_index[_canonical_name(block["place"])]
        is_far_high_effort = _is_high_effort(place) and _haversine(
            place["lat"], place["lng"], center_lat, center_lng
        ) > 15.0
        if is_far_high_effort:
            return [block]
        isolated.append(block)
    return isolated


def _apply_visit_durations(
    blocks: List[Dict[str, str]],
    place_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, str]]:
    """
    Default 1-hour per place.
    Extended 90 mins for hills/cityscape/fort/trek style locations.
    Includes 20-min transit buffer between consecutive places.
    """
    timed_blocks: List[Dict[str, str]] = []
    block_count = len(blocks)

    # Spread visits through the day so itinerary doesn't end too early.
    if block_count >= 4:
        start_templates = [480, 630, 840, 1020]  # 08:00, 10:30, 14:00, 17:00
    elif block_count == 3:
        start_templates = [510, 750, 990]  # 08:30, 12:30, 16:30
    elif block_count == 2:
        start_templates = [510, 990]  # 08:30, 16:30
    elif block_count == 1:
        start_templates = [540]  # 09:00
    else:
        start_templates = []

    for idx, block in enumerate(blocks):
        place = place_index.get(_canonical_name(block["place"]), {})
        duration = 90 if _is_extended_visit(place) else 60
        start_minutes = start_templates[idx] if idx < len(start_templates) else 540
        timed_blocks.append(
            {
                "time": _format_slot(start_minutes, duration),
                "place": block["place"],
                "reason_for_time_choice": block["reason_for_time_choice"],
                "image_url": place.get("image_url", ""),
            }
        )
    return timed_blocks


def _insert_mandatory_places(
    days: List[Dict[str, Any]],
    mandatory_top_places: List[str],
    place_index: Dict[str, Dict[str, Any]],
) -> None:
    if not days:
        return

    mandatory_names = []
    for name in mandatory_top_places:
        canonical = _canonical_name(name)
        if canonical in place_index and canonical not in mandatory_names:
            mandatory_names.append(canonical)

    scheduled = {
        _canonical_name(block["place"])
        for day in days
        for block in day.get("schedule_blocks", [])
    }

    missing = [name for name in mandatory_names if name not in scheduled]
    if not missing:
        return

    day_idx = 0
    for canonical in missing:
        place_name = place_index[canonical]["name"]
        inserted = False

        for _ in range(len(days)):
            day = days[day_idx]
            blocks = day.get("schedule_blocks", [])
            if len(blocks) < 4:
                day["schedule_blocks"] = [
                    {
                        "time": "",
                        "place": place_name,
                        "reason_for_time_choice": "Mandatory top-ranked place from initial destination ranking.",
                    }
                ] + blocks
                inserted = True
                day_idx = (day_idx + 1) % len(days)
                break
            day_idx = (day_idx + 1) % len(days)

        if not inserted:
            # Force insert on earliest day if all days are full.
            day = days[0]
            day["schedule_blocks"] = (
                [
                    {
                        "time": "",
                        "place": place_name,
                        "reason_for_time_choice": "Mandatory top-ranked place from initial destination ranking.",
                    }
                ]
                + day.get("schedule_blocks", [])[:3]
            )


def _day_cost(schedule_blocks: List[Dict[str, str]], place_index: Dict[str, Dict[str, Any]]) -> float:
    unique_places = {_canonical_name(block["place"]) for block in schedule_blocks}
    ticket_total = sum(place_index[name]["ticket_price"] for name in unique_places if name in place_index)
    return round(ticket_total + 700 + 700, 2)


def _sanitize_itinerary(
    parsed: Dict[str, Any],
    place_index: Dict[str, Dict[str, Any]],
    food_index: Dict[str, Dict[str, Any]],
    destination_city: str,
    num_days: int,
    budget: float,
    mandatory_top_places: Optional[List[str]] = None,
) -> Dict[str, Any]:
    raw_itinerary = parsed.get("itinerary", {})
    raw_days = raw_itinerary.get("days", [])
    center_lat, center_lng = _mean_lat_lng(place_index)

    fallback_places = list(place_index.values())
    fallback_places.sort(key=lambda p: p.get("rating", 0.0), reverse=True)
    fallback_cursor = 0
    used_places = set()

    days = []
    for idx in range(1, num_days + 1):
        day_raw = raw_days[idx - 1] if idx - 1 < len(raw_days) else {}
        blocks = _sanitize_day_blocks(day_raw.get("schedule_blocks", []), place_index, center_lat, center_lng)

        if not blocks and fallback_cursor < len(fallback_places):
            while fallback_cursor < len(fallback_places):
                fallback = fallback_places[fallback_cursor]
                fallback_cursor += 1
                canonical = _canonical_name(fallback["name"])
                if canonical in used_places:
                    continue
                blocks = [{
                    "time": "",
                    "place": fallback["name"],
                    "reason_for_time_choice": "Fallback from verified place index."
                }]
                used_places.add(canonical)
                break

        meals = _enforce_four_meals(day_raw.get("food_halts", []), food_index)
        walking_km = _safe_float(day_raw.get("total_walking_km_estimate"), 3.0)

        if blocks and len(blocks) == 1:
            only_place = place_index.get(_canonical_name(blocks[0]["place"]), {})
            if _is_high_effort(only_place):
                walking_km = max(walking_km, 4.5)
            else:
                walking_km = min(walking_km, 4.0)
        else:
            walking_km = min(walking_km, 4.0)

        days.append(
            {
                "day": idx,
                "day_time_window": "08:00-20:00",
                "geographic_flow_explanation": str(day_raw.get("geographic_flow_explanation", "")).strip()
                or "Directional movement with low backtracking and realistic segment durations.",
                "total_walking_km_estimate": round(max(walking_km, 0.0), 2),
                "schedule_blocks": blocks,
                "food_halts": meals,
                "estimated_day_cost": _day_cost(blocks, place_index),
            }
        )

    _insert_mandatory_places(days, mandatory_top_places or [], place_index)

    for day in days:
        day["schedule_blocks"] = _apply_visit_durations(day.get("schedule_blocks", []), place_index)
        day["estimated_day_cost"] = _day_cost(day["schedule_blocks"], place_index)

    total_estimated_cost = round(sum(day["estimated_day_cost"] for day in days), 2)
    hotel = raw_itinerary.get("hotel_recommendation", {})
    hotel_area = str(hotel.get("area", "")).strip() or f"{destination_city} Central"
    hotel_reason = str(hotel.get("reason", "")).strip() or "Central area minimizes average daily commute."

    return {
        "itinerary": {
            "title": str(raw_itinerary.get("title", "")).strip() or f"{destination_city} Human-Realistic Route Plan",
            "hotel_recommendation": {"area": hotel_area, "reason": hotel_reason},
            "days": days,
            "total_estimated_cost": total_estimated_cost,
            "within_budget": total_estimated_cost <= budget,
        }
    }


async def final_route_architect(
    priority_output: Dict[str, Any],
    discovery_places: List[Dict[str, Any]],
    culinary_intelligence: Dict[str, Any],
    original_request: Dict[str, Any],
    transport_estimate: Dict[str, Any],
    mandatory_top_places: Optional[List[str]] = None,
) -> Dict[str, Any]:
    place_index = _build_place_index(discovery_places)
    food_index = _build_food_index(culinary_intelligence)
    allowed_places = _sorted_allowed_places(place_index)
    allowed_food_outlets = list(food_index.values())

    llm_input = {
        "request": {
            "destination_city": original_request.get("destination_city"),
            "num_days": original_request.get("num_days"),
            "budget": original_request.get("budget"),
            "interests": original_request.get("interests", []),
        },
        "priority_day_plan": _slim_priority_payload(priority_output),
        "mandatory_top_places": mandatory_top_places or [],
        "allowed_places": allowed_places,
        "allowed_food_outlets": allowed_food_outlets,
        "culinary_intelligence": {
            "breakfast_signatures": culinary_intelligence.get("breakfast_signatures", []),
            "lunch_style": culinary_intelligence.get("lunch_style", []),
            "snack_signatures": culinary_intelligence.get("snack_signatures", []),
            "dinner_style": culinary_intelligence.get("dinner_style", []),
            "legacy_establishments": culinary_intelligence.get("legacy_establishments", []),
            "heritage_food_clusters": culinary_intelligence.get("heritage_food_clusters", []),
        },
        "transport_estimate": {
            "local_daily_avg": transport_estimate.get("local_daily_avg"),
            "notes": transport_estimate.get("notes", ""),
        },
    }

    response = await generate_content(SYSTEM_PROMPT_FINAL_ROUTE_ARCHITECT, json.dumps(llm_input))
    parsed = _clean_json(response)
    return _sanitize_itinerary(
        parsed=parsed,
        place_index=place_index,
        food_index=food_index,
        destination_city=str(original_request.get("destination_city", "City")).strip() or "City",
        num_days=int(original_request.get("num_days", 1)),
        budget=_safe_float(original_request.get("budget"), 0.0),
        mandatory_top_places=mandatory_top_places or [],
    )
