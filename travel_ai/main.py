from fastapi import FastAPI
from travel_ai.routes.planner import router as planner_router

app = FastAPI(title="Travel AI Multi-Agent Planner")

app.include_router(planner_router)

@app.get("/")
def root():
    return {"status": "Travel AI backend running"}