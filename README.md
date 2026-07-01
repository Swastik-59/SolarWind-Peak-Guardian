# SolarWind Peak Guardian

AI-Powered Hybrid Renewable System for Fossil-Free Evening Peak Management.

## Run

Start the backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the frontend:

```powershell
npm run dev -- -p 3000
```

Open `http://localhost:3000`.

## Verify

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests\test_api.py -q
npm run build
```

## Prototype Coverage

The app turns the presentation into three acts: problem visualization with Duck Curve and grid challenges, AI EMS mission control with animated Solar/Wind/Li-Ion/CAES/Grid energy flow, and results modules for carbon, cost, use cases, reports, settings, mitigations, and roadmap.
