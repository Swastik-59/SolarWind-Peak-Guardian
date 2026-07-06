# SolarWind Peak Guardian Summary

## What This Project Is

SolarWind Peak Guardian is a prototype AI-powered hybrid renewable energy management system focused on fossil-free evening peak demand management. The project is presented as a mission-control style dashboard for a national-scale grid problem: solar output falls in the evening, demand rises, and the system must coordinate solar, wind, lithium-ion storage, and compressed air energy storage (CAES) to keep the grid stable without relying on diesel peaker plants.

The codebase is split into two main parts:

- A Next.js frontend that presents the system as an interactive operations dashboard.
- A FastAPI backend that simulates renewable output, grid behavior, storage response, economics, carbon impact, and operator reports.

## What It Does

The application demonstrates how a hybrid renewable energy system could manage the 17:00-22:00 evening peak window. It visualizes the problem, shows the control strategy, and generates simulated operational results.

At a product level, it provides:

- A live mission dashboard with animated energy flows.
- Forecasts for demand, solar, wind, battery dispatch, CAES dispatch, and grid frequency.
- Weather, storage, renewables, carbon, cost, and analytics snapshots.
- A simulation workflow that models evening peak operation in phases.
- A structured operator report combining simulation, performance, carbon, and financial data.
- A WebSocket telemetry stream to keep the UI feeling live.

## How It Works

### Frontend Flow

The frontend is built with Next.js and renders a single immersive page. The home route mounts a `LenisProvider` and the `MissionExperience` component, which acts as the entire presentation and control surface.

`MissionExperience` does three important things:

- Fetches all mission data from the backend using `lib/api.ts`.
- Opens a WebSocket connection to the backend telemetry stream.
- Lets the user trigger an evening peak simulation and view the resulting decisions.

The UI is organized into themed sections:

- The problem section visualizes the duck curve and the evening peak challenge.
- The control section shows a digital twin of solar, wind, AI EMS, battery, CAES, and grid nodes.
- The source sections describe how each asset contributes to the system.
- The simulator section runs the peak sequence and displays EMS decisions.
- The results section highlights carbon and cost comparisons.
- The reports and settings section frames the output as an operator-ready artifact.

The UI uses `framer-motion` for animation, `recharts` for charts, `zustand` for mission state, `react-hook-form` for settings inputs, and `lucide-react` icons for visual identity.

### Backend Flow

The backend is a FastAPI application defined in `backend/app/main.py`. It enables CORS for the local frontend, adds gzip compression, exposes health and root endpoints, and mounts the API router from `backend/app/api.py`.

The router exposes the main domain endpoints:

- `GET /forecast`
- `GET /weather`
- `GET /analytics`
- `GET /battery`
- `GET /storage`
- `GET /renewables`
- `GET /carbon`
- `GET /cost`
- `GET /grid` and `GET /grid/status`
- `POST /simulate`
- `POST /report`
- `GET /telemetry` as a WebSocket feed

The implementation lives in `backend/app/services.py`. That file contains the actual simulation logic, including:

- Solar production curves that peak around midday and fall away in the evening.
- Wind output that ramps during the evening window.
- Demand curves that rise into the evening peak.
- Battery dispatch logic for fast response and shortfall coverage.
- CAES dispatch logic for longer-duration peak delivery.
- Forecast generation across the 16:00-22:00 period.
- Grid status calculations with frequency, renewable percentage, voltage, and AI action text.
- Storage, renewables, carbon, cost, and analytics snapshots.
- A four-phase simulation model that describes the operating cycle from daytime charging through recovery.

The backend models in `backend/app/models.py` define the API shapes with Pydantic, so the frontend receives structured objects for forecasting, telemetry, simulation, economics, and reporting.

### Data Flow

The frontend gets its initial dashboard state from a single aggregated call in `lib/api.ts`. That helper fetches all core endpoints in parallel and returns one combined `MissionData` object.

After the page loads:

1. The dashboard displays the fetched forecast, weather, analytics, battery, storage, renewables, carbon, cost, and grid data.
2. A WebSocket connection streams live telemetry frames from `/telemetry`.
3. When the user runs the simulation, the frontend posts to `/simulate` with a target peak demand.
4. The simulation result is stored in local mission state and shown in the simulator and report areas.

## Codebase Structure

### Frontend

- `app/page.tsx`: Home route that mounts the mission experience.
- `app/layout.tsx`: Global HTML shell and metadata.
- `app/globals.css`: Application styling and theme rules.
- `components/mission/mission-experience.tsx`: Main dashboard, charts, animation, simulator, and UI composition.
- `components/lenis-provider.tsx`: Smooth scrolling provider.
- `lib/api.ts`: API client and data aggregation helper.
- `lib/content.ts`: Static narrative content for challenges, sources, phases, use cases, justification, and disadvantages.
- `lib/types.ts`: Shared TypeScript types for API payloads.
- `store/mission-store.ts`: Zustand store for telemetry, simulation state, and UI activity.

### Backend

- `backend/app/main.py`: FastAPI app setup, middleware, and health/root routes.
- `backend/app/api.py`: REST and WebSocket routes.
- `backend/app/models.py`: Pydantic request and response models.
- `backend/app/services.py`: Simulation and data-generation logic.
- `backend/tests/test_api.py`: API tests that validate the core operational behavior.

## Key Behaviors in the Simulation

The simulation is deliberately physics-inspired rather than random. It does not pull from a live grid model or an external optimizer; instead, `backend/app/services.py` uses deterministic helper functions to produce a believable operating picture from a few input assumptions. The goal is to simulate how the system would behave under evening peak stress, not to forecast a real utility network.

At a high level, the simulation works in four layers:

1. It builds time-based curves for solar, wind, and demand.
2. It applies dispatch rules for Li-ion batteries and CAES.
3. It packages the result into phase-by-phase operating steps.
4. It computes the final business and operational outcomes.

### 1. Time-based generation curves

The backend starts with simple physics-inspired functions:

- Solar is strong during the day and falls off quickly near sunset.
- Wind strengthens in the evening and compensates for the solar drop.
- Li-ion batteries provide fast frequency response and short-duration balancing.
- CAES provides the longer-duration bulk energy needed to carry the full evening peak.
- The system reports grid frequency, renewable share, emissions avoided, and economic comparison against diesel peakers.

Solar output is modeled with a Gaussian-like curve that peaks near midday and drops to zero outside daylight hours. Wind output is modeled as a gentler base supply with an evening ramp between roughly 17:00 and 22:00. Demand follows a separate daily load curve with a morning shoulder, a daytime plateau, and a steep evening rise. Those three curves create the duck-curve style mismatch the dashboard is built around.

### 2. Dispatch logic

Once demand and generation are known, the service layer decides how storage should respond.

- Li-ion batteries handle fast balancing first because they can respond in about 200 ms and are best suited for short, sharp gaps between supply and demand.
- CAES is reserved for bulk delivery when the evening peak is long enough that batteries alone would not be sufficient.

The battery dispatch rule looks at the supply gap between demand and renewables. If there is surplus generation, the battery charges. If there is a shortfall, the battery discharges up to a capped maximum and is limited by the remaining state of charge. CAES then covers any remaining gap during the evening discharge window, which lets the simulation show a realistic handoff between fast storage and long-duration storage.

### 3. Forecast and telemetry generation

The forecast endpoint produces a sequence of hourly points from 16:00 to 22:00. Each point includes demand, solar, wind, battery output, CAES output, and grid frequency. This makes the forecast chart in the frontend read like an operator planning tool rather than a generic visualization.

The telemetry feed uses the same underlying model but varies over time with a `tick` value. Every second, the WebSocket endpoint emits a new telemetry frame containing grid status, storage state, renewable production, carbon impact, and cost. That is what makes the dashboard feel live even though the underlying values are generated locally.

### 4. Simulation phases

The `POST /simulate` endpoint turns the system into a four-stage operating narrative:

- `08:00-17:00` Solar Charging: solar supplies daytime demand, while extra energy charges Li-ion and compresses air for CAES.
- `17:00-19:00` Wind + Storage Transition: solar falls away, wind rises, and Li-ion starts carrying the fast-response burden.
- `19:00-22:00` Full Peak Coverage: wind, Li-ion, and CAES work together to cover the evening maximum.
- `22:00-08:00` Recovery + Recharge: off-peak wind and residual solar restore storage readiness for the next cycle.

Each phase is returned as a `PhaseStep` with a description, MW allocations, and grid frequency. That structure is what drives the phase timeline in the UI.

### 5. Outcome calculations

The simulation scales with the requested `peak_demand_mw` input. The request defaults to 320 MW and is bounded between 50 and 500 MW. Internally, the simulation uses a scale factor derived from that request to adjust phase power levels, carbon avoided, diesel displacement, and cost outcomes.

The returned `outcomes` object summarizes the main results, including carbon avoided, diesel cost avoided, HRES cost, and renewable peak coverage. The report endpoint then combines the simulation with analytics, carbon, cost, and forecast data to produce a single structured operator summary.

## Testing

The backend includes an API test suite in `backend/tests/test_api.py`. The tests check that:

- The main operational endpoints respond successfully.
- The forecast reflects the expected evening peak pattern.
- Solar declines after the afternoon while wind rises into the peak window.
- The simulation returns a four-phase timeline, EMS decisions, and outcomes.
- Grid status stays within expected operating bounds.
- Storage includes both Li-ion and CAES.
- The report endpoint returns a structured operator summary.

## Tech Stack

- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS, Framer Motion, Recharts, Zustand, React Hook Form.
- Backend: FastAPI, Uvicorn, Pydantic, NumPy, Pandas, SciPy, scikit-learn, pytest, httpx.

## Overall Read

This project is a polished prototype for showing how a renewable energy management system could be visualized and reasoned about in software. It combines a cinematic frontend with a deterministic backend simulation to demonstrate the operational logic of evening peak management, grid stability, storage orchestration, and carbon reduction.