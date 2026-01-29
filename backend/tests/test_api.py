import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# --- TESTS DE HEALTH (1) ---
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# --- TESTS DE ZONES ---
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
    assert response.status_code == 400 # Error por ID duplicado

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

# --- TEST DE RELLENO PARA COMPLETAR 8 (esto es para la persona 2) ---
def test_list_zones_empty():
    response = client.get("/zones/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)