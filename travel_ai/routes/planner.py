# travel_ai/routes/planner.py

import time
from fastapi import APIRouter, HTTPException

from travel_ai.services.agents import (
    discovery_agent,
    cluster_priority_agent,
    final_itinerary_agent,
)
from travel_ai.services.tools import (
    cluster_places_by_proximity,
    estimate_transport_costs,
)
from travel_ai.prompts.system_prompts import SYSTEM_PROMPT_FOOD_OPTIONS
from travel_ai.services.llm_service import generate_content
from travel_ai.services.agents import _clean_json
from travel_ai.models.schemas import TravelRequest

router = APIRouter(prefix="/planner", tags=["Planner"])


# ==========================================================
# DISCOVERY ONLY
# ==========================================================
@router.post("/discover")
async def discover_places(request: TravelRequest):
    start = time.time()

    try:
        discovery = await discovery_agent(request.dict())
        latency = (time.time() - start) * 1000

        return {
            "discovered_places": discovery.get("places", []),
            "metadata": {
                "latency_ms": round(latency, 2)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# FULL ITINERARY
# ==========================================================
@router.post("/full-itinerary")
async def full_itinerary(request: TravelRequest):
    start_total = time.time()

    try:
        # 1️⃣ Discovery
        discovery = await discovery_agent(request.dict())
        places = discovery.get("places", [])

        if not places:
            return {"error": "No places discovered"}

        # 2️⃣ Cluster
        clusters = cluster_places_by_proximity(places)

        structured_clusters = []
        for idx, cluster in enumerate(clusters):
            structured_clusters.append({
                "cluster_id": idx,
                "cluster_size": len(cluster),
                "places": [
                    {
                        "name": p["name"],
                        "category": p.get("category"),
                        "effort_type": p.get("effort_type"),
                    }
                    for p in cluster
                ]
            })

        # 3️⃣ Priority Assignment
        priority_plan = await cluster_priority_agent(
            clusters=structured_clusters,
            user_interests=request.interests,
            num_days=request.num_days
        )

        # 4️⃣ Transport Estimate
        transport_est = estimate_transport_costs(
            home=request.home_city,
            dest=request.destination_city,
            num_days=request.num_days
        )

        # 5️⃣ Food Intelligence (can cache later)
        food_raw = await generate_content(
            SYSTEM_PROMPT_FOOD_OPTIONS,
            request.destination_city
        )
        food_data = _clean_json(food_raw)

        # 6️⃣ Final Itinerary
        final_result = await final_itinerary_agent(
            priority_output=priority_plan,
            discovery_places=places,
            original_request=request.dict(),
            transport_estimate=transport_est,
            food_options=food_data.get("food_outlets", food_data)
        )

        total_latency = (time.time() - start_total) * 1000

        return {
            "itinerary": final_result.get("itinerary", {}),
            "metadata": {
                "total_latency_ms": round(total_latency, 2),
                "num_places_discovered": len(places),
                "num_clusters": len(clusters),
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))