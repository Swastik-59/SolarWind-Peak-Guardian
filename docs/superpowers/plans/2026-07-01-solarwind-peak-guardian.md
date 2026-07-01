# SolarWind Peak Guardian Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete immersive mission-control prototype from the Team Kaisen presentation.

**Architecture:** Next.js 15 App Router renders a single cinematic, sectioned experience backed by a modular FastAPI service. Mock AI services produce realistic renewable, storage, grid, carbon, cost, and simulation telemetry, with WebSocket updates powering the live control room.

**Tech Stack:** Next.js 15, TypeScript, Tailwind CSS, Framer Motion, Lenis, Recharts, Zustand, React Hook Form, Lucide Icons, FastAPI, Pydantic, async APIs, WebSocket.

## Global Constraints

- The PowerPoint is the single source of truth.
- Every slide concept must appear in the app: problem, duck curve, challenges, solution, renewables, architecture, phases, use cases, justification, advantages, disadvantages, mitigations, and conclusion.
- The UI must feel like a futuristic national-grid mission control center, not a CRUD dashboard, SaaS admin panel, or generic AI site.
- Motion must be intentional: page transitions, energy particles, counters, grid pulses, battery/CAES activity, wind rotation, and day-to-night changes.
- Backend endpoints required: `/forecast`, `/simulate`, `/weather`, `/grid/status`, `/grid`, `/battery`, `/storage`, `/renewables`, `/carbon`, `/cost`, `/analytics`, `/telemetry`.

---

### Task 1: Backend Domain And API

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/models.py`
- Create: `backend/app/services.py`
- Create: `backend/app/api.py`
- Create: `backend/app/__init__.py`
- Create: `backend/tests/test_api.py`

**Interfaces:**
- Produces async FastAPI app `app.main:app`.
- Produces deterministic service functions: `get_forecast`, `get_weather`, `get_grid_status`, `get_battery`, `get_storage`, `get_renewables`, `get_carbon`, `get_cost`, `get_analytics`, `run_simulation`, `next_telemetry`.

- [x] Write API tests that assert all required endpoints exist and return realistic typed data.
- [x] Verify the tests fail before implementation.
- [x] Implement Pydantic models, mock AI services, routes, CORS, and WebSocket.
- [x] Run backend tests until passing.

### Task 2: Frontend Scaffold And Data Layer

**Files:**
- Create: `package.json`
- Create: `next.config.ts`
- Create: `tsconfig.json`
- Create: `postcss.config.mjs`
- Create: `tailwind.config.ts`
- Create: `app/layout.tsx`
- Create: `app/page.tsx`
- Create: `app/globals.css`
- Create: `lib/types.ts`
- Create: `lib/api.ts`
- Create: `lib/content.ts`
- Create: `store/mission-store.ts`
- Create: `components/lenis-provider.tsx`

**Interfaces:**
- Produces typed API client functions and a Zustand mission state used by all sections.

- [x] Scaffold Next.js App Router with typed Tailwind setup.
- [x] Add deck-derived content constants covering every slide.
- [x] Add typed REST and WebSocket data hooks/state.
- [x] Run TypeScript build checks.

### Task 3: Mission Experience Components

**Files:**
- Create components under `components/mission/*`.

**Interfaces:**
- Consumes backend types and content constants.
- Produces the landing, problem, mission control, digital twin, storage, forecast, simulator, analytics, carbon, cost, use case, architecture, report, and settings sections.

- [x] Build unique editorial compositions for each required module.
- [x] Add SVG energy paths, animated particles, turbines, storage gauges, day-night transitions, and chart animations.
- [x] Make the Run Evening Peak Simulation action orchestrate UI state across sections.
- [x] Ensure mobile layouts remain readable and controls are accessible.

### Task 4: Verification

**Files:**
- Modify app/backend files only as needed for fixes.

- [x] Run backend tests.
- [x] Run `npm run build`.
- [x] Start dev server.
- [ ] Verify the app in browser at desktop and mobile viewports.
