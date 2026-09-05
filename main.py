"""Terminal entry point for the ReAct-Based Intelligent Commute Agent."""
from __future__ import annotations
from agent import CommuteAgent
from services.geocoding import GeocodingError

MODE_CHOICES={"1":"car","2":"bike","3":"bus","4":"train","5":"walking"}

def _ask_for_mode() -> str:
    while True:
        print("\nSelect travel mode:\n1. Car\n2. Bike\n3. Bus\n4. Train\n5. Walking")
        choice=input("Enter choice: ").strip()
        if choice in MODE_CHOICES: return MODE_CHOICES[choice]
        print("Please enter a number from 1 to 5.")

def _print_result(result) -> None:
    print("\n----------------------------------------\n           AGENT ACTIVITY\n----------------------------------------")
    for item in result.activity: print(item)
    print("\n----------------------------------------\n           COMMUTE RESULT\n----------------------------------------")
    print(f"Source: {result.source}\nDestination: {result.destination}\nTravel Mode: {result.travel_mode.title()}")
    print(f"\nDistance: {result.route.distance_km} km\nBase Travel Time: {result.route.base_time_minutes} minutes\nRoute Data Source: {result.route.data_source}")
    if result.route.note: print(f"Note: {result.route.note}")
    if result.traffic: print(f"\nTraffic: {result.traffic.traffic_level}\nTraffic Delay: +{result.traffic.delay_minutes} minutes\nTraffic Data Source: {result.traffic.data_source}")
    else: print("\nTraffic: Not used for this travel mode")
    if result.weather.available: print(f"\nWeather: {result.weather.condition}\nTemperature: {result.weather.temperature}°C\nWeather Impact: +{result.estimate.weather_delay_minutes} minutes")
    else: print("\nWeather: Weather data unavailable.\nWeather Impact: +0 minutes")
    if result.road: print(f"\nRoad Condition: {result.road.condition}\nRoad Delay: +{result.road.additional_delay_minutes} minutes\nRoad Data Source: {result.road.data_source}")
    else: print("\nRoad Condition: Not used for this travel mode")
    print(f"\nEstimated Travel Time: {result.estimate.lower_bound}-{result.estimate.upper_bound} minutes\nCalculation: {result.estimate.explanation}\nRecommendation: {result.recommendation}\n\nAgent Mode: {result.agent_mode}")

def main() -> None:
    print("========================================\n       INTELLIGENT COMMUTE AGENT\n========================================")
    source=input("Enter source: ").strip(); destination=input("Enter destination: ").strip(); mode=_ask_for_mode()
    try: _print_result(CommuteAgent().run(source,destination,mode))
    except (ValueError, GeocodingError) as exc: print(f"\nUnable to plan this commute: {exc}")
    except KeyboardInterrupt: print("\nCommute planning cancelled.")
    except Exception: print("\nUnable to plan this commute right now. Please try again.")

if __name__ == "__main__": main()
