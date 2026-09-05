"""Transparent commute-time range calculation."""
from pydantic import BaseModel
from tools.weather_tool import WeatherInfo

class TimeEstimate(BaseModel):
    lower_bound: int
    central_estimate: int
    upper_bound: int
    weather_delay_minutes: int
    explanation: str

def get_weather_delay(weather: WeatherInfo, travel_mode: str) -> int:
    if not weather.available: return 0
    delays={"LOW":{"car":1,"bike":2,"bus":1,"train":0,"walking":2},"MODERATE":{"car":5,"bike":10,"bus":4,"train":2,"walking":12},"HIGH":{"car":10,"bike":18,"bus":8,"train":4,"walking":22}}
    return delays.get(weather.severity,delays["LOW"])[travel_mode]

def estimate_time(base_time:int,traffic_delay:int,weather:WeatherInfo,road_delay:int,travel_mode:str)->TimeEstimate:
    weather_delay=get_weather_delay(weather,travel_mode); total=base_time+traffic_delay+weather_delay+road_delay; spread=max(3,round(total*.10))
    return TimeEstimate(lower_bound=max(1,total-spread),central_estimate=total,upper_bound=total+spread,weather_delay_minutes=weather_delay,explanation=f"Base {base_time} min + traffic {traffic_delay} min + weather {weather_delay} min + road {road_delay} min.")
