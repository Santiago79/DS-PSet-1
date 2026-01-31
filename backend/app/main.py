from fastapi import FastAPI
from .routes_zones import router as zones_router

app = FastAPI(title="Demand Prediction Service - PSet #1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Solo está mi parte (persona1)
app.include_router(zones_router)