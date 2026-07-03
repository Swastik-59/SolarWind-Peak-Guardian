"""
SolarWind Peak Guardian — AI EMS Services
Physics-informed simulation with realistic renewable energy modelling.
"""
import math
from datetime import datetime, timezone

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

# ---------------------------------------------------------------------------
# Physics helpers
# ---------------------------------------------------------------------------

def _solar_output(hour: float, scale: float = 1.0, cloud_factor: float = 0.82) -> float:
    """Gaussian solar curve peaking at 13:00, zero outside 06:00-19:30."""
    if hour < 6 or hour > 19.5:
        return 0.0
    peak_mw = 180 * scale * cloud_factor
    sigma = 4.2
    return round(peak_mw * math.exp(-0.5 * ((hour - 13) / sigma) ** 2), 1)


def _wind_output(hour: float, scale: float = 1.0, speed_mps: float = 8.7) -> float:
    """Evening coastal wind ramp — increases 17:00-22:00, moderate daytime."""
    base = 65 * scale * (speed_mps / 9.0)
    if 17 <= hour <= 22:
        ramp = (hour - 17) / 5 * 0.55
        return round(base * (1 + ramp), 1)
    elif hour > 22 or hour < 6:
        return round(base * 0.88, 1)
    return round(base, 1)


def _demand_mw(hour: float, scale: float = 1.0) -> float:
    """Realistic demand curve with morning shoulder and evening peak."""
    if 0 <= hour < 6:
        base = 160
    elif 6 <= hour < 9:
        base = 200 + (hour - 6) * 20
    elif 9 <= hour < 17:
        base = 260 + math.sin((hour - 9) / 8 * math.pi) * 30
    elif 17 <= hour < 20:
        base = 290 + (hour - 17) / 3 * 60
    elif 20 <= hour < 22:
        base = 350 - (hour - 20) / 2 * 30
    else:
        base = 220
    return round(base * scale, 1)


def _battery_dispatch(demand: float, solar: float, wind: float, soc: float) -> float:
    """Li-Ion dispatches to cover shortfall; fast ramp up to 90 MW."""
    gap = demand - solar - wind
    if gap <= 0:
        return max(-30.0, -gap * 0.4)   # charge if surplus
    return round(min(gap, 90.0, soc * 0.9), 1)


def _caes_dispatch(demand: float, solar: float, wind: float, battery: float, hour: float) -> float:
    """CAES provides bulk delivery 18:00-22:00 when Li-Ion is insufficient."""
    if hour < 18 or hour > 23:
        return 0.0
    remaining_gap = demand - solar - wind - battery
    return round(max(0.0, min(remaining_gap, 120.0)), 1)


# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------

FORECAST_HOURS = [16, 17, 18, 19, 20, 21, 22]
SCALE_DEFAULT = 1.0


def _forecast_points(scale: float = 1.0) -> list[ForecastPoint]:
    points = []
    soc = 82.0  # battery starts at 82%
    for h in FORECAST_HOURS:
        solar = _solar_output(h, scale)
        wind = _wind_output(h, scale)
        demand = _demand_mw(h, scale)
        battery = _battery_dispatch(demand, solar, wind, soc)
        caes = _caes_dispatch(demand, solar, wind, battery, h)
        freq = 50.0 + math.sin(h * 0.7) * 0.04
        # Update SOC
        soc = max(10.0, soc - battery * 0.012)
        points.append(ForecastPoint(
            time=f"{h:02d}:00",
            demand_mw=demand,
            solar_mw=solar,
            wind_mw=wind,
            battery_mw=round(battery, 1),
            caes_mw=round(caes, 1),
            frequency_hz=round(freq, 3),
        ))
    return points


async def get_forecast() -> ForecastResponse:
    return ForecastResponse(
        horizon_hours=6,
        peak_window="17:00-22:00",
        confidence=0.91,
        points=_forecast_points(),
        ai_explanation=(
            "Demand rises 52% after 17:00 while solar falls to zero at 19:30. "
            "EMS pre-positions Li-Ion for fast frequency regulation and reserves "
            "CAES for 18:00-22:00 bulk delivery. Wind ramp reduces battery cycling by 34%."
        ),
    )


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------

async def get_weather() -> WeatherResponse:
    return WeatherResponse(
        condition="Coastal thermal wind ramp after sunset",
        temperature_c=31.4,
        wind_speed_mps=8.7,
        solar_irradiance_wm2=184,
        cloud_cover_percentage=18,
        forecast_note=(
            "Falling irradiance and strengthening evening sea breeze create a natural "
            "solar-to-wind handoff window. Expected wind output increase of 38% by 20:00."
        ),
    )


# ---------------------------------------------------------------------------
# Grid status (tick-aware for WebSocket)
# ---------------------------------------------------------------------------

async def get_grid_status(tick: int = 0) -> GridStatus:
    t = tick * 0.8          # slow oscillation
    demand = 318 + math.sin(t / 3) * 14
    wind_boost = math.cos(t / 2) * 8
    served = demand + wind_boost * 0.3
    frequency = 50.0 + math.sin(t / 4) * 0.055
    renewable_pct = 88.5 + math.cos(t / 5) * 2.4
    voltage = 220.0 + math.sin(t / 5) * 1.6

    if abs(frequency - 50) < 0.06:
        state = "stable"
    elif abs(frequency - 50) < 0.12:
        state = "watch"
    else:
        state = "intervention"

    actions = [
        "Hold Li-Ion droop response; dispatch CAES for bulk ramp.",
        "Wind ramp absorbed — reducing Li-Ion output by 8 MW.",
        "Frequency deviation detected — activating Li-Ion fast response.",
        "Solar handoff complete — wind + CAES covering full peak demand.",
    ]
    action = actions[tick % len(actions)]

    return GridStatus(
        frequency_hz=round(frequency, 3),
        renewable_percentage=round(renewable_pct, 1),
        demand_mw=round(demand, 1),
        served_mw=round(served, 1),
        stability_state=state,
        voltage_kv=round(voltage, 1),
        ai_action=action,
    )


# ---------------------------------------------------------------------------
# Battery / Storage
# ---------------------------------------------------------------------------

async def get_battery(tick: int = 0) -> BatteryStatus:
    soc = max(20.0, 78.0 - (tick % 28) * 0.95)
    output = round(62 + math.sin(tick / 2.2) * 12, 1)
    return BatteryStatus(
        state_of_charge_percentage=round(soc, 1),
        output_mw=output,
        response_time_ms=200,
        health_percentage=93.8,
        cycle_strategy=(
            "Shallow fast-response cycling (20-80% SOC window) to maximise cycle life "
            "while maintaining 200ms frequency regulation response."
        ),
    )


async def get_storage(tick: int = 0) -> StorageStatus:
    battery = await get_battery(tick)
    caes_soc = max(20.0, 86.0 - (tick % 22) * 0.82)
    caes_pressure = round(68 - (tick % 22) * 0.6, 1)
    caes_output = round(94 + math.cos(tick / 3.1) * 16, 1)
    hours_remaining = round(max(1.0, 8.2 - (tick % 14) * 0.11), 1)
    return StorageStatus(
        li_ion=battery,
        caes_pressure_bar=caes_pressure,
        caes_state_of_charge_percentage=round(caes_soc, 1),
        caes_output_mw=caes_output,
        duration_hours_remaining=hours_remaining,
        round_trip_efficiency_percentage=94,
    )


# ---------------------------------------------------------------------------
# Renewables
# ---------------------------------------------------------------------------

async def get_renewables(tick: int = 0) -> RenewablesResponse:
    hour = 19.0 + (tick % 60) / 60     # simulate 19:00-20:00 window
    solar = _solar_output(hour)
    wind = _wind_output(hour, speed_mps=8.7 + math.sin(tick / 8) * 1.2)
    li_ion_mw = round(64 + math.sin(tick / 2.5) * 10, 1)
    caes_mw = round(94 + math.cos(tick / 3.5) * 14, 1)
    total = solar + wind + li_ion_mw + caes_mw
    return RenewablesResponse(
        solar_mw=solar,
        wind_mw=round(wind, 1),
        solar_capacity_factor=round(solar / 720, 3) if solar > 0 else 0.0,
        wind_capacity_factor=round(wind / 200, 3),
        smart_grid_efficiency_percentage=94,
        source_mix={
            "solar": solar,
            "wind": round(wind, 1),
            "li_ion": li_ion_mw,
            "caes": caes_mw,
        },
    )


# ---------------------------------------------------------------------------
# Carbon / Cost / Analytics
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

async def run_simulation(request: SimulationRequest) -> SimulationResponse:
    scale = request.peak_demand_mw / 320.0

    # Physics-based phase calculations
    phases = []
    phase_specs = [
        ("08:00-17:00", "Solar Charging",
         "Solar PV feeds 60% of daytime demand while 40% pre-charges Li-Ion (C/3 rate) and drives CAES compression to 72 bar.",
         _solar_output(12, scale), _wind_output(10, scale),
         round(-38 * scale, 1), round(-28 * scale, 1), 50.04),
        ("17:00-19:00", "Wind + Storage Transition",
         "EMS detects solar ramp-down and rising demand; wind increases output while Li-Ion absorbs the frequency correction load.",
         _solar_output(18, scale), _wind_output(18, scale),
         round(72 * scale, 1), round(18 * scale, 1), 49.98),
        ("19:00-22:00", "Full Peak Coverage",
         "Wind and Li-Ion cover fast response; CAES turbines synchronised for long-duration bulk delivery at 50 Hz ± 0.05 Hz.",
         0.0, _wind_output(20, scale),
         round(82 * scale, 1), round(108 * scale, 1), 50.01),
        ("22:00-08:00", "Recovery + Recharge",
         "Off-peak wind energy recharges Li-Ion at C/5 rate and re-pressurises CAES. System autonomously ready for next peak cycle.",
         _solar_output(7, scale), _wind_output(2, scale),
         round(-18 * scale, 1), round(-22 * scale, 1), 50.05),
    ]

    for window, name, desc, solar, wind, battery, caes, freq in phase_specs:
        phases.append(PhaseStep(
            name=name, window=window, description=desc,
            solar_mw=round(solar, 1), wind_mw=round(wind, 1),
            battery_mw=battery, caes_mw=caes, grid_frequency_hz=freq,
        ))

    co2_avoided = round(411 * scale, 1)
    diesel_avoided = round(58240 * scale, 1)
    hres_cost = round(23680 * scale, 1)

    return SimulationResponse(
        scenario=request.scenario,
        phases=phases,
        ems_decisions=[
            EmsDecision(
                timestamp="17:08",
                decision=f"Battery output increased to {round(72*scale)} MW",
                reason="Solar ramp-down crossed 15 MW threshold; demand forecast rising at +18 MW/h.",
            ),
            EmsDecision(
                timestamp="18:42",
                decision="CAES armed for bulk discharge at 72 bar",
                reason="5+ hour peak window confirmed; Li-Ion SOC reserved above 35% for frequency correction.",
            ),
            EmsDecision(
                timestamp="19:04",
                decision=f"CAES synchronised — {round(108*scale)} MW injected",
                reason=f"Demand reached {round(request.peak_demand_mw)} MW; frequency dipped to 49.97 Hz.",
            ),
            EmsDecision(
                timestamp="22:11",
                decision="Recovery recharge initiated",
                reason="Load fell 28% below peak; wind supply exceeds demand — optimal recharge window.",
            ),
        ],
        outcomes={
            "co2_avoided_tonnes": co2_avoided,
            "diesel_cost_avoided_usd": diesel_avoided,
            "hres_cost_usd": hres_cost,
            "net_savings_usd": round(diesel_avoided - hres_cost, 1),
            "renewable_peak_coverage_percentage": 91.2,
            "frequency_deviation_hz": 0.04,
            "peak_demand_mw": request.peak_demand_mw,
        },
    )


# ---------------------------------------------------------------------------
# WebSocket telemetry frame
# ---------------------------------------------------------------------------

async def next_telemetry(tick: int) -> TelemetryFrame:
    return TelemetryFrame(
        tick=tick,
        timestamp=datetime.now(timezone.utc).isoformat(),
        grid=await get_grid_status(tick),
        storage=await get_storage(tick),
        renewables=await get_renewables(tick),
        carbon=await get_carbon(),
        cost=await get_cost(),
    )
