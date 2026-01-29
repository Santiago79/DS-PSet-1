from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .schemas import ZoneCreate, ZoneUpdate, ZoneResponse
from .storage import zones_db

router = APIRouter(prefix="/zones", tags=["Zones"])

# POST /zones: Crear una zona [cite: 55]
@router.post("/", response_model=ZoneResponse, status_code=201)
async def create_zone(zone: ZoneCreate):
    if zone.id in zones_db:
        # Error 400 por regla de negocio (ID duplicado) [cite: 77]
        raise HTTPException(status_code=400, detail="Zone ID already exists")
    
    from datetime import datetime
    new_zone = zone.model_dump()
    new_zone["created_at"] = datetime.now()
    zones_db[zone.id] = new_zone
    return new_zone

# GET /zones: Listar con filtros opcionales [cite: 57]
@router.get("/", response_model=List[ZoneResponse])
async def list_zones(
    active: Optional[bool] = None, 
    borough: Optional[str] = None
):
    results = list(zones_db.values())
    if active is not None:
        results = [z for z in results if z["active"] == active]
    if borough:
        results = [z for z in results if borough.lower() in z["borough"].lower()]
    return results

# GET /zones/{id}: Obtener una sola zona [cite: 58]
@router.get("/{id}", response_model=ZoneResponse)
async def get_zone(id: int):
    if id not in zones_db:
        raise HTTPException(status_code=404, detail="Zone not found") [cite: 78]
    return zones_db[id]

# PUT /zones/{id}: Actualizar zona [cite: 59]
@router.put("/{id}", response_model=ZoneResponse)
async def update_zone(id: int, zone_update: ZoneUpdate):
    if id not in zones_db:
        raise HTTPException(status_code=404, detail="Zone not found") [cite: 78]
    
    stored_zone = zones_db[id]
    update_data = zone_update.model_dump(exclude_unset=True)
    stored_zone.update(update_data)
    return stored_zone

# DELETE /zones/{id}: Eliminar zona [cite: 60]
@router.delete("/{id}", status_code=204)
async def delete_zone(id: int):
    if id not in zones_db:
        raise HTTPException(status_code=404, detail="Zone not found") [cite: 78]
    del zones_db[id]
    return None # Retorna 204 No Content [cite: 60]