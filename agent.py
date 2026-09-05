"""Safe ReAct-style orchestration for the terminal application."""
from pydantic import BaseModel
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from tools.route_tool import RouteInfo, get_route
from tools.weather_tool import WeatherInfo, get_weather
from tools.traffic_tool import TrafficInfo, get_traffic
from tools.road_tool import RoadInfo, get_road_conditions
from tools.time_estimator import TimeEstimate, estimate_time

VALID_MODES={"car","bike","bus","train","walking"}

class CommuteResult(BaseModel):
    source: str; destination: str; travel_mode: str; agent_mode: str
    route: RouteInfo; traffic: TrafficInfo|None; weather: WeatherInfo; road: RoadInfo|None
    estimate: TimeEstimate; recommendation: str; activity: list[str]

class CommuteAgent:
    """Coordinates relevant tools and exposes only safe action/observation labels."""
    def _tools_for_mode(self,mode:str)->list[str]:
        return {"car":["traffic","weather","road"],"bike":["traffic","weather","road"],"bus":["traffic","weather"],"train":["weather"],"walking":["weather"]}[mode]
    def _llm_recommendation(self,context:str)->str|None:
        if not OPENAI_API_KEY: return None
        try:
            from openai import OpenAI
            client=OpenAI(api_key=OPENAI_API_KEY,base_url=OPENAI_BASE_URL or None)
            response=client.chat.completions.create(model=OPENAI_MODEL,temperature=0.2,messages=[{"role":"system","content":"Write one concise commute recommendation. Never describe simulated data as live. Do not expose reasoning."},{"role":"user","content":context}])
            return (response.choices[0].message.content or "").strip() or None
        except Exception: return None
    def run(self,source:str,destination:str,travel_mode:str)->CommuteResult:
        source,destination,travel_mode=source.strip(),destination.strip(),travel_mode.lower().strip()
        if not source: raise ValueError("Source cannot be empty.")
        if not destination: raise ValueError("Destination cannot be empty.")
        if travel_mode not in VALID_MODES: raise ValueError("Invalid travel mode. Choose car, bike, bus, train, or walking.")
        activity=["[1] Input validated.","[2] Finding route..."]; route=get_route(source,destination,travel_mode); activity[-1]="[2] Route information retrieved."
        selected=self._tools_for_mode(travel_mode); traffic=get_traffic(route.distance_km,travel_mode) if "traffic" in selected else None
        if traffic: activity.append("[3] Traffic checked (SIMULATED / DEMO).")
        weather=get_weather(route.source_coordinates.latitude,route.source_coordinates.longitude); activity.append("[4] Weather checked." if weather.available else "[4] Weather data unavailable; continuing.")
        road=get_road_conditions(source,destination,route.distance_km) if "road" in selected else None
        if road: activity.append("[5] Road condition checked (SIMULATED / DEMO).")
        estimate=estimate_time(route.base_time_minutes,traffic.delay_minutes if traffic else 0,weather,road.additional_delay_minutes if road else 0,travel_mode); activity.append("[6] Travel time calculated.")
        fallback=self._fallback_recommendation(traffic,weather,road,estimate)
        llm_recommendation=self._llm_recommendation(f"Mode: {travel_mode}; estimated range: {estimate.lower_bound}-{estimate.upper_bound} minutes; traffic: {traffic.traffic_level if traffic else 'not applicable'}; weather: {weather.condition}; road: {road.condition if road else 'not applicable'}; fallback: {fallback}")
        recommendation=llm_recommendation or fallback
        activity.append("[7] Recommendation generated.")
        return CommuteResult(source=source,destination=destination,travel_mode=travel_mode,agent_mode="LLM" if llm_recommendation else "Demo Fallback",route=route,traffic=traffic,weather=weather,road=road,estimate=estimate,recommendation=recommendation,activity=activity)
    @staticmethod
    def _fallback_recommendation(traffic,weather,road,estimate)->str:
        concerns=[]
        if traffic and traffic.traffic_level in {"HEAVY","SEVERE"}: concerns.append("simulated heavy traffic")
        if weather.affects_commute: concerns.append(f"{weather.condition.lower()} conditions")
        if road and road.condition=="POOR": concerns.append("simulated poor road conditions")
        return "Allow about 15 extra minutes because of " + " and ".join(concerns) + "." if concerns else f"Conditions are favorable. Plan for approximately {estimate.central_estimate} minutes."
