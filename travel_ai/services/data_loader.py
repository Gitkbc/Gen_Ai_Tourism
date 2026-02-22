import json
from pathlib import Path
from typing import Dict, Any


BASE_PATH = Path(__file__).resolve().parent.parent
CITIES_PATH = BASE_PATH / "data" / "cities"


def _normalize_city_name(city_name: str) -> str:
    return " ".join(city_name.strip().lower().split())


def load_city_dataset(city_name: str) -> Dict[str, Any]:
    """
    Loads city dataset from travel_ai/data/cities/{city}.json
    Returns empty structure if file not found.
    """
    normalized_city = _normalize_city_name(city_name)
    direct_match = CITIES_PATH / f"{normalized_city}.json"

    if direct_match.exists():
        with open(direct_match, "r", encoding="utf-8") as f:
            return json.load(f)

    for candidate in CITIES_PATH.glob("*.json"):
        if _normalize_city_name(candidate.stem) == normalized_city:
            with open(candidate, "r", encoding="utf-8") as f:
                return json.load(f)

    return {
        "city": city_name,
        "places": []
    }
