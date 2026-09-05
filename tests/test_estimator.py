import pytest
from tools.weather_tool import WeatherInfo
from tools.time_estimator import estimate_time,get_weather_delay

@pytest.mark.parametrize("mode,minimum",[("car",5),("bike",10),("train",2),("walking",12)])
def test_weather_delay_by_mode(mode,minimum):
    assert get_weather_delay(WeatherInfo(available=True,severity="MODERATE"),mode)>=minimum

@pytest.mark.parametrize("mode",["car","bike","train","walking"])
def test_time_range_contains_central_estimate(mode):
    estimate=estimate_time(40,15,WeatherInfo(available=True,severity="HIGH"),5,mode)
    assert estimate.central_estimate==40+15+5+estimate.weather_delay_minutes
    assert estimate.lower_bound<estimate.central_estimate<estimate.upper_bound
