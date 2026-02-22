import asyncio
import time
from fastapi import APIRouter, HTTPException

from travel_ai.services.agents import (
    discovery_agent,
    cluster_priority_agent,
    rank_places_for_visit,
)
from travel_ai.services.tools import (
    cluster_places_by_proximity,
    estimate_transport_costs,
)
from travel_ai.services.culinary_agent import culinary_agent
from travel_ai.services.final_route_architect import final_route_architect
from travel_ai.models.schemas import TravelRequest, PlaceDetailRequest, PlaceDetailResponse
from travel_ai.utils.logger import get_logger
from travel_ai.services.place_detail_service import get_place_detail_with_tts
from travel_ai.services.itinerary_cache_service import (
    get_cached_full_itinerary,
    save_cached_full_itinerary,
)

router = APIRouter(prefix="/planner", tags=["Planner"])
logger = get_logger("planner_route")


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


@router.post("/place-detail-tts", response_model=PlaceDetailResponse)
async def place_detail_tts(request: PlaceDetailRequest):
    try:
        result = await get_place_detail_with_tts(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# FULL ITINERARY
# ==========================================================
@router.post("/full-itinerary")
async def full_itinerary(request: TravelRequest):
    start_total = time.time()

    try:
        request_dict = request.dict()

        cached_response = get_cached_full_itinerary(request_dict)
        if cached_response:
            await asyncio.sleep(20)
            cached_meta = cached_response.get("metadata", {})
            cached_meta["cache_hit"] = True
            cached_meta["returned_within_30_seconds"] = True
            cached_meta["total_latency_ms"] = round((time.time() - start_total) * 1000, 2)
            cached_response["metadata"] = cached_meta
            return cached_response

        # 1) Run discovery + culinary intelligence in parallel
        discovery_task = asyncio.create_task(discovery_agent(request_dict))
        culinary_task = asyncio.create_task(culinary_agent(request.destination_city, request.interests))
        discovery_result, culinary_result = await asyncio.gather(
            discovery_task, culinary_task, return_exceptions=True
        )

        if isinstance(discovery_result, Exception):
            raise discovery_result
        discovery = discovery_result
        if isinstance(culinary_result, Exception):
            logger.warning(f"Culinary task failed: {culinary_result}")
            culinary_result = {
                "city": request.destination_city,
                "breakfast_signatures": [],
                "lunch_style": [],
                "snack_signatures": [],
                "dinner_style": [],
                "legacy_establishments": [],
                "heritage_food_clusters": [],
                "food_outlets": [],
            }

        places = discovery.get("places", [])

        if not places:
            return {"error": "No places discovered"}

        ranking = rank_places_for_visit(places, request.interests, top_n=4)
        mandatory_top_places = [p["name"] for p in ranking.get("mandatory_top_places", [])]

        # 2) Cluster
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

        # 3) Priority assignment
        priority_plan = await cluster_priority_agent(
            clusters=structured_clusters,
            user_interests=request.interests,
            num_days=request.num_days
        )

        # 4) Transport estimate
        transport_est = estimate_transport_costs(
            home=request.home_city,
            dest=request.destination_city,
            num_days=request.num_days
        )

        # 5) Final route architect
        final_result = await final_route_architect(
            priority_output=priority_plan,
            discovery_places=places,
            culinary_intelligence=culinary_result,
            original_request=request_dict,
            transport_estimate=transport_est,
            mandatory_top_places=mandatory_top_places,
        )

        total_latency = (time.time() - start_total) * 1000

        response_payload = {
            "itinerary": final_result.get("itinerary", {}),
            "metadata": {
                "total_latency_ms": round(total_latency, 2),
                "num_places_discovered": len(places),
                "num_clusters": len(clusters),
                "mandatory_top_places": mandatory_top_places,
                "cache_hit": False,
                "returned_within_30_seconds": total_latency <= 30000,
            }
        }
        save_cached_full_itinerary(request_dict, response_payload)
        return response_payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
