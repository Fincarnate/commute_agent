"""OSRM route lookup with transparent transit and API-failure fallbacks."""
from __future__ import annotations
import math
import requests
from pydantic import BaseModel, Field
from config import REQUEST_TIMEOUT_SECONDS, USER_AGENT
from services.geocoding import Location, geocode_location

class RouteInfo(BaseModel):
    source: str
    destination: str
    source_coordinates: Location
    destination_coordinates: Location
    distance_km: float = Field(ge=0)
    base_time_minutes: int = Field(ge=1)
    status: str = "success"
    data_source: str
    note: str | None = None

def _straight_line_km(first: Location, second: Location) -> float:
    radius = 6371.0
    lat_delta, lon_delta = math.radians(second.latitude-first.latitude), math.radians(second.longitude-first.longitude)
    formula = math.sin(lat_delta/2)**2 + math.cos(math.radians(first.latitude))*math.cos(math.radians(second.latitude))*math.sin(lon_delta/2)**2
    return radius * 2 * math.atan2(math.sqrt(formula), math.sqrt(1-formula))

def get_route(source: str, destination: str, travel_mode: str) -> RouteInfo:
    """Get OSRM data for car/bike/walking; label transit estimates honestly."""
    first, second = geocode_location(source), geocode_location(destination)
    if travel_mode in {"bus", "train"}:
        distance = round(_straight_line_km(first, second)*1.25, 1)
        speed, transfer = (24,7) if travel_mode == "bus" else (42,10)
        return RouteInfo(source=source, destination=destination, source_coordinates=first, destination_coordinates=second, distance_km=distance, base_time_minutes=max(8, round(distance/speed*60)+transfer), data_source="DEMO transit estimate", note="OSRM does not provide public-transit schedules; this is a demo estimate.")
    profile = {"car":"driving", "bike":"cycling", "walking":"foot"}[travel_mode]
    endpoint = f"https://router.project-osrm.org/route/v1/{profile}/{first.longitude},{first.latitude};{second.longitude},{second.latitude}"
    try:
        response = requests.get(endpoint, params={"overview":"false"}, headers={"User-Agent":USER_AGENT}, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status(); route = response.json().get("routes", [])[0]
        return RouteInfo(source=source, destination=destination, source_coordinates=first, destination_coordinates=second, distance_km=round(float(route["distance"])/1000,1), base_time_minutes=max(1,round(float(route["duration"])/60)), data_source="OSRM")
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        distance = round(_straight_line_km(first, second)*1.25, 1)
        speed = {"car":32,"bike":15,"walking":4.8}[travel_mode]
        return RouteInfo(source=source, destination=destination, source_coordinates=first, destination_coordinates=second, distance_km=distance, base_time_minutes=max(1,round(distance/speed*60)), data_source="DEMO route fallback", note="Public OSRM routing was unavailable; this is an approximate fallback.")
