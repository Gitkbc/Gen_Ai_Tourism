import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


CACHE_DIR = Path(__file__).resolve().parent.parent / "cache" / "full_itinerary.output"


def _normalize_request(request_dict: Dict[str, Any]) -> Dict[str, Any]:
    interests = request_dict.get("interests", [])
    normalized_interests = sorted([str(i).strip().lower() for i in interests if str(i).strip()])
    return {
        "home_city": str(request_dict.get("home_city", "")).strip().lower(),
        "destination_city": str(request_dict.get("destination_city", "")).strip().lower(),
        "num_days": int(request_dict.get("num_days", 0)),
        "budget": float(request_dict.get("budget", 0)),
        "interests": normalized_interests,
    }


def _cache_key(request_dict: Dict[str, Any]) -> str:
    normalized = _normalize_request(request_dict)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_cached_full_itinerary(request_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _cache_key(request_dict)
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        cached = json.load(f)
    return cached.get("response")


def save_cached_full_itinerary(request_dict: Dict[str, Any], response: Dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _cache_key(request_dict)
    path = CACHE_DIR / f"{key}.json"
    payload = {
        "cache_key": key,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "request": _normalize_request(request_dict),
        "response": response,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
