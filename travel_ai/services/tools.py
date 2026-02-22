import math
import re
from typing import Dict, Any, List, Tuple
from copy import deepcopy

# ==========================================================
# Constants and Configuration
# ==========================================================

# Keywords for classifying the physical effort required to visit a place.
# This structure makes it easier to add or modify keywords for different cities.
EFFORT_CLASSIFICATION_KEYWORDS = {
    "high_effort_outskirts": ["fort", "sinhagad", "hill", "parvati", "trek"],
    "urban_walkable": ["temple", "ganapati", "devi", "chatushrungi", "dagadusheth", "market", "peth", "baug"],
    "semi_urban": ["museum", "kelkar", "zoo", "garden"],
    "modern_outskirts": ["marketcity", "phoenix"],
}

# Constants for transport cost estimation to improve readability and maintenance.
DEFAULT_ROUND_TRIP_COST = 3000  # Fallback for inter-city travel
MUMBAI_PUNE_TRAIN_BUS_ROUND_TRIP = 800  # Approx. 2026 cost for round trip
PUNE_LOCAL_PER_DAY_COST = 600  # Approx. daily cost for local travel in Pune


# ==========================================================
# Helper Functions
# ==========================================================

def _parse_cost(cost_str: str) -> float:
    """Parses a cost string (e.g., "₹1,500", "500-1000") into a float."""
    cleaned = str(cost_str).replace(",", "").replace("₹", "").strip()
    match = re.findall(r"\d+\.\d+|\d+", cleaned)
    if not match:
        return 0.0
    if "-" in cleaned and len(match) >= 2:
        return (float(match[0]) + float(match[1])) / 2
    return float(match[0])


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the distance between two points on Earth using the Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ==========================================================
# Core Tooling Functions
# ==========================================================

def estimate_transport_costs(home: str, dest: str, num_days: int) -> Dict[str, Any]:
    """
    Estimates transportation costs for a trip, including inter-city and local travel.
    """
    if home.lower() == "mumbai" and dest.lower() == "pune":
        round_trip = MUMBAI_PUNE_TRAIN_BUS_ROUND_TRIP
    else:
        round_trip = DEFAULT_ROUND_TRIP_COST

    local_total = PUNE_LOCAL_PER_DAY_COST * num_days

    return {
        "intercity_round_trip": round_trip,
        "local_daily_avg": PUNE_LOCAL_PER_DAY_COST,
        "local_total_estimate": local_total,
        "grand_total_transport": round_trip + local_total,
        "notes": "Assumes mid-range travel options (AC train/bus, app-based cabs/autos). Costs can vary.",
    }


def calculate_budget(discovery_output: Dict[str, Any], user_budget: float) -> Dict[str, Any]:
    """Calculates the total estimated cost of a trip and checks if it's within budget."""
    total_cost = sum(
        _parse_cost(place.get("estimated_cost", "0"))
        for place in discovery_output.get("places", [])
    )
    return {
        "total_estimated_cost": round(total_cost, 2),
        "within_budget": total_cost <= user_budget,
    }


def classify_place_type(place: Dict[str, Any]) -> str:
    """Classifies a place based on its name and category using predefined keywords."""
    name = place.get("name", "").lower()
    cat = place.get("category", "").lower()

    for effort_type, keywords in EFFORT_CLASSIFICATION_KEYWORDS.items():
        if any(keyword in name or keyword in cat for keyword in keywords):
            return effort_type

    return "urban_walkable"  # Default classification


def cluster_places_by_proximity(
    places: List[Dict[str, Any]], max_distance_km: float = 3.0
) -> List[List[Dict[str, Any]]]:
    """
    Clusters a list of places based on their geographic proximity.

    This function uses a simple depth-first search approach to group places that are
    within `max_distance_km` of each other. It does not modify the original list.
    """
    # Work on a copy to avoid side effects
    places_copy = deepcopy(places)

    # Filter out places that do not have valid geographic coordinates
    valid_places = [
        p for p in places_copy
        if isinstance(p.get("lat"), (int, float)) and isinstance(p.get("lng"), (int, float))
    ]

    clusters = []
    visited_indices = set()

    for i, place_i in enumerate(valid_places):
        if i in visited_indices:
            continue

        current_cluster = []
        stack = [i]

        while stack:
            current_idx = stack.pop()
            if current_idx in visited_indices:
                continue

            visited_indices.add(current_idx)
            place_to_add = valid_places[current_idx]

            # Classify effort type for the place
            place_to_add["effort_type"] = classify_place_type(place_to_add)
            current_cluster.append(place_to_add)

            # Find neighbors and add them to the stack
            for j, place_j in enumerate(valid_places):
                if j not in visited_indices:
                    dist = _haversine(
                        place_to_add["lat"], place_to_add["lng"],
                        place_j["lat"], place_j["lng"]
                    )
                    if dist <= max_distance_km:
                        stack.append(j)

        if current_cluster:
            clusters.append(current_cluster)

    # Sort clusters by size (largest first) as a heuristic for importance
    clusters.sort(key=len, reverse=True)

    return clusters