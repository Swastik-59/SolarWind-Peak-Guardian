import math
from datetime import datetime

from .models import (
    AnalyticsResponse,
    BatteryStatus,
    CarbonResponse,
    CostResponse,
    EmsDecision,
    ForecastPoint,
    ForecastResponse,
    GridStatus,
    PhaseStep,
    RenewablesResponse,
    SimulationRequest,
    SimulationResponse,
    StorageStatus,
    TelemetryFrame,
    WeatherResponse,
)


def _forecast_points(scale: float = 1.0) -> list[ForecastPoint]:
    rows = [
        ("16:00", 210, 116, 58, 18, 0, 50.03),
        ("17:00", 254, 72, 76, 36, 0, 50.01),
        ("18:00", 308, 22, 93, 74, 24, 49.98),
        ("19:00", 338, 0, 104, 86, 82, 50.00),
        ("20:00", 326, 0, 96, 72, 104, 50.02),
        ("21:00", 286, 0, 88, 54, 82, 50.04),
        ("22:00", 224, 0, 71, 28, 48, 50.05),
    ]
    return [
        ForecastPoint(
            time=time,
            demand_mw=round(demand * scale, 1),
            solar_mw=round(solar * scale, 1),
            wind_mw=round(wind * scale, 1),
            battery_mw=round(battery * scale, 1),
            caes_mw=round(caes * scale, 1),
            frequency_hz=freq,
        )
        for time, demand, solar, wind, battery, caes, freq in rows
    ]


async def get_forecast() -> ForecastResponse:
    return ForecastResponse(
        horizon_hours=2,
        peak_window="17:00-22:00",
        confidence=0.91,
        points=_forecast_points(),
        ai_explanation=(
            "Demand is expected to rise 52% after 17:00 while solar falls to zero. "
            "EMS is pre-positioning Li-Ion for fast regulation and reserving CAES for 19:00-22:00 bulk delivery."
        ),
    )


async def get_weather() -> WeatherResponse:
    return WeatherResponse(
        condition="Coastal thermal wind ramp after sunset",
        temperature_c=31.4,
        wind_speed_mps=8.7,
        solar_irradiance_wm2=184,
        cloud_cover_percentage=18,
        forecast_note="Falling irradiance and strengthening evening wind create favorable solar-to-wind handoff conditions.",
    )


async def get_grid_status(tick: int = 0) -> GridStatus:
    demand = 318 + math.sin(tick / 3) * 16
    served = demand + math.cos(tick / 2) * 2
    frequency = 50 + math.sin(tick / 4) * 0.06
    return GridStatus(
        frequency_hz=round(frequency, 3),
        renewable_percentage=round(88 + math.cos(tick / 5) * 3, 1),
        demand_mw=round(demand, 1),
        served_mw=round(served, 1),
        stability_state="stable" if abs(frequency - 50) < 0.08 else "watch",
        voltage_kv=round(220 + math.sin(tick / 5) * 1.8, 1),
        ai_action="Hold Li-Ion droop response; dispatch CAES for bulk ramp.",
    )


async def get_battery(tick: int = 0) -> BatteryStatus:
    return BatteryStatus(
        state_of_charge_percentage=round(76 - (tick % 20) * 1.1, 1),
        output_mw=round(64 + math.sin(tick / 2) * 14, 1),
        response_time_ms=200,
        health_percentage=93.8,
        cycle_strategy="Fast response frequency regulation with shallow cycling to reduce wear.",
    )


async def get_storage(tick: int = 0) -> StorageStatus:
    battery = await get_battery(tick)
    return StorageStatus(
        li_ion=battery,
        caes_pressure_bar=round(68 - (tick % 18) * 0.7, 1),
        caes_state_of_charge_percentage=round(84 - (tick % 18) * 0.9, 1),
        caes_output_mw=round(92 + math.cos(tick / 3) * 18, 1),
        duration_hours_remaining=round(7.8 - (tick % 12) * 0.12, 1),
        round_trip_efficiency_percentage=94,
    )


async def get_renewables(tick: int = 0) -> RenewablesResponse:
    solar = max(0, 42 - tick * 2.2)
    wind = 92 + math.sin(tick / 3) * 14
    return RenewablesResponse(
        solar_mw=round(solar, 1),
        wind_mw=round(wind, 1),
        solar_capacity_factor=0.25,
        wind_capacity_factor=0.47,
        smart_grid_efficiency_percentage=94,
        source_mix={"solar": round(solar, 1), "wind": round(wind, 1), "li_ion": 68, "caes": 96},
    )


async def get_carbon() -> CarbonResponse:
    return CarbonResponse(
        co2_avoided_tonnes_year=150000,
        co2_avoided_tonnes_today=411,
        diesel_mwh_displaced=642,
        sdg_alignment=["SDG 7 Affordable Clean Energy", "SDG 13 Climate Action"],
    )


async def get_cost() -> CostResponse:
    return CostResponse(
        hres_lcoe_usd_mwh=74,
        diesel_peaker_usd_mwh=182,
        annual_savings_usd_million=21.6,
        capex_usd_mw_million=2.1,
        payback_years=9.4,
        ancillary_revenue_usd_million=3.8,
    )


async def get_analytics() -> AnalyticsResponse:
    return AnalyticsResponse(
        efficiency_gain_percentage=16.2,
        grid_stability_score=97.4,
        storage_cycles_saved=128,
        renewable_peak_coverage_percentage=91.2,
        brownout_risk_reduction_percentage=86.5,
        telemetry=_forecast_points(),
    )


async def run_simulation(request: SimulationRequest) -> SimulationResponse:
    scale = request.peak_demand_mw / 320
    phases = [
        PhaseStep(name="Solar Charging", window="08:00-17:00", description="60% feeds daytime grid demand while 40% charges Li-Ion and compresses air for CAES.", solar_mw=168*scale, wind_mw=42*scale, battery_mw=-38*scale, caes_mw=-28*scale, grid_frequency_hz=50.04),
        PhaseStep(name="Wind + Storage Transition", window="17:00-19:00", description="EMS detects sunset and rising demand, then blends wind with controlled Li-Ion discharge.", solar_mw=24*scale, wind_mw=92*scale, battery_mw=74*scale, caes_mw=22*scale, grid_frequency_hz=49.98),
        PhaseStep(name="Full Peak Coverage", window="19:00-22:00", description="CAES turbines activate for long-duration bulk delivery while Li-Ion regulates frequency within +/-0.5 Hz.", solar_mw=0, wind_mw=104*scale, battery_mw=82*scale, caes_mw=112*scale, grid_frequency_hz=50.01),
        PhaseStep(name="Recovery + Recharge", window="22:00-08:00", description="Demand drops and available wind plus morning solar restore storage without manual intervention.", solar_mw=36*scale, wind_mw=70*scale, battery_mw=-18*scale, caes_mw=-24*scale, grid_frequency_hz=50.05),
    ]
    return SimulationResponse(
        scenario=request.scenario,
        phases=phases,
        ems_decisions=[
            EmsDecision(timestamp="17:08", decision="Battery output increased to 74 MW", reason="Solar ramp-down crossed demand forecast threshold."),
            EmsDecision(timestamp="18:42", decision="CAES armed for bulk discharge", reason="Forecast shows 5+ hour peak window; Li-Ion reserved for fast frequency correction."),
            EmsDecision(timestamp="19:04", decision="CAES synchronized to grid", reason="Demand reached 320 MW and frequency dipped to 49.98 Hz."),
            EmsDecision(timestamp="22:11", decision="Recovery recharge started", reason="Load fell below forecast baseline and wind remains available."),
        ],
        outcomes={
            "co2_avoided_tonnes": round(411 * scale, 1),
            "diesel_cost_avoided_usd": round(58240 * scale, 1),
            "hres_cost_usd": round(23680 * scale, 1),
            "renewable_peak_coverage_percentage": 91.2,
            "frequency_deviation_hz": 0.04,
        },
    )


async def next_telemetry(tick: int) -> TelemetryFrame:
    return TelemetryFrame(
        tick=tick,
        grid=await get_grid_status(tick),
        storage=await get_storage(tick),
        renewables=await get_renewables(tick),
        carbon=await get_carbon(),
        cost=await get_cost(),
    )
