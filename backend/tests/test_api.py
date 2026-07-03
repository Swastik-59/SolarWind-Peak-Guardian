"""
SolarWind Peak Guardian — API test suite.
All tests run against the FastAPI TestClient (no server needed).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Core endpoint availability
# ---------------------------------------------------------------------------

def test_core_endpoints_return_required_operational_payloads():
    endpoints = [
        "/forecast", "/weather", "/analytics", "/battery",
        "/storage", "/renewables", "/carbon", "/cost",
        "/grid", "/grid/status", "/health",
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, f"FAILED: {endpoint}"
        body = response.json()
        assert isinstance(body, dict) and body, f"Empty body: {endpoint}"


# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------

def test_forecast_models_evening_peak_window_and_ai_decisions():
    body = client.get("/forecast").json()
    assert body["peak_window"] == "17:00-22:00"
    assert len(body["points"]) >= 6
    assert any(p["demand_mw"] > p["solar_mw"] for p in body["points"])
    assert body["ai_explanation"]
    assert body["confidence"] > 0.8


def test_forecast_physics_solar_drops_at_19():
    points = {p["time"]: p for p in client.get("/forecast").json()["points"]}
    assert points["16:00"]["solar_mw"] > points["19:00"]["solar_mw"]
    assert points["19:00"]["solar_mw"] < points["16:00"]["solar_mw"] * 0.5  # solar declining rapidly


def test_forecast_wind_increases_during_peak():
    points = client.get("/forecast").json()["points"]
    wind_16 = next(p["wind_mw"] for p in points if p["time"] == "16:00")
    wind_20 = next(p["wind_mw"] for p in points if p["time"] == "20:00")
    assert wind_20 > wind_16


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def test_simulation_returns_phase_timeline_and_outcomes():
    body = client.post("/simulate", json={"scenario": "evening_peak", "peak_demand_mw": 320}).json()
    assert body["scenario"] == "evening_peak"
    assert len(body["phases"]) == 4
    assert body["outcomes"]["co2_avoided_tonnes"] > 0
    assert body["outcomes"]["diesel_cost_avoided_usd"] > body["outcomes"]["hres_cost_usd"]
    assert "CAES" in " ".join(d["decision"] for d in body["ems_decisions"])


def test_simulation_scales_with_demand():
    body_200 = client.post("/simulate", json={"peak_demand_mw": 200}).json()
    body_400 = client.post("/simulate", json={"peak_demand_mw": 400}).json()
    assert body_400["outcomes"]["co2_avoided_tonnes"] > body_200["outcomes"]["co2_avoided_tonnes"]
    assert body_400["outcomes"]["net_savings_usd"] > body_200["outcomes"]["net_savings_usd"]


def test_simulation_rejects_out_of_range_demand():
    r = client.post("/simulate", json={"peak_demand_mw": 1000})
    assert r.status_code == 422

    r2 = client.post("/simulate", json={"peak_demand_mw": 10})
    assert r2.status_code == 422


# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------

def test_grid_status_exposes_frequency_and_renewable_share():
    body = client.get("/grid/status").json()
    assert 49.5 <= body["frequency_hz"] <= 50.5
    assert body["renewable_percentage"] >= 80
    assert body["stability_state"] in {"stable", "watch", "intervention"}
    assert body["voltage_kv"] > 0


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def test_storage_has_both_li_ion_and_caes():
    body = client.get("/storage").json()
    assert "li_ion" in body
    assert body["li_ion"]["response_time_ms"] == 200
    assert body["caes_pressure_bar"] > 0
    assert body["duration_hours_remaining"] > 0
    assert body["round_trip_efficiency_percentage"] == 94


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def test_report_endpoint_returns_structured_operator_summary():
    body = client.post("/report", json={"peak_demand_mw": 320}).json()
    assert "simulation" in body
    assert "performance" in body
    assert "economics" in body
    assert "carbon" in body
    assert body["performance"]["renewable_peak_coverage_percentage"] > 80
    assert body["performance"]["grid_stability_score"] > 90
