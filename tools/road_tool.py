"""Deterministic simulated road-condition tool, replaceable by a real API."""
import hashlib
from pydantic import BaseModel, Field

class RoadInfo(BaseModel):
    condition: str
    construction: bool
    pothole_risk: str
    additional_delay_minutes: int = Field(ge=0)
    data_source: str = "SIMULATED / DEMO"

def get_road_conditions(source: str,destination: str,distance_km: float) -> RoadInfo:
    marker=int(hashlib.sha256(f"{source.lower()}|{destination.lower()}".encode()).hexdigest()[:8],16)%100
    if marker<50: return RoadInfo(condition="GOOD",construction=False,pothole_risk="LOW",additional_delay_minutes=0)
    if marker<83: return RoadInfo(condition="MODERATE",construction=marker%2==0,pothole_risk="MEDIUM",additional_delay_minutes=max(2,round(distance_km*.08)))
    return RoadInfo(condition="POOR",construction=True,pothole_risk="HIGH",additional_delay_minutes=max(5,round(distance_km*.18)))
