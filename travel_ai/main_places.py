from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import json
import re

from travel_ai.services.llm_service import generate_content

app = FastAPI(title="Universal Travel Places Generator")


class CityRequest(BaseModel):
    city: str
    interests: list[str] | None = None


def clean_json(raw: str) -> Dict[str, Any]:
    raw = raw.strip()

    raw = re.sub(r"^```json", "", raw)
    raw = re.sub(r"^```", "", raw)
    raw = re.sub(r"```$", "", raw)
    raw = raw.strip()

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in response")

    return json.loads(match.group(0))

SYSTEM_PROMPT_PLACES = user_prompt = """
City: Pune

Authoritative Verified Seed Places (These are real places with coordinates and must be preserved in final output):

[
  {
    "name": "Phoenix Marketcity Pune",
    "lat": 18.562254,
    "lng": 73.9166943,
    "category": "Shopping & Markets",
    "rating": 4.5
  },
  {
    "name": "Chatushrungi Devi Temple",
    "lat": 18.5393061,
    "lng": 73.8290409,
    "category": "Religious & Spiritual Pilgrimages",
    "rating": 4.6
  },
  {
    "name": "Pune-Okayama Friendship Garden",
    "lat": 18.4913813,
    "lng": 73.8367603,
    "category": "Sightseeing & Exploration",
    "rating": 4.5
  },
  {
    "name": "Raja Dinkar Kelkar Museum",
    "lat": 18.5106855,
    "lng": 73.8544307,
    "category": "Arts, Science & Literature Attractions",
    "rating": 4.4
  },
  {
    "name": "Sinhagad Fort",
    "lat": 18.366277,
    "lng": 73.7558777,
    "category": "Cultural & Heritage Sites",
    "rating": 4.6
  },
  {
    "name": "Rajiv Gandhi Zoo",
    "lat": 18.4524807,
    "lng": 73.8607977,
    "category": "Natural Landscapes & Wildlife",
    "rating": 4.1
  },
  {
    "name": "Dagadusheth Halwai Ganapati Temple",
    "lat": 18.5164297,
    "lng": 73.8561329,
    "category": "Religious & Spiritual Pilgrimages",
    "rating": 4.8
  },
  {
    "name": "Shaniwar Wada",
    "lat": 18.5194647,
    "lng": 73.8553175,
    "category": "Cultural & Heritage Sites",
    "rating": 4.4
  }
]

Instructions:

1) All verified seed places MUST be included in the final output.
2) Do NOT remove or downgrade seed places.
3) Use their coordinates to logically cluster nearby attractions.
4) Expand intelligently by adding culturally important nearby landmarks within Pune city limits.
5) Enrich clusters around each seed anchor.
6) Avoid duplicates.
7) Avoid places outside realistic Pune urban radius.
8) Ensure minimum 35 total places in output.
9) At least 30% of places must not be globally famous.

Generate the structured JSON blueprint as per system rules.
"""

@app.post("/generate-places")
def generate_places(request: CityRequest):
    try:
        user_prompt = json.dumps({
            "city": request.city,
            "interests": request.interests or []
        })

        response = generate_content(
            SYSTEM_PROMPT_PLACES,
            user_prompt
        )

        parsed = clean_json(response)

        return parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))