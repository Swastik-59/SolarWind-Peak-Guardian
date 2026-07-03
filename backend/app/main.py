from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .api import router

app = FastAPI(
    title="SolarWind Peak Guardian API",
    description="Physics-informed AI EMS for fossil-free evening peak management.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "name": "SolarWind Peak Guardian",
        "version": "1.0.0",
        "status": "mission-ready",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
