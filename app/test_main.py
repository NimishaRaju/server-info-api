import pytest
from fastapi.testclient import TestClient

# 1. Cleanly import the app and the factory function directly
from main import app 
from dependencies import get_server_service
from services import ServerService
client=TestClient(app)

@pytest.fixture(autouse=True)
def use_test_json_file(tmp_path):
    """Safely overrides your factory function to point to a real, isolated temporary file."""
    test_file_path = str(tmp_path / "test_database.json")
    
    # Instantiate a clean, genuine instance with our temporary path
    real_test_service = ServerService(file_path=test_file_path)
    
    # We override BOTH the class reference and the function to trick FastAPI's type validator
    app.dependency_overrides[ServerService] = lambda: real_test_service
    app.dependency_overrides[get_server_service] = lambda: real_test_service
    
    yield
    app.dependency_overrides.clear()


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_get_all_servers():
    response = client.get("/api/servers")
    assert response.status_code == 200
    # response.json() will be a list here. 
    # We assert that it successfully returns a list type.
    assert isinstance(response.json(), list)

def test_get_server_by_id():
    response = client.get("/api/servers/not-an-id-present")
    assert response.status_code == 404
    assert response.json()["detail"] == "Server with ID 'not-an-id-present' not found."

def test_create_server():
    """Test creating a new server by sending JSON data"""
    # Define the data payload you want to send
    payload = {"server_name": "My New Test Server"}
    
    # Make the POST request with the json payload
    response = client.post("/api/servers", json=payload)
    
    # Check the results
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert "server_id" in response.json()  # Verifies an ID was generated


def test_update_server_not_found():
    """Test updating a fake server returns a 404"""
    # Send metric changes to a server ID that doesn't exist
    payload = {
        "metrics": {
            "cpu_health": {
                "utilization_percentage": 45.5
            },
            "memory_health": {
                "used_gb": 60.2
            }
        }
    }
    
    response = client.patch("/api/servers/not-an-id-present", json=payload)
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_server_not_found():
    """Test deleting a fake server returns a 404"""
    response = client.delete("/api/servers/delete/not-an-id-present")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
