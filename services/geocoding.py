"""Location lookup through OpenStreetMap Nominatim."""
from __future__ import annotations
import requests
from pydantic import BaseModel
from config import REQUEST_TIMEOUT_SECONDS, USER_AGENT

class GeocodingError(ValueError):
    """Friendly, display-safe geocoding failure."""

class Location(BaseModel):
    latitude: float
    longitude: float
    display_name: str

def geocode_location(query: str) -> Location:
    """Find a location, raising a clear error for an unavailable or unknown place."""
    try:
        response = requests.get("https://nominatim.openstreetmap.org/search", params={"q": query, "format": "jsonv2", "limit": 1}, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        matches = response.json()
    except requests.RequestException as exc:
        raise GeocodingError("Location lookup is temporarily unavailable. Please try again.") from exc
    if not isinstance(matches, list) or not matches:
        raise GeocodingError(f"Could not find '{query}'. Please try a more specific location.")
    try:
        match = matches[0]
        return Location(latitude=float(match["lat"]), longitude=float(match["lon"]), display_name=str(match["display_name"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise GeocodingError("Location service returned an unexpected result. Please try again.") from exc
