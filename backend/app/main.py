from fastapi import FastAPI
from .routes_zones import router as zones_router

app = FastAPI(title="Demand Prediction Service - PSet #1")

# Endpoint obligatorio de Health [cite: 52, 53]
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Solo incluimos tu parte
app.include_router(zones_router)