from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from .schemas import RouteCreate, RouteUpdate, RouteResponse
from .storage import routes_db, route_id_counter, zones_db

router = APIRouter(prefix="/routes", tags=["Routes"])

@router.post("/", response_model=RouteResponse, status_code=201)
def create_route(route: RouteCreate):
    # Validar que pickup_zone_id != dropoff_zone_id
    if route.pickup_zone_id == route.dropoff_zone_id:
        raise HTTPException(
            status_code=400, 
            detail="pickup_zone_id and dropoff_zone_id must be different"
        )
    
    # Validar que ambas zones existan
    if route.pickup_zone_id not in zones_db:
        raise HTTPException(
            status_code=400,
            detail=f"Zone with id {route.pickup_zone_id} does not exist"
        )
    if route.dropoff_zone_id not in zones_db:
        raise HTTPException(
            status_code=400,
            detail=f"Zone with id {route.dropoff_zone_id} does not exist"
        )
    
    # Generar ID y crear ruta
    global route_id_counter
    route_id = route_id_counter
    route_id_counter += 1
    
    new_route = route.model_dump()
    new_route["id"] = route_id
    new_route["created_at"] = datetime.now()
    
    routes_db[route_id] = new_route
    return new_route

@router.get("/", response_model=List[RouteResponse])
def list_routes(
    active: Optional[bool] = None,
    pickup_zone_id: Optional[int] = None,
    dropoff_zone_id: Optional[int] = None
):
    results = list(routes_db.values())
    
    if active is not None:
        results = [r for r in results if r["active"] == active]
    if pickup_zone_id is not None:
        results = [r for r in results if r["pickup_zone_id"] == pickup_zone_id]
    if dropoff_zone_id is not None:
        results = [r for r in results if r["dropoff_zone_id"] == dropoff_zone_id]
    
    return results

@router.get("/{id}", response_model=RouteResponse)
def get_route(id: int):
    if id not in routes_db:
        raise HTTPException(status_code=404, detail="Route not found")
    return routes_db[id]

@router.put("/{id}", response_model=RouteResponse)
def update_route(id: int, route_update: RouteUpdate):
    if id not in routes_db:
        raise HTTPException(status_code=404, detail="Route not found")
    
    current_route = routes_db[id]
    update_data = route_update.model_dump(exclude_unset=True)
    
    # Si se actualizan los zone_ids, validar
    new_pickup = update_data.get("pickup_zone_id", current_route["pickup_zone_id"])
    new_dropoff = update_data.get("dropoff_zone_id", current_route["dropoff_zone_id"])
    
    if new_pickup == new_dropoff:
        raise HTTPException(
            status_code=400,
            detail="pickup_zone_id and dropoff_zone_id must be different"
        )
    
    # Validar existencia de zones si se actualizan
    if "pickup_zone_id" in update_data and new_pickup not in zones_db:
        raise HTTPException(
            status_code=400,
            detail=f"Zone with id {new_pickup} does not exist"
        )
    if "dropoff_zone_id" in update_data and new_dropoff not in zones_db:
        raise HTTPException(
            status_code=400,
            detail=f"Zone with id {new_dropoff} does not exist"
        )
    
    # Aplicar actualizaciones
    for key, value in update_data.items():
        current_route[key] = value
    
    return current_route

@router.delete("/{id}", status_code=204)
def delete_route(id: int):
    if id not in routes_db:
        raise HTTPException(status_code=404, detail="Route not found")
    del routes_db[id]
