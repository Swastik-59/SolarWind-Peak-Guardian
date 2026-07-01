import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .models import SimulationRequest
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


@router.websocket("/telemetry")
async def telemetry(websocket: WebSocket):
    await websocket.accept()
    tick = 0
    try:
        while True:
            await websocket.send_json((await next_telemetry(tick)).model_dump())
            tick += 1
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
