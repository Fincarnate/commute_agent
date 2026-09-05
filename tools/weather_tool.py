"""Open-Meteo weather tool that degrades gracefully."""
from __future__ import annotations
import requests
from pydantic import BaseModel
from config import REQUEST_TIMEOUT_SECONDS

WEATHER_CODES={0:("Clear","CLEAR"),1:("Mostly clear","CLEAR"),2:("Partly cloudy","CLOUDY"),3:("Overcast","CLOUDY"),45:("Fog","CLOUDY"),48:("Fog","CLOUDY"),51:("Light drizzle","RAIN"),53:("Drizzle","RAIN"),55:("Dense drizzle","RAIN"),61:("Rain","RAIN"),63:("Rain","RAIN"),65:("Heavy rain","HEAVY_RAIN"),80:("Rain showers","RAIN"),81:("Rain showers","RAIN"),82:("Heavy rain showers","HEAVY_RAIN"),95:("Thunderstorm","STORM"),96:("Thunderstorm with hail","STORM"),99:("Thunderstorm with hail","STORM")}

class WeatherInfo(BaseModel):
    temperature: float|None=None
    apparent_temperature: float|None=None
    precipitation_probability: int|None=None
    precipitation: float|None=None
    condition: str="Weather data unavailable"
    category: str="UNKNOWN"
    severity: str="UNKNOWN"
    wind_speed: float|None=None
    affects_commute: bool=False
    available: bool=False

def get_weather(latitude: float, longitude: float) -> WeatherInfo:
    """Get current Open-Meteo values near the source location."""
    try:
        response=requests.get("https://api.open-meteo.com/v1/forecast",params={"latitude":latitude,"longitude":longitude,"current":"temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m","hourly":"precipitation_probability","forecast_days":1},timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status(); payload=response.json(); current=payload["current"]
        condition,category=WEATHER_CODES.get(current.get("weather_code"),("Unknown","UNKNOWN"))
        chance=(payload.get("hourly",{}).get("precipitation_probability") or [None])[0]
        severity="HIGH" if category in {"HEAVY_RAIN","STORM"} else "MODERATE" if category=="RAIN" or (chance or 0)>=50 else "LOW"
        return WeatherInfo(temperature=current.get("temperature_2m"),apparent_temperature=current.get("apparent_temperature"),precipitation_probability=chance,precipitation=current.get("precipitation"),condition=condition,category=category,severity=severity,wind_speed=current.get("wind_speed_10m"),affects_commute=severity in {"MODERATE","HIGH"},available=True)
    except (requests.RequestException,KeyError,TypeError,ValueError):
        return WeatherInfo()
