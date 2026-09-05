# ReAct-Based Intelligent Commute Agent

A simple terminal-only Python project that estimates a commute using route, weather, traffic, and road-condition tools. It is designed to be easy to explain in a college viva.

## Objective and features

Enter a source, destination, and travel method (car, bike, bus, train, or walking). The program reports distance, base time, traffic delay, weather impact, road delay, an estimated time range, and a practical recommendation.

The output shows safe ReAct activity messages: validate → choose tools → act → observe → estimate → recommend. These are high-level status updates, not private model chain-of-thought.

## Tools and data

- Route/geocoding: OSRM and OpenStreetMap Nominatim.
- Weather: Open-Meteo, without an API key.
- Traffic: deterministic `SIMULATED / DEMO` data, never live traffic.
- Road condition: deterministic `SIMULATED / DEMO` data, never live road data.
- OpenAI: optional. With `OPENAI_API_KEY`, the current OpenAI Python SDK can help word the final recommendation. Without it, the deterministic fallback works fully.

Bus and train are labelled demo transit estimates because OSRM does not provide public-transport schedules.

## Structure

```text
main.py            terminal entry point
agent.py           ReAct-style coordinator
config.py          environment configuration
tools/             route, weather, traffic, road, and time tools
services/          Nominatim geocoding helper
tests/             offline-friendly pytest tests
```

## Install and run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

Leave `OPENAI_API_KEY=` empty in `.env` to use **Agent Mode: Demo Fallback**. No other key is required.

## Example terminal output

```text
Distance: 19.8 km
Traffic: HEAVY
Traffic Data Source: SIMULATED / DEMO
Weather: Rain
Estimated Travel Time: 63-73 minutes
Recommendation: Allow about 15 extra minutes because of simulated heavy traffic and rain conditions.
Agent Mode: Demo Fallback
```

## Tests

```powershell
python -m pytest tests -q
```

## Limitations and future work

Public route/weather APIs can be unavailable; the app handles failures gracefully. Weather is taken near the source, not across the entire route. Traffic and road data are simulations. Future versions could plug in real traffic, road, and transit-schedule APIs, cache results, and add route alternatives.
