import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#This code adds the project's "API" folder to Python's search path so the test file can find and import:
#main.py (which contains the FastAPI app)
#Data/records.py (which contains the CLIENTS data)
from fastapi.testclient import TestClient
from main import app
from Data.records import CLIENTS

client = TestClient(app)

def test_list_clients():
    """Test listing all clients"""
    response = client.get("/clients")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(CLIENTS)
    # Check that we get all the expected clients
    client_ids = [c["client_id"] for c in data]
    assert set(client_ids) == set(CLIENTS.keys())

def test_get_client():
    """Test getting a specific client"""
    # Test getting an existing client
    response = client.get("/clients/1")
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == 1
    assert data["client_name"] == "Harrington Family Trust"

    # Test getting a non-existent client
    response = client.get("/clients/999")
    assert response.status_code == 404
    assert "No client with id 999" in response.json()["detail"]

def test_add_client():
    """Test adding a new client"""
    # Store initial count
    initial_count = len(CLIENTS)

    # Test adding a new client with all fields
    new_client_data = {
        "client_name": "Test Client",
        "risk_tolerance": 4,
        "excluded_sectors": ["tobacco"],
        "max_single_holding_pct": 5.0,
        "min_esg_rating": "B",
        "max_ongoing_charge_pct": 1.0,
        "notes": "Test notes"
    }

    response = client.post("/clients", json=new_client_data)
    assert response.status_code == 200
    data = response.json()

    # Check that the client was created with an auto-generated ID
    assert "id" in data
    client_id = data["id"]
    assert client_id > 0

    # Check that all fields were set correctly
    assert data["client_name"] == "Test Client"
    assert data["risk_tolerance"] == 4
    assert data["excluded_sectors"] == ["tobacco"]
    assert data["max_single_holding_pct"] == 5.0
    assert data["min_esg_rating"] == "B"
    assert data["max_ongoing_charge_pct"] == 1.0
    assert data["notes"] == "Test notes"

    # Verify the client was actually added to CLIENTS
    assert client_id in CLIENTS
    assert CLIENTS[client_id]["client_name"] == "Test Client"

    # Test adding a client with empty fields (should be None)
    new_client_data_empty = {
        "client_name": "Test Client 2",
        "risk_tolerance": None,
        "excluded_sectors": None,
        "max_single_holding_pct": None,
        "min_esg_rating": None,
        "max_ongoing_charge_pct": None,
        "notes": None
    }

    response = client.post("/clients", json=new_client_data_empty)
    assert response.status_code == 200
    data = response.json()
    client_id_2 = data["id"]

    # Check that None values are preserved
    assert data["client_name"] == "Test Client 2"
    assert data["risk_tolerance"] is None
    assert data["excluded_sectors"] is None
    assert data["max_single_holding_pct"] is None
    assert data["min_esg_rating"] is None
    assert data["max_ongoing_charge_pct"] is None
    assert data["notes"] is None

    # Verify client count increased by 2
    assert len(CLIENTS) == initial_count + 2

def test_update_client():
    """Test updating an existing client"""
    # Store original values for client 1
    original_client = CLIENTS[1].copy()

    # Test updating some fields
    update_data = {
        "client_name": "Updated Name",
        "risk_tolerance": 3,
        "notes": "Updated notes"
    }

    response = client.put("/clients/1", json=update_data)
    assert response.status_code == 200
    data = response.json()

    # Check that the updated fields are correct
    assert data["client_name"] == "Updated Name"
    assert data["risk_tolerance"] == 3
    assert data["notes"] == "Updated notes"

    # Check that unchanged fields remain the same
    assert data["excluded_sectors"] == original_client["excluded_sectors"]
    assert data["max_single_holding_pct"] == original_client["max_single_holding_pct"]
    assert data["min_esg_rating"] == original_client["min_esg_rating"]
    assert data["max_ongoing_charge_pct"] == original_client["max_ongoing_charge_pct"]

    # Verify the changes were persisted in CLIENTS
    assert CLIENTS[1]["client_name"] == "Updated Name"
    assert CLIENTS[1]["risk_tolerance"] == 3
    assert CLIENTS[1]["notes"] == "Updated notes"
    assert CLIENTS[1]["excluded_sectors"] == original_client["excluded_sectors"]  # unchanged

    # Test updating with empty fields (should not change existing values)
    update_data_empty = {
        "client_name": None,
        "risk_tolerance": None,
        "excluded_sectors": None,
        "max_single_holding_pct": None,
        "min_esg_rating": None,
        "max_ongoing_charge_pct": None,
        "notes": None
    }

    # Store values before update with None
    before_update = CLIENTS[1].copy()

    response = client.put("/clients/1", json=update_data_empty)
    assert response.status_code == 200
    data = response.json()

    # All values should remain unchanged
    assert data["client_name"] == before_update["client_name"]
    assert data["risk_tolerance"] == before_update["risk_tolerance"]
    assert data["excluded_sectors"] == before_update["excluded_sectors"]
    assert data["max_single_holding_pct"] == before_update["max_single_holding_pct"]
    assert data["min_esg_rating"] == before_update["min_esg_rating"]
    assert data["max_ongoing_charge_pct"] == before_update["max_ongoing_charge_pct"]
    assert data["notes"] == before_update["notes"]

    # Test updating a non-existent client
    response = client.put("/clients/999", json=update_data)
    assert response.status_code == 404
    assert "No client with id 999" in response.json()["detail"]

def test_delete_client():
    """Test deleting a client"""
    # Store initial count
    initial_count = len(CLIENTS)

    # Add a client to delete
    new_client_data = {
        "client_name": "Client to Delete",
        "risk_tolerance": 5,
        "excluded_sectors": [],
        "max_single_holding_pct": 10.0,
        "min_esg_rating": "A",
        "max_ongoing_charge_pct": 2.0,
        "notes": "This client will be deleted"
    }

    response = client.post("/clients", json=new_client_data)
    assert response.status_code == 200
    data = response.json()
    client_id = data["id"]

    # Verify client was added
    assert client_id in CLIENTS
    assert len(CLIENTS) == initial_count + 1

    # Test deleting the client
    response = client.delete(f"/clients/{client_id}")
    assert response.status_code == 200
    data = response.json()

    # Check that we got the deleted client back
    assert data["id"] == client_id
    assert data["client_name"] == "Client to Delete"

    # Verify client was removed from CLIENTS
    assert client_id not in CLIENTS
    assert len(CLIENTS) == initial_count

    # Test deleting a non-existent client
    response = client.delete("/clients/999")
    assert response.status_code == 404
    assert "No client with id 999" in response.json()["detail"]

def test_sector_validation():
    """Test that sector validation works correctly"""
    # Test adding a client with invalid sector
    invalid_client_data = {
        "client_name": "Invalid Sector Client",
        "risk_tolerance": 5,
        "excluded_sectors": ["invalid_sector"],
        "max_single_holding_pct": 5.0,
        "min_esg_rating": "B",
        "max_ongoing_charge_pct": 1.0,
        "notes": "Test"
    }

    response = client.post("/clients", json=invalid_client_data)
    assert response.status_code == 422  # Validation error

    # Test updating a client with invalid sector
    invalid_update_data = {
        "excluded_sectors": ["another_invalid_sector"]
    }

    response = client.put("/clients/1", json=invalid_update_data)
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    test_list_clients()
    test_get_client()
    test_add_client()
    test_update_client()
    test_delete_client()
    test_sector_validation()
    print("All tests passed!")