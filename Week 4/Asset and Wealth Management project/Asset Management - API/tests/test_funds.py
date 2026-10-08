import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#This code adds the project's "API" folder to Python's search path so the test file can find and import:
#main.py (which contains the FastAPI app)
#Data/records.py (which contains the FUNDS data)
import pytest
from fastapi.testclient import TestClient
from main import app
from Data.records import FUNDS, SECTORS

client = TestClient(app)

def test_list_funds():
    """Test listing all funds"""
    response = client.get("/funds")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(FUNDS)
    # Check that we get all the expected funds
    fund_ids = [f["fund_id"] for f in data]
    assert set(fund_ids) == set(FUNDS.keys())

def test_get_fund():
    """Test getting a specific fund"""
    # Test getting an existing fund
    response = client.get("/funds/1")
    assert response.status_code == 200
    data = response.json()
    assert data["fund_id"] == 1
    assert data["name"] == "Meridian Global Equity Growth"
    assert data["strategy"] == "equity"

    # Test getting a non-existent fund
    response = client.get("/funds/999")
    assert response.status_code == 404
    assert "No fund with id 999" in response.json()["detail"]

def test_fund_records_are_valid():
    """Every fund has in-range values, known sectors, consistent weights and four NAV quarters"""
    for fund in client.get("/funds").json():
        assert 1 <= fund["risk_rating"] <= 7
        assert 0 <= fund["ongoing_charge_pct"] <= 5
        assert fund["esg_rating"] in ["A", "B", "C", "D", "unrated"]
        assert all(h["sector"] in SECTORS for h in fund["holdings"])
        total = sum(h["weight_pct"] for h in fund["holdings"])
        assert total <= 100
        assert fund["Percentage_of_fund_represented"] >= 25
        assert fund["Percentage_of_fund_represented"] == pytest.approx(total)
        assert [n["quarter"] for n in fund["NAV_per_share"]] == ["Q1", "Q2", "Q3", "Q4"]


def test_bond_fund_fields():
    """Only the bond fund carries duration and yield"""
    fund = client.get("/funds/4").json()
    assert fund["duration_years"] == 5.2
    assert fund["yield_to_maturity_pct"] == 4.1
