from pydantic import BaseModel, Field
from typing import List, Dict, Any


class TravelRequest(BaseModel):
    home_city: str
    destination_city: str
    num_days: int = Field(gt=0)
    budget: float = Field(gt=0)
    interests: List[str]


class PlannerResponse(BaseModel):
    plan: Dict[str, Any]
    budget_analysis: Dict[str, Any]
    evaluation: Dict[str, Any]
    metadata: Dict[str, Any]


class PlaceDetailRequest(BaseModel):
    time: str
    place: str
    reason_for_time_choice: str
    image_url: str = ""
    destination_city: str


class NarrationOutput(BaseModel):
    text: str
    audio_file: str
    audio_url: str


class PlaceDetailResponse(BaseModel):
    place: str
    destination_city: str
    local_language: str
    local_text: str
    constraints: List[str]
    special_cautions: List[str]
    outputs: Dict[str, NarrationOutput]
    cached: bool
