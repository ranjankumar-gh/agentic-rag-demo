from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    region: Optional[str] = "Maharashtra"

class PlanItem(BaseModel):
    name: str
    price: float
    data_per_day: str
    validity_days: int
    source: str
    last_updated: Optional[str]

class QueryResponse(BaseModel):
    query: str
    plans: List[PlanItem]
    generated_at: str
    confidence: float
    notes: Optional[str]
