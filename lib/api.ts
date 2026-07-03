import type {
  Analytics, Battery, Carbon, Cost, Forecast,
  GridStatus, Renewables, Simulation, Storage, Telemetry, Weather,
} from "./types";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
export const WS_BASE = API_BASE.replace(/^http/, "ws");

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`API ${path} → ${response.status}`);
  return response.json() as Promise<T>;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!response.ok) throw new Error(`API POST ${path} → ${response.status}`);
  return response.json() as Promise<T>;
}

export const api = {
  forecast:   () => getJson<Forecast>("/forecast"),
  weather:    () => getJson<Weather>("/weather"),
  analytics:  () => getJson<Analytics>("/analytics"),
  battery:    () => getJson<Battery>("/battery"),
  storage:    () => getJson<Storage>("/storage"),
  renewables: () => getJson<Renewables>("/renewables"),
  carbon:     () => getJson<Carbon>("/carbon"),
  cost:       () => getJson<Cost>("/cost"),
  grid:       () => getJson<GridStatus>("/grid/status"),
  simulate:   (peak_demand_mw: number) =>
    postJson<Simulation>("/simulate", { scenario: "evening_peak", peak_demand_mw }),
  report:     (peak_demand_mw: number) =>
    postJson<Record<string, unknown>>("/report", { peak_demand_mw }),
  telemetryUrl: () => `${WS_BASE}/telemetry`,
};

export type MissionData = {
  forecast: Forecast;
  weather: Weather;
  analytics: Analytics;
  battery: Battery;
  storage: Storage;
  renewables: Renewables;
  carbon: Carbon;
  cost: Cost;
  grid: GridStatus;
};

export async function getMissionData(): Promise<MissionData> {
  const [forecast, weather, analytics, battery, storage, renewables, carbon, cost, grid] =
    await Promise.all([
      api.forecast(),
      api.weather(),
      api.analytics(),
      api.battery(),
      api.storage(),
      api.renewables(),
      api.carbon(),
      api.cost(),
      api.grid(),
    ]);
  return { forecast, weather, analytics, battery, storage, renewables, carbon, cost, grid };
}
