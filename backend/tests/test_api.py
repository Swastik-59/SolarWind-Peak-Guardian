from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_core_endpoints_return_required_operational_payloads():
    endpoints = [
        "/forecast",
        "/weather",
        "/analytics",
        "/battery",
        "/storage",
        "/renewables",
        "/carbon",
        "/cost",
        "/grid",
        "/grid/status",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, endpoint
        body = response.json()
        assert isinstance(body, dict)
        assert body


def test_forecast_models_evening_peak_window_and_ai_decisions():
    response = client.get("/forecast")

    assert response.status_code == 200
    body = response.json()
    assert body["horizon_hours"] == 2
    assert body["peak_window"] == "17:00-22:00"
    assert len(body["points"]) >= 6
    assert any(point["demand_mw"] > point["solar_mw"] for point in body["points"])
    assert body["ai_explanation"]


def test_simulation_returns_phase_timeline_and_outcomes():
    response = client.post("/simulate", json={"scenario": "evening_peak", "peak_demand_mw": 320})

    assert response.status_code == 200
    body = response.json()
    assert body["scenario"] == "evening_peak"
    assert len(body["phases"]) == 4
    assert body["outcomes"]["co2_avoided_tonnes"] > 0
    assert body["outcomes"]["diesel_cost_avoided_usd"] > body["outcomes"]["hres_cost_usd"]
    assert "CAES" in " ".join(step["decision"] for step in body["ems_decisions"])


def test_grid_status_exposes_frequency_and_renewable_share():
    response = client.get("/grid/status")

    assert response.status_code == 200
    body = response.json()
    assert 49.5 <= body["frequency_hz"] <= 50.5
    assert body["renewable_percentage"] >= 80
    assert body["stability_state"] in {"stable", "watch", "intervention"}
