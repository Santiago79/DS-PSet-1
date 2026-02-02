# backend/app/routes_uploads.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
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
    """
    Procesa archivo parquet de viajes NYC TLC.
    Crea/actualiza Zones y Routes usando la misma lógica CRUD que los endpoints.
    """
    
   
    # 1. VALIDACIONES INICIALES
   
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
        # 2. LEER Y PREPROCESAR DATAFRAME
        contents = await file.read()
        df = pd.read_parquet(io.BytesIO(contents))
        
        # Aplicar límite de filas para evitar OOM
        if limit_rows and len(df) > limit_rows:
            df = df.head(limit_rows)
        
        rows_read = len(df)
        
        
        # 3. VALIDAR COLUMNAS REQUERIDAS
        required_columns = ['PULocationID', 'DOLocationID']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # 4. LIMPIAR Y CONVERTIR DATOS
        # Convertir a numérico y manejar valores nulos
        df['PULocationID'] = pd.to_numeric(df['PULocationID'], errors='coerce').fillna(0).astype(int)
        df['DOLocationID'] = pd.to_numeric(df['DOLocationID'], errors='coerce').fillna(0).astype(int)
        
        # Filtrar IDs inválidos (<= 0)
        df = df[(df['PULocationID'] > 0) & (df['DOLocationID'] > 0)]
        
        if len(df) == 0:
            raise HTTPException(
                status_code=400,
                detail="No valid rows found after cleaning data"
            )
        
        # 5. INICIALIZAR CONTADORES Y ERRORES
        zones_created = 0
        zones_updated = 0
        routes_created = 0
        routes_updated = 0
        errors: List[str] = []
        
        # Usar contador global compartido con routes_routes.py
        global route_id_counter
        
        
        # 6. PROCESAR ZONAS (Zones CRUD logic)
        
        # Obtener todas las zonas únicas del dataset
        pickup_zones = set(df['PULocationID'].unique())
        dropoff_zones = set(df['DOLocationID'].unique())
        all_zone_ids = pickup_zones.union(dropoff_zones)
        
        for zone_id in all_zone_ids:
            try:
                # Verificar si la zona existe en zones_db
                if zone_id in zones_db:
                    # ZONA EXISTE: Actualizar (marcar como activa)
                    # Simula PUT /zones/{id} con active=True
                    zones_db[zone_id]["active"] = True
                    zones_updated += 1
                    
                else:
                    # ZONA NO EXISTE: Crear placeholder
                    # Simula POST /zones con campos mínimos default
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
        
        # 7. PROCESAR RUTAS (Routes CRUD logic)
        
        # 7.1 Obtener pares (PULocationID, DOLocationID) y su conteo
        route_counts = df.groupby(['PULocationID', 'DOLocationID']).size().reset_index(name='count')
        
        # 7.2 Filtrar rutas inválidas (pickup == dropoff)
        route_counts = route_counts[route_counts['PULocationID'] != route_counts['DOLocationID']]
        
        # 7.3 Ordenar por frecuencia y tomar top N
        route_counts = route_counts.sort_values('count', ascending=False)
        routes_detected = len(route_counts)
        top_routes = route_counts.head(top_n_routes)
        
        # 7.4 Procesar cada ruta top
        for _, row in top_routes.iterrows():
            pickup_id = int(row['PULocationID'])
            dropoff_id = int(row['DOLocationID'])
            
            try:
                # Validar que ambas zonas existen (deberían, después del paso 6)
                if pickup_id not in zones_db:
                    errors.append(f"Pickup zone {pickup_id} does not exist in zones_db")
                    continue
                if dropoff_id not in zones_db:
                    errors.append(f"Dropoff zone {dropoff_id} does not exist in zones_db")
                    continue
                
                # 7.5 Buscar existencia de ruta (GET /routes?pickup_zone_id=...&dropoff_zone_id=...)
                existing_route_id = None
                for route_id, route in routes_db.items():
                    if (route['pickup_zone_id'] == pickup_id and 
                        route['dropoff_zone_id'] == dropoff_id):
                        existing_route_id = route_id
                        break
                
                if existing_route_id is not None:
                    # RUTA EXISTE
                    if mode == "update":
                        # Actualizar ruta existente (PUT /routes/{id})
                        # Marcar como activa y/o actualizar nombre
                        routes_db[existing_route_id]["active"] = True
                        routes_updated += 1
                
                else:
                    # RUTA NO EXISTE
                    if mode in ["create", "update"]:
                        # Validar pickup != dropoff (por seguridad)
                        if pickup_id == dropoff_id:
                            errors.append(f"Pickup and dropoff are the same: {pickup_id}")
                            continue
                        
                        # Crear nueva ruta (POST /routes)
                        # Usar el MISMO formato que routes_routes.py
                        new_route = {
                            "id": route_id_counter,  # ID numérico autoincremental
                            "pickup_zone_id": pickup_id,
                            "dropoff_zone_id": dropoff_id,
                            "name": f"Route {pickup_id} to {dropoff_id}",
                            "active": True,
                            "created_at": datetime.now()
                        }
                        
                        # Guardar en routes_db con ID numérico
                        routes_db[route_id_counter] = new_route
                        route_id_counter += 1  # Incrementar para próxima ruta
                        routes_created += 1
                        
            except Exception as e:
                errors.append(f"Error processing route {pickup_id}->{dropoff_id}: {str(e)}")
        
        # 8. RETORNAR RESULTADO
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
        # Capturar cualquier otro error
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )