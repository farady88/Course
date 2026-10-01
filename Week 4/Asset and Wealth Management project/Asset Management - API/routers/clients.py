from typing import Literal, Optional
from fastapi import Depends, APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from Data.records import CLIENTS

router = APIRouter(prefix="/Clients", tags=["Clients"])

class NewClient(BaseModel):
    client_id: int
    client_name: str = Field(min_length=1)
    risk_tolerance: int = Field(ge=1, le=7)
    excluded_sectors: list[str]  
    max_single_holding_pct: float = Field(ge=0, le=100)
    min_esg_rating: Optional[Literal["A", "B", "C", "D"]] = None
    max_ongoing_charge_pct: Optional[float] = Field(default=None, ge=0, le=100)
    notes: str = Field(min_length=1)

def get_client_or_404(client_id: int) -> dict:
    for client in CLIENTS:
        if client["id"] == client_id:
            return client
    raise HTTPException(status_code=404, detail=f"No client with id {client_id}")

@router.get("")
def list_clients():
    return list(CLIENTS.values())

@router.get("/{client_id}")
def get_client(client: dict = Depends(get_client_or_404)):
    return client

@router.post("")
def add_or_update_client(new: NewClient):
    # Adds a new client, or updates the existing client if client_id already exists.
    if new.client_id in CLIENTS:
        client_id = new.client_id
    else:
        client_id = max(CLIENTS, default=0) + 1
    client = {
        "id": client_id,
        "client_name": new.client_name,
        "risk_tolerance": new.risk_tolerance,
        "excluded_sectors": new.excluded_sectors,
        "max_single_holding_pct": new.max_single_holding_pct,
        "min_esg_rating": new.min_esg_rating,
        "max_ongoing_charge_pct": new.max_ongoing_charge_pct,
        "notes": new.notes,
    }
    CLIENTS[client_id] = client
    return client