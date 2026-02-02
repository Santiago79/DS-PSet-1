import pandas as pd
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_zone():
    payload = {
        "id": 10,
        "borough": "Manhattan",
        "zone_name": "Central Park",
        "service_zone": "Yellow Zone"
    }
    response = client.post("/zones/", json=payload)
    assert response.status_code == 201
    assert response.json()["id"] == 10

def test_create_zone_duplicate():
    payload = {"id": 10, "borough": "X", "zone_name": "Y"}
    response = client.post("/zones/", json=payload)
    assert response.status_code == 400

def test_get_zone():
    response = client.get("/zones/10")
    assert response.status_code == 200
    assert response.json()["zone_name"] == "Central Park"

def test_get_zone_404():
    response = client.get("/zones/999")
    assert response.status_code == 404

def test_update_zone():
    update_payload = {"zone_name": "Central Park North"}
    response = client.put("/zones/10", json=update_payload)
    assert response.status_code == 200
    assert response.json()["zone_name"] == "Central Park North"

def test_delete_zone():
    response = client.delete("/zones/10")
    assert response.status_code == 204
    # Verificar que ya no existe
    assert client.get("/zones/10").status_code == 404

def test_list_zones_empty():
    response = client.get("/zones/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_route():
    # Crear dos zones para la ruta
    zone1 = {"id": 1, "borough": "Manhattan", "zone_name": "Zone 1"}
    zone2 = {"id": 2, "borough": "Brooklyn", "zone_name": "Zone 2"}
    client.post("/zones/", json=zone1)
    client.post("/zones/", json=zone2)
    
    # Crear ruta
    route_payload = {
        "pickup_zone_id": 1,
        "dropoff_zone_id": 2,
        "name": "Manhattan to Brooklyn"
    }
    response = client.post("/routes/", json=route_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["pickup_zone_id"] == 1
    assert data["dropoff_zone_id"] == 2
    assert data["name"] == "Manhattan to Brooklyn"
    assert "id" in data
    assert "created_at" in data

def test_create_route_same_zones():
    # Intentar crear ruta con pickup == dropoff (debe fallar)
    route_payload = {
        "pickup_zone_id": 1,
        "dropoff_zone_id": 1,
        "name": "Same Zone Route"
    }
    response = client.post("/routes/", json=route_payload)
    assert response.status_code == 400
    assert "different" in response.json()["detail"].lower()

def test_create_route_zone_not_exists():
    # Intentar crear ruta con zone que no existe
    route_payload = {
        "pickup_zone_id": 999,
        "dropoff_zone_id": 1,
        "name": "Invalid Route"
    }
    response = client.post("/routes/", json=route_payload)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]

def test_list_routes():
    response = client.get("/routes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_get_route():
    # Obtener la primera ruta creada (si existe)
    list_response = client.get("/routes/")
    routes = list_response.json()
    if routes:
        route_id = routes[0]["id"]
        response = client.get(f"/routes/{route_id}")
        assert response.status_code == 200
        assert response.json()["id"] == route_id

def test_get_route_404():
    response = client.get("/routes/99999")
    assert response.status_code == 404

def test_update_route():
    # Crear una nueva zone para actualizar
    zone3 = {"id": 3, "borough": "Queens", "zone_name": "Zone 3"}
    client.post("/zones/", json=zone3)
    
    # Obtener una ruta existente
    list_response = client.get("/routes/")
    routes = list_response.json()
    if routes:
        route_id = routes[0]["id"]
        update_payload = {
            "name": "Updated Route Name",
            "active": False
        }
        response = client.put(f"/routes/{route_id}", json=update_payload)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Route Name"
        assert response.json()["active"] == False

def test_update_route_404():
    update_payload = {"name": "Nonexistent"}
    response = client.put("/routes/99999", json=update_payload)
    assert response.status_code == 404

def test_delete_route():
    # Crear una ruta para eliminar
    route_payload = {
        "pickup_zone_id": 1,
        "dropoff_zone_id": 2,
        "name": "Route to Delete"
    }
    create_response = client.post("/routes/", json=route_payload)
    route_id = create_response.json()["id"]
    
    # Eliminar
    response = client.delete(f"/routes/{route_id}")
    assert response.status_code == 204
    
    # Verificar que ya no existe
    assert client.get(f"/routes/{route_id}").status_code == 404

#TESTS PARQUET

def test_upload_parquet_zones_full_logic():
    # PROBAR CREACIÓN
    data_new = {
        "PULocationID": [500, 501],
        "DOLocationID": [600, 601]
    }
    df_new = pd.DataFrame(data_new)
    
    buffer_new = io.BytesIO()
    df_new.to_parquet(buffer_new, engine='pyarrow')
    buffer_new.seek(0)
    
    files_new = {"file": ("new_data.parquet", buffer_new, "application/octet-stream")}
    payload_create = {"mode": "create"}

    response_new = client.post("/uploads/trips-parquet", files=files_new, data=payload_create)
    
    assert response_new.status_code == 200
    summary_new = response_new.json()
    assert summary_new["zones_created"] >= 2
    assert summary_new["rows_read"] == 2

    # PROBAR ACTUALIZACIÓN
    buffer_update = io.BytesIO()
    df_new.to_parquet(buffer_update, engine='pyarrow')
    buffer_update.seek(0)
    
    files_update = {"file": ("update_data.parquet", buffer_update, "application/octet-stream")}
    payload_update = {"mode": "update"}
    
    response_update = client.post("/uploads/trips-parquet", files=files_update, data=payload_update)
    
    assert response_update.status_code == 200
    summary_update = response_update.json()
    
    assert "zones_updated" in summary_update
    assert summary_update["zones_updated"] >= 2

    print(f"\nResumen de creación: {response_new.json()}")
    print(f"\nResumen de actualización: {response_update.json()}")
