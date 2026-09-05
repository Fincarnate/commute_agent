"""Deterministic simulated traffic tool. It never claims live traffic data."""
from datetime import datetime
from pydantic import BaseModel, Field

class TrafficInfo(BaseModel):
    traffic_level: str
    delay_minutes: int = Field(ge=0)
    data_source: str = "SIMULATED / DEMO"

def get_traffic(distance_km: float, travel_mode: str, hour: int | None = None) -> TrafficInfo:
    hour=datetime.now().hour if hour is None else hour
    rush=2 if hour in {7,8,9,17,18,19,20} else 1 if hour in {6,10,16,21} else 0
    score=rush+int(distance_km>=12)+int(distance_km>=35)
    if travel_mode in {"walking","train"}: score=max(0,score-1)
    level=("LOW","MODERATE","HEAVY","SEVERE")[min(score,3)]
    delay={"LOW":round(distance_km*.03),"MODERATE":max(5,round(distance_km*.12)),"HEAVY":max(10,round(distance_km*.24)),"SEVERE":max(20,round(distance_km*.38))}[level]
    return TrafficInfo(traffic_level=level,delay_minutes=0 if travel_mode in {"walking","train"} else delay)
