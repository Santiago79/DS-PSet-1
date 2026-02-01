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