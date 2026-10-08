import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#This code adds the project's "API" folder to Python's search path so the test file can find and import:
#main.py (which contains the FastAPI app)
#Data/records.py (which contains the PORTFOLIOS and FUNDS data)
import pytest
from fastapi.testclient import TestClient
from main import app
from Data.records import PORTFOLIOS, FUNDS

client = TestClient(app)


def test_list_portfolios():
    """Test listing all portfolios"""
    response = client.get("/portfolios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(PORTFOLIOS)
    # Check that we get all the expected portfolios
    portfolio_ids = [p["portfolio_id"] for p in data]
    assert set(portfolio_ids) == set(PORTFOLIOS.keys())


def test_get_portfolio():
    """Test getting a specific portfolio"""
    # Test getting an existing portfolio
    response = client.get("/portfolios/1")
    assert response.status_code == 200
    data = response.json()
    assert data["portfolio_id"] == 1
    assert len(data["positions"]) == 3  # Based on seed data

    # Test getting a non-existent portfolio
    response = client.get("/portfolios/999")
    assert response.status_code == 404
    assert "No portfolio with id 999" in response.json()["detail"]


def test_add_portfolio():
    """Test adding a new portfolio"""
    # Store initial count
    initial_count = len(PORTFOLIOS)

    # Test adding a new portfolio with valid positions
    new_portfolio_data = {
        "positions": [
            {"fund_id": 1, "weight_pct": 60.0},
            {"fund_id": 2, "weight_pct": 40.0}
        ]
    }

    response = client.post("/portfolios", json=new_portfolio_data)
    assert response.status_code == 200
    data = response.json()

    # Check that the portfolio was created with an auto-generated ID
    assert "portfolio_id" in data
    portfolio_id = data["portfolio_id"]
    assert portfolio_id > 0

    # Check that positions were set correctly
    assert len(data["positions"]) == 2
    assert data["positions"][0]["fund_id"] == 1
    assert data["positions"][0]["weight_pct"] == 60.0
    assert data["positions"][1]["fund_id"] == 2
    assert data["positions"][1]["weight_pct"] == 40.0

    # Verify the portfolio was actually added to PORTFOLIOS
    assert portfolio_id in PORTFOLIOS
    assert PORTFOLIOS[portfolio_id]["positions"] == new_portfolio_data["positions"]

    # Test adding a portfolio with 100% allocation
    new_portfolio_data_2 = {
        "positions": [
            {"fund_id": 3, "weight_pct": 100.0}
        ]
    }

    response = client.post("/portfolios", json=new_portfolio_data_2)
    assert response.status_code == 200
    data = response.json()
    # Verify portfolio count increased by 2
    assert len(PORTFOLIOS) == initial_count + 2


def test_update_portfolio():
    """Test updating an existing portfolio"""
    # Test updating some positions
    update_data = {
        "positions": [
            {"fund_id": 1, "weight_pct": 70.0},
            {"fund_id": 3, "weight_pct": 30.0}
        ]
    }

    response = client.put("/portfolios/1", json=update_data)
    assert response.status_code == 200
    data = response.json()

    # Check that the updated positions are correct
    assert len(data["positions"]) == 2
    assert data["positions"][0]["fund_id"] == 1
    assert data["positions"][0]["weight_pct"] == 70.0
    assert data["positions"][1]["fund_id"] == 3
    assert data["positions"][1]["weight_pct"] == 30.0

    # Verify the changes were persisted in PORTFOLIOS
    assert PORTFOLIOS[1]["positions"] == update_data["positions"]

    # Test updating with None (should not change existing values)
    update_data_none = {
        "positions": None
    }

    # Store values before update with None
    before_update = PORTFOLIOS[1].copy()

    response = client.put("/portfolios/1", json=update_data_none)
    assert response.status_code == 200
    data = response.json()

    # All values should remain unchanged
    assert data["positions"] == before_update["positions"]

    # Test updating a non-existent portfolio
    response = client.put("/portfolios/999", json=update_data)
    assert response.status_code == 404
    assert "No portfolio with id 999" in response.json()["detail"]


def test_delete_portfolio():
    """Test deleting a portfolio"""
    # Store initial count
    initial_count = len(PORTFOLIOS)

    # Add a portfolio to delete
    new_portfolio_data = {
        "positions": [
            {"fund_id": 1, "weight_pct": 50.0},
            {"fund_id": 2, "weight_pct": 50.0}
        ]
    }

    response = client.post("/portfolios", json=new_portfolio_data)
    assert response.status_code == 200
    data = response.json()
    portfolio_id = data["portfolio_id"]

    # Verify portfolio was added
    assert portfolio_id in PORTFOLIOS
    assert len(PORTFOLIOS) == initial_count + 1

    # Test deleting the portfolio
    response = client.delete(f"/portfolios/{portfolio_id}")
    assert response.status_code == 200
    data = response.json()

    # Check that we got the deleted portfolio back
    assert data["portfolio_id"] == portfolio_id
    assert len(data["positions"]) == 2

    # Verify portfolio was removed from PORTFOLIOS
    assert portfolio_id not in PORTFOLIOS
    assert len(PORTFOLIOS) == initial_count

    # Test deleting a non-existent portfolio
    response = client.delete("/portfolios/999")
    assert response.status_code == 404
    assert "No portfolio with id 999" in response.json()["detail"]


def test_portfolio_validation():
    """Test that portfolio validation works correctly"""
    # Test adding a portfolio with non-existent fund
    invalid_portfolio_data = {
        "positions": [
            {"fund_id": 999, "weight_pct": 50.0},  # Non-existent fund
            {"fund_id": 1, "weight_pct": 50.0}
        ]
    }

    response = client.post("/portfolios", json=invalid_portfolio_data)
    assert response.status_code == 400  # Bad request
    assert "Fund with id 999 does not exist" in response.json()["detail"]

    # Test updating a portfolio with non-existent fund
    invalid_update_data = {
        "positions": [
            {"fund_id": 999, "weight_pct": 100.0}  # Non-existent fund
        ]
    }

    response = client.put("/portfolios/1", json=invalid_update_data)
    assert response.status_code == 400  # Bad request
    assert "Fund with id 999 does not exist" in response.json()["detail"]

    # Test adding a portfolio with weight exceeding 100%
    overweight_portfolio_data = {
        "positions": [
            {"fund_id": 1, "weight_pct": 60.0},
            {"fund_id": 2, "weight_pct": 50.0}  # Total 110%
        ]
    }

    response = client.post("/portfolios", json=overweight_portfolio_data)
    assert response.status_code == 400  # Bad request
    assert "Total weight percentage" in response.json()["detail"]

    # Test a single weight below 0 or above 100 (Pydantic validation)
    for weight in (-10.0, 150.0):
        response = client.post("/portfolios", json={"positions": [{"fund_id": 1, "weight_pct": weight}]})
        assert response.status_code == 422


def look_through_exposure(portfolio_id, sector):
    """Effective exposure to a sector: the sum of position weight x holding weight / 100"""
    portfolio = client.get(f"/portfolios/{portfolio_id}").json()
    total = 0.0
    for position in portfolio["positions"]:
        fund = client.get(f"/funds/{position['fund_id']}").json()
        for holding in fund["holdings"]:
            if holding["sector"] == sector:
                total += position["weight_pct"] * holding["weight_pct"] / 100
    return total


def test_seed_portfolios_are_valid():
    """Every portfolio points at real funds and its positions plus cash total 100"""
    for portfolio in client.get("/portfolios").json():
        assert all(p["fund_id"] in FUNDS for p in portfolio["positions"])
        total = sum(p["weight_pct"] for p in portfolio["positions"])
        assert total + portfolio.get("cash_weight_pct", 0) == 100


def test_look_through_exposure():
    """Portfolio 5 holds 15% of Fund 2 (3% tobacco), so 0.45%. Portfolio 4's cash adds nothing.
    A sector in no holding gives 0."""
    assert look_through_exposure(5, "tobacco") == pytest.approx(0.45)
    assert look_through_exposure(4, "fossil_fuels") == pytest.approx(30 * 4.8 / 100 + 10 * 17.5 / 100)
    assert look_through_exposure(2, "tobacco") == 0
