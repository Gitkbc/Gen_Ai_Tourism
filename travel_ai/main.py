from fastapi import FastAPI
from travel_ai.routes.planner import router as planner_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
app = FastAPI(title="Travel AI Multi-Agent Planner")

app.include_router(planner_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache_root = Path(__file__).resolve().parent / "cache"
cache_root.mkdir(parents=True, exist_ok=True)
app.mount("/cache", StaticFiles(directory=str(cache_root)), name="cache")

@app.get("/")
def root():
    return {"status": "Travel AI backend running"}
