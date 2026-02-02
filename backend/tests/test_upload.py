from fastapi.testclient import TestClient
import pandas as pd
import io
from app.main import app
from app.storage import zones_db, routes_db

client = TestClient(app)

def create_test_parquet():
    """Crea un archivo parquet de prueba en memoria"""
    data = {
        'PULocationID': [1, 1, 2, 2, 3, 1, 2, 3, 3, 1],
        'DOLocationID': [2, 2, 3, 3, 1, 2, 3, 1, 2, 3],
        'trip_distance': [1.5, 2.0, 3.5, 1.0, 2.5, 1.8, 3.0, 2.2, 1.5, 2.8]
    }
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    return buffer

def test_upload_parquet_create():
    """Test upload parquet con modo create"""
    # Limpiar storage
    zones_db.clear()
    routes_db.clear()
    
    parquet_buffer = create_test_parquet()
    
    response = client.post(
        "/uploads/trips-parquet",
        files={"file": ("test.parquet", parquet_buffer, "application/octet-stream")},
        data={"mode": "create", "limit_rows": 100, "top_n_routes": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["file_name"] == "test.parquet"
    assert data["rows_read"] == 10
    assert data["zones_created"] > 0
    assert data["routes_created"] > 0
    assert isinstance(data["errors"], list)

def test_upload_parquet_update():
    """Test upload parquet con modo update"""
    parquet_buffer = create_test_parquet()
    
    # Primero crear algunas zones
    zones_db[1] = {
        "id": 1,
        "borough": "Manhattan",
        "zone_name": "Zone 1",
        "service_zone": "Yellow",
        "active": False,
        "created_at": "2024-01-01T00:00:00"
    }
    
    response = client.post(
        "/uploads/trips-parquet",
        files={"file": ("test.parquet", parquet_buffer, "application/octet-stream")},
        data={"mode": "update"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["zones_updated"] >= 1

def test_upload_invalid_mode():
    """Test con modo inválido"""
    parquet_buffer = create_test_parquet()
    
    response = client.post(
        "/uploads/trips-parquet",
        files={"file": ("test.parquet", parquet_buffer, "application/octet-stream")},
        data={"mode": "invalid_mode"}
    )
    
    assert response.status_code == 400
    assert "mode must be" in response.json()["detail"]

def test_upload_non_parquet_file():
    """Test con archivo no parquet"""
    text_content = b"This is not a parquet file"
    
    response = client.post(
        "/uploads/trips-parquet",
        files={"file": ("test.txt", io.BytesIO(text_content), "text/plain")},
        data={"mode": "create"}
    )
    
    assert response.status_code == 400
    assert "parquet" in response.json()["detail"].lower()

def test_upload_missing_columns():
    """Test con parquet sin columnas requeridas"""
    data = {
        'column1': [1, 2, 3],
        'column2': [4, 5, 6]
    }
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    
    response = client.post(
        "/uploads/trips-parquet",
        files={"file": ("test.parquet", buffer, "application/octet-stream")},
        data={"mode": "create"}
    )
    
    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]

def test_upload_filters_invalid_routes():
    """Test que filtra rutas con pickup == dropoff"""
    data = {
        'PULocationID': [1, 2, 3, 1, 1],
        'DOLocationID': [1, 2, 3, 2, 1]  # Las filas 0, 1, 2, 4 tienen pickup == dropoff
    }
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    
    zones_db.clear()
    routes_db.clear()
    
    response = client.post(
        "/uploads/trips-parquet",
        files={"file": ("test.parquet", buffer, "application/octet-stream")},
        data={"mode": "create"}
    )
    
    assert response.status_code == 200
    data = response.json()
    # Solo debe detectar la ruta 1->2 (las rutas con pickup == dropoff se filtran)
    assert data["routes_detected"] == 1
