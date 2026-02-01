from fastapi import FastAPI

from .routes_zones import router as zones_router
from .routes_routes import router as routes_router
from .routes_uploads import router as uploads_router

app = FastAPI(title="Demand Prediction Service - PSet #1")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(zones_router)
app.include_router(routes_router)
app.include_router(uploads_router)