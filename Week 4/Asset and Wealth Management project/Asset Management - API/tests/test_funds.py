import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#This code adds the project's "API" folder to Python's search path so the test file can find and import:
#main.py (which contains the FastAPI app)
#Data/records.py (which contains the FUNDS data)
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



if __name__ == "__main__":
    test_list_funds()
    test_get_fund()
    print("All tests passed!")