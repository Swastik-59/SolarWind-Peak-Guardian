export type ForecastPoint = {
  time: string;
  demand_mw: number;
  solar_mw: number;
  wind_mw: number;
  battery_mw: number;
  caes_mw: number;
  frequency_hz: number;
};

export type Forecast = { horizon_hours: number; peak_window: string; confidence: number; points: ForecastPoint[]; ai_explanation: string };
export type GridStatus = { frequency_hz: number; renewable_percentage: number; demand_mw: number; served_mw: number; stability_state: string; voltage_kv: number; ai_action: string };
export type Battery = { state_of_charge_percentage: number; output_mw: number; response_time_ms: number; health_percentage: number; cycle_strategy: string };
export type Storage = { li_ion: Battery; caes_pressure_bar: number; caes_state_of_charge_percentage: number; caes_output_mw: number; duration_hours_remaining: number; round_trip_efficiency_percentage: number };
export type Renewables = { solar_mw: number; wind_mw: number; solar_capacity_factor: number; wind_capacity_factor: number; smart_grid_efficiency_percentage: number; source_mix: Record<string, number> };
export type Carbon = { co2_avoided_tonnes_year: number; co2_avoided_tonnes_today: number; diesel_mwh_displaced: number; sdg_alignment: string[] };
export type Cost = { hres_lcoe_usd_mwh: number; diesel_peaker_usd_mwh: number; annual_savings_usd_million: number; capex_usd_mw_million: number; payback_years: number; ancillary_revenue_usd_million: number };
export type Analytics = { efficiency_gain_percentage: number; grid_stability_score: number; storage_cycles_saved: number; renewable_peak_coverage_percentage: number; brownout_risk_reduction_percentage: number; telemetry: ForecastPoint[] };
export type Weather = { condition: string; temperature_c: number; wind_speed_mps: number; solar_irradiance_wm2: number; cloud_cover_percentage: number; forecast_note: string };
export type Simulation = {
  scenario: string;
  phases: { name: string; window: string; description: string; solar_mw: number; wind_mw: number; battery_mw: number; caes_mw: number; grid_frequency_hz: number }[];
  ems_decisions: { timestamp: string; decision: string; reason: string }[];
  outcomes: Record<string, number>;
};
export type Telemetry = { tick: number; grid: GridStatus; storage: Storage; renewables: Renewables; carbon: Carbon; cost: Cost };
