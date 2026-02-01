from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import pandas as pd
import io
from datetime import datetime

from .schemas import TripsParquetUploadResult
from .storage import zones_db, routes_db, route_id_counter

router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.post("/trips-parquet", response_model=TripsParquetUploadResult)
async def upload_trips_parquet(
    file: UploadFile = File(...),
    mode: str = Form(...),
    limit_rows: Optional[int] = Form(50_000),
    top_n_routes: Optional[int] = Form(50)
):
    if mode not in ["create", "update"]:
        raise HTTPException(
            status_code=400,
            detail="mode must be 'create' or 'update'"
        )
    
    if not file.filename.endswith('.parquet'):
        raise HTTPException(
            status_code=400,
            detail="File must be a .parquet file"
        )
    
    try:
        contents = await file.read()
        df = pd.read_parquet(io.BytesIO(contents))
        
        if limit_rows and len(df) > limit_rows:
            df = df.head(limit_rows)
        
        rows_read = len(df)
        
        required_columns = ['PULocationID', 'DOLocationID']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        zones_created = 0
        zones_updated = 0
        routes_created = 0
        routes_updated = 0
        errors = []
        
        # Extraer todos los zone IDs únicos del parquet
        pickup_zones = set(df['PULocationID'].dropna().astype(int).unique())
        dropoff_zones = set(df['DOLocationID'].dropna().astype(int).unique())
        all_zone_ids = pickup_zones.union(dropoff_zones)
        
        for zone_id in all_zone_ids:
            try:
                if zone_id in zones_db:
                    zones_db[zone_id]["active"] = True
                    zones_updated += 1
                else:
                    new_zone = {
                        "id": zone_id,
                        "borough": "Unknown",
                        "zone_name": f"Zone {zone_id}",
                        "service_zone": "Unknown",
                        "active": True,
                        "created_at": datetime.now()
                    }
                    zones_db[zone_id] = new_zone
                    zones_created += 1
            except Exception as e:
                errors.append(f"Error processing zone {zone_id}: {str(e)}")
        
        # Contar frecuencia de cada par (pickup, dropoff)
        route_counts = df.groupby(['PULocationID', 'DOLocationID']).size().reset_index(name='count')
        route_counts = route_counts.sort_values('count', ascending=False)
        
        # Filtrar rutas inválidas (pickup == dropoff)
        route_counts = route_counts[route_counts['PULocationID'] != route_counts['DOLocationID']]
        
        routes_detected = len(route_counts)
        top_routes = route_counts.head(top_n_routes)
        
        global route_id_counter
        
        for _, row in top_routes.iterrows():
            pickup_id = int(row['PULocationID'])
            dropoff_id = int(row['DOLocationID'])
            
            try:
                # Buscar si ya existe una ruta con este par pickup-dropoff
                existing_route = None
                for route_id, route in routes_db.items():
                    if (route['pickup_zone_id'] == pickup_id and 
                        route['dropoff_zone_id'] == dropoff_id):
                        existing_route = route_id
                        break
                
                if existing_route:
                    if mode == "update":
                        routes_db[existing_route]["active"] = True
                        routes_updated += 1
                else:
                    if mode == "create" or mode == "update":
                        route_name = f"Route {pickup_id} to {dropoff_id}"
                        new_route = {
                            "id": route_id_counter,
                            "pickup_zone_id": pickup_id,
                            "dropoff_zone_id": dropoff_id,
                            "name": route_name,
                            "active": True,
                            "created_at": datetime.now()
                        }
                        routes_db[route_id_counter] = new_route
                        route_id_counter += 1
                        routes_created += 1
                        
            except Exception as e:
                errors.append(f"Error processing route {pickup_id}->{dropoff_id}: {str(e)}")
        
        return TripsParquetUploadResult(
            file_name=file.filename,
            rows_read=rows_read,
            zones_created=zones_created,
            zones_updated=zones_updated,
            routes_detected=routes_detected,
            routes_created=routes_created,
            routes_updated=routes_updated,
            errors=errors
        )
        
    except pd.errors.ParserError:
        raise HTTPException(
            status_code=400,
            detail="Invalid parquet file format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )
