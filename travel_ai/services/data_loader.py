import json
from pathlib import Path
from typing import Dict, Any


BASE_PATH = Path(__file__).resolve().parent.parent
CITIES_PATH = BASE_PATH / "data" / "cities"


def load_city_dataset(city_name: str) -> Dict[str, Any]:
    """
    Loads city dataset from travel_ai/data/cities/{city}.json
    Returns empty structure if file not found.
    """

    file_path = CITIES_PATH / f"{city_name.lower()}.json"

    if not file_path.exists():
        return {
            "city": city_name,
            "places": []
        }

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)