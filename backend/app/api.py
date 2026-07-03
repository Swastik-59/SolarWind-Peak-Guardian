import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from .models import ReportRequest, SimulationRequest
from .services import (
    get_analytics,
    get_battery,
    get_carbon,
    get_cost,
    get_forecast,
    get_grid_status,
    get_renewables,
    get_storage,
    get_weather,
    next_telemetry,
    run_simulation,
)

router = APIRouter()


@router.get("/forecast")
async def forecast():
    return await get_forecast()


@router.get("/weather")
async def weather():
    return await get_weather()


@router.get("/analytics")
async def analytics():
    return await get_analytics()


@router.get("/battery")
async def battery():
    return await get_battery()


@router.get("/storage")
async def storage():
    return await get_storage()


@router.get("/renewables")
async def renewables():
    return await get_renewables()


@router.get("/carbon")
async def carbon():
    return await get_carbon()


@router.get("/cost")
async def cost():
    return await get_cost()


@router.get("/grid")
@router.get("/grid/status")
async def grid_status():
    return await get_grid_status()


@router.post("/simulate")
async def simulate(request: SimulationRequest):
    return await run_simulation(request)


@router.post("/report")
async def generate_report(request: ReportRequest):
    """Generate a structured operator report combining simulation + analytics."""
    sim_req = SimulationRequest(scenario="evening_peak", peak_demand_mw=request.peak_demand_mw)
    simulation = await run_simulation(sim_req)
    analytics = await get_analytics()
    carbon = await get_carbon()
    cost = await get_cost()
    forecast = await get_forecast()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system": "SolarWind Peak Guardian — AI Hybrid Renewable Energy System",
        "operating_condition": "Condition 1: Increased electricity demand during evening peak hours",
        "renewable_sources": ["Solar PV", "Wind Energy", "Hybrid Storage (Li-Ion + CAES)"],
        "simulation": simulation.model_dump(),
        "performance": {
            "grid_stability_score": analytics.grid_stability_score,
            "renewable_peak_coverage_percentage": analytics.renewable_peak_coverage_percentage,
            "efficiency_gain_percentage": analytics.efficiency_gain_percentage,
            "brownout_risk_reduction_percentage": analytics.brownout_risk_reduction_percentage,
        },
        "carbon": carbon.model_dump() if request.include_carbon else None,
        "economics": cost.model_dump() if request.include_financials else None,
        "forecast_points": [p.model_dump() for p in forecast.points],
        "sdg_alignment": ["SDG 7 Affordable Clean Energy", "SDG 13 Climate Action"],
    }
    return JSONResponse(content=report)


@router.websocket("/telemetry")
async def telemetry(websocket: WebSocket):
    await websocket.accept()
    tick = 0
    try:
        while True:
            frame = await next_telemetry(tick)
            await websocket.send_json(frame.model_dump())
            tick += 1
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.close()
