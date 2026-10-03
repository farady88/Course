from fastapi import APIRouter, Depends, HTTPException
from Data.records import FUNDS

router = APIRouter(prefix="/funds", tags=["Funds"])


def get_fund_or_404(fund_id: int) -> dict:
    #General get fund function that returns fund data or raises 404.
    fund = FUNDS.get(fund_id)
    if fund is None:
        raise HTTPException(status_code=404, detail=f"No fund with id {fund_id}")
    return fund


@router.get("")
def list_funds():
    #List all funds and their information.
    return list(FUNDS.values())


@router.get("/{fund_id}")
def get_fund(fund: dict = Depends(get_fund_or_404)):
    #Returns fund information of valid fund_id.
    return fund