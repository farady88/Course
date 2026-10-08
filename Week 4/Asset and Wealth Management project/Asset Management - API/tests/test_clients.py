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
    assert "client_id" in data
    client_id = data["client_id"]
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
    client_id = data["client_id"]

    # Verify client was added
    assert client_id in CLIENTS
    assert len(CLIENTS) == initial_count + 1

    # Test deleting the client
    response = client.delete(f"/clients/{client_id}")
    assert response.status_code == 200
    data = response.json()

    # Check that we got the deleted client back
    assert data["client_id"] == client_id
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

ESG_ORDER = {"A": 4, "B": 3, "C": 2, "D": 1}


def breached_rules(client_id, fund_id):
    """Apply the five mandate rules to API data and return the names of those breached.

    A value equal to a limit is compliant, a rule set to None is skipped,
    and an unrated fund fails any ESG minimum.
    """
    c = client.get(f"/clients/{client_id}").json()
    fund = client.get(f"/funds/{fund_id}").json()
    breaches = set()
    if set(c["excluded_sectors"] or []) & {h["sector"] for h in fund["holdings"]}:
        breaches.add("excluded_sector")
    if fund["risk_rating"] > c["risk_tolerance"]:
        breaches.add("risk")
    if any(h["weight_pct"] > c["max_single_holding_pct"] for h in fund["holdings"]):
        breaches.add("concentration")
    if c["min_esg_rating"] is not None:
        if ESG_ORDER.get(fund["esg_rating"], 0) < ESG_ORDER[c["min_esg_rating"]]:
            breaches.add("esg")
    if c["max_ongoing_charge_pct"] is not None:
        if fund["ongoing_charge_pct"] > c["max_ongoing_charge_pct"]:
            breaches.add("fee")
    return breaches


def test_clean_pairing():
    """Fund 3 breaks none of Client 3's rules"""
    assert breached_rules(3, 3) == set()


def test_pairing_breaking_every_rule():
    """Fund 2 breaks all five of Client 3's rules"""
    assert breached_rules(3, 2) == {"excluded_sector", "risk", "concentration", "esg", "fee"}


def test_excluded_sector_reports_weights():
    """Client 3 excludes tobacco and fossil fuels, which Fund 2 holds at 3.0% and 4.8%"""
    excluded = client.get("/clients/3").json()["excluded_sectors"]
    holdings = client.get("/funds/2").json()["holdings"]
    found = {h["sector"]: h["weight_pct"] for h in holdings if h["sector"] in excluded}
    assert found == {"tobacco": 3.0, "fossil_fuels": 4.8}


def test_concentration_breach():
    """Fund 4's 12% holding breaches Client 2's 5% limit and nothing else"""
    assert breached_rules(2, 4) == {"concentration"}


def test_boundary_values_are_compliant():
    """Fund 5 equals Client 5's limits on risk, fee and top holding, so nothing is breached"""
    assert breached_rules(5, 5) == set()


def test_unrated_fund_fails_esg_minimum():
    """Fund 6 is unrated, so it fails Client 3's ESG minimum along with risk, concentration and fee"""
    assert breached_rules(3, 6) == {"risk", "concentration", "esg", "fee"}


def test_rules_set_to_none_are_skipped():
    """Client 4 has no ESG minimum and no fee ceiling, so Fund 6 breaks nothing"""
    client_4 = client.get("/clients/4").json()
    assert client_4["min_esg_rating"] is None
    assert client_4["max_ongoing_charge_pct"] is None
    assert breached_rules(4, 6) == set()


def test_highest_risk_fund():
    """Fund 7 is above Client 4's risk tolerance and holds gambling, which Client 4 excludes"""
    assert breached_rules(4, 7) == {"excluded_sector", "risk", "concentration"}
