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