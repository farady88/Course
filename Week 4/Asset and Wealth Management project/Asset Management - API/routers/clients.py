from typing import Literal, Optional
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from Data.records import CLIENTS, SECTORS

router = APIRouter(prefix="/clients", tags=["Clients"])


class NewClient(BaseModel):
    # Class for making a new client
    model_config = ConfigDict(str_strip_whitespace=True)

    client_name: Optional[str] = Field(min_length=1)
    risk_tolerance: Optional[int] = Field(default=None, ge=1, le=7)
    excluded_sectors: Optional[list[str]] = None
    max_single_holding_pct: Optional[float] = Field(default=None, ge=0, le=100)
    min_esg_rating: Optional[Literal["A", "B", "C", "D"]] = None
    max_ongoing_charge_pct: Optional[float] = Field(default=None, ge=0, le=100)
    notes: Optional[str] = Field(default=None, min_length=1)

    @field_validator("excluded_sectors")
    @classmethod
    def validate_sector(cls, sectors):
        # Validates the sector added by the user
        unknown = [s for s in sectors or [] if s not in SECTORS]
        if unknown:
            raise ValueError(f"Unknown sectors: {unknown}. Valid sectors: {SECTORS}")
        return sectors


class UpdateClient(BaseModel):
    # Class for updating an existing client
    model_config = ConfigDict(str_strip_whitespace=True)

    client_name: Optional[str] = Field(None, min_length=1)
    risk_tolerance: Optional[int] = Field(default=None, ge=1, le=7)
    excluded_sectors: Optional[list[str]] = None
    max_single_holding_pct: Optional[float] = Field(default=None, ge=0, le=100)
    min_esg_rating: Optional[Literal["A", "B", "C", "D"]] = None
    max_ongoing_charge_pct: Optional[float] = Field(default=None, ge=0, le=100)
    notes: Optional[str] = Field(default=None, min_length=1)

    @field_validator("excluded_sectors")
    @classmethod
    def validate_sector(cls, sectors):
        # Validates the sector added by the user
        unknown = [s for s in sectors or [] if s not in SECTORS]
        if unknown:
            raise ValueError(f"Unknown sectors: {unknown}. Valid sectors: {SECTORS}")
        return sectors

# NOTE: When adding or updating a client, fields you want to leave empty or unchanged
# should have an input of null, not left empty.

def get_client_or_404(client_id: int) -> dict:
    # General get client function that loops through and returns all clients
    client = CLIENTS.get(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail=f"No client with id {client_id}")
    return client

@router.get("")
def list_clients():
    # Lists all clients and their information
    return list(CLIENTS.values())

@router.get("/{client_id}")
def get_client(client: dict = Depends(get_client_or_404)):
    # Returns client information of valid client_id
    return client

@router.post("")
def add_client(new: NewClient):
    # Adds a new client with auto-generated ID
    client_id = max(CLIENTS.keys(), default=0) + 1
    client = {
        "client_id": client_id,
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


@router.put("/{client_id}")
def update_client(client_id: int, update: UpdateClient, client: dict = Depends(get_client_or_404)):
    # Update only the fields that are provided in the request
    if update.client_name is not None:
        client["client_name"] = update.client_name
    if update.risk_tolerance is not None:
        client["risk_tolerance"] = update.risk_tolerance
    if update.excluded_sectors is not None:
        client["excluded_sectors"] = update.excluded_sectors
    if update.max_single_holding_pct is not None:
        client["max_single_holding_pct"] = update.max_single_holding_pct
    if update.min_esg_rating is not None:
        client["min_esg_rating"] = update.min_esg_rating
    if update.max_ongoing_charge_pct is not None:
        client["max_ongoing_charge_pct"] = update.max_ongoing_charge_pct
    if update.notes is not None:
        client["notes"] = update.notes

    # Update the client in the CLIENTS dictionary
    CLIENTS[client_id] = client
    return client


@router.delete("/{client_id}")
def delete_client(client_id: int, client: dict = Depends(get_client_or_404)):
    # Delete the client from the CLIENTS dictionary
    deleted_client = CLIENTS.pop(client_id)
    return deleted_client