from unittest.mock import Mock, patch
import pytest
from services.geocoding import Location
from tools.route_tool import get_route
from tools.weather_tool import get_weather
from tools.traffic_tool import get_traffic
from tools.road_tool import get_road_conditions
from agent import CommuteAgent

@patch("tools.route_tool.geocode_location")
@patch("tools.route_tool.requests.get")
def test_route_response_structure(mock_get,mock_geocode):
    mock_geocode.side_effect=[Location(latitude=13.08,longitude=80.27,display_name="A"),Location(latitude=12.99,longitude=80.17,display_name="B")]
    response=Mock(); response.raise_for_status.return_value=None; response.json.return_value={"routes":[{"distance":20000,"duration":2400}]}; mock_get.return_value=response
    route=get_route("A","B","car")
    assert route.status=="success" and route.distance_km==20 and route.base_time_minutes==40

@patch("tools.weather_tool.requests.get")
def test_weather_classification(mock_get):
    response=Mock(); response.raise_for_status.return_value=None; response.json.return_value={"current":{"temperature_2m":29,"apparent_temperature":31,"precipitation":1,"weather_code":61,"wind_speed_10m":12},"hourly":{"precipitation_probability":[70]}}; mock_get.return_value=response
    weather=get_weather(13,80)
    assert weather.available and weather.category=="RAIN" and weather.affects_commute

def test_simulated_traffic_categories():
    traffic=get_traffic(20,"car",hour=8)
    assert traffic.traffic_level in {"LOW","MODERATE","HEAVY","SEVERE"} and traffic.data_source=="SIMULATED / DEMO"

def test_road_condition_is_deterministic():
    assert get_road_conditions("A","B",20)==get_road_conditions("A","B",20)

@pytest.mark.parametrize("source,destination,mode",[("","B","car"),("A","","car"),("A","B","plane")])
def test_input_validation(source,destination,mode):
    with pytest.raises(ValueError): CommuteAgent().run(source,destination,mode)
