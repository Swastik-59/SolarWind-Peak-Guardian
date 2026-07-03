from typing import Optional
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    time: str
    demand_mw: float
    solar_mw: float
    wind_mw: float
    battery_mw: float
    caes_mw: float
    frequency_hz: float


class ForecastResponse(BaseModel):
    horizon_hours: int
    peak_window: str
    confidence: float
    points: list[ForecastPoint]
    ai_explanation: str


class WeatherResponse(BaseModel):
    condition: str
    temperature_c: float
    wind_speed_mps: float
    solar_irradiance_wm2: float
    cloud_cover_percentage: float
    forecast_note: str


class GridStatus(BaseModel):
    frequency_hz: float
    renewable_percentage: float
    demand_mw: float
    served_mw: float
    stability_state: str        # "stable" | "watch" | "intervention"
    voltage_kv: float
    ai_action: str


class BatteryStatus(BaseModel):
    state_of_charge_percentage: float
    output_mw: float
    response_time_ms: int
    health_percentage: float
    cycle_strategy: str


class StorageStatus(BaseModel):
    li_ion: BatteryStatus
    caes_pressure_bar: float
    caes_state_of_charge_percentage: float
    caes_output_mw: float
    duration_hours_remaining: float
    round_trip_efficiency_percentage: float


class RenewablesResponse(BaseModel):
    solar_mw: float
    wind_mw: float
    solar_capacity_factor: float
    wind_capacity_factor: float
    smart_grid_efficiency_percentage: float
    source_mix: dict[str, float]


class CarbonResponse(BaseModel):
    co2_avoided_tonnes_year: float
    co2_avoided_tonnes_today: float
    diesel_mwh_displaced: float
    sdg_alignment: list[str]


class CostResponse(BaseModel):
    hres_lcoe_usd_mwh: float
    diesel_peaker_usd_mwh: float
    annual_savings_usd_million: float
    capex_usd_mw_million: float
    payback_years: float
    ancillary_revenue_usd_million: float


class AnalyticsResponse(BaseModel):
    efficiency_gain_percentage: float
    grid_stability_score: float
    storage_cycles_saved: int
    renewable_peak_coverage_percentage: float
    brownout_risk_reduction_percentage: float
    telemetry: list[ForecastPoint]


class SimulationRequest(BaseModel):
    scenario: str = Field(default="evening_peak")
    peak_demand_mw: float = Field(default=320, ge=50, le=500)


class PhaseStep(BaseModel):
    name: str
    window: str
    description: str
    solar_mw: float
    wind_mw: float
    battery_mw: float
    caes_mw: float
    grid_frequency_hz: float


class EmsDecision(BaseModel):
    timestamp: str
    decision: str
    reason: str


class SimulationResponse(BaseModel):
    scenario: str
    phases: list[PhaseStep]
    ems_decisions: list[EmsDecision]
    outcomes: dict[str, float]


class TelemetryFrame(BaseModel):
    tick: int
    timestamp: str
    grid: GridStatus
    storage: StorageStatus
    renewables: RenewablesResponse
    carbon: CarbonResponse
    cost: CostResponse


class ReportRequest(BaseModel):
    peak_demand_mw: float = Field(default=320, ge=50, le=500)
    include_financials: bool = True
    include_carbon: bool = True
