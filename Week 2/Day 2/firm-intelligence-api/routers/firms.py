from fastapi import Depends, APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from data import FIRMS 

router = APIRouter(prefix="/firms", tags=["firms"])

_seen_keys: dict[str, dict] = {}

class NewFirm(BaseModel):
    #name, jurisdiction, revenue_usd_m, lawyers, equity_partners
    name: str = Field(min_length=1)
    jurisdiction: str = Field(min_length=2, max_length=5)
    revenue_usd_m: float = Field(gt=0)
    lawyers: int = Field(gt=0)

def get_firm_or_404(firm_id: int) -> dict:
    for firm in FIRMS:
            if firm["id"] == firm_id:
                return firm
    raise HTTPException(status_code = 404, detail = f"No firm with id {firm_id}")




#list_firms always return everything
#add two optional query parameters (not a path parameter)

@router.get("")
def list_firms(
    min_lawyers: float | None = None,
    min_revenue: float | None = None 
):

    results = FIRMS

    if min_lawyers is not None:
        firms = [
            firm for firm in results
            if firm["lawyers"] >= min_lawyers
        ]

    if min_revenue is not None:
        firms = [
            firm for firm in results
            if firm["revenue_usd_m"] >= min_revenue
        ]

    return results


#get one firm
#someone asks for firm 999
#return 404
@router.get("/{firm_id}")
def get_firm(firm: dict = Depends(get_firm_or_404)):
    return firm



#compute revenue per lawyer is total revenue divided by fee-earner headcount
    #profit per equity partner assumes a 35% margin, then divides by  the number of equity
    #both are pretty standard law firm benchmarks... the kind of things Centellic platforms provide 

@router.get("/{firm_id}/benchmarks")
def get_benchmarks(firm: dict = Depends(get_firm_or_404)):
    revenue = firm["revenue_usd_m"]
    return {
        #id
        "id": firm["id"],
        #name
        "name": firm["name"],
        #rev per lawyer
        "revenue_per_lawyer_usd": round(revenue * 1_000_000 / firm["lawyers"], 2),
        #profit per ep
        "profit_per_equity_partner": round(revenue * 1_000_000 * 0.35 / firm["equity_partners"], 2),
    }


    """CHALLENGE 1 - replace a firm's data.

    Requirements:
      - Body is validated the same way as POST /firms (how did we do this before?).
      - Update `firm`'s fields *in place* so the change persists for later
        requests (the same idea as add_firm appending to FIRMS - mutate
        the existing dict, don't just return a new one).
      - Return the updated firm.
      - Status code 200 (the default - no status_code= needed).
    """

@router.post("", status_code=201)
def add_firm(new: NewFirm, idempotency_key: str | None = Header(default = None)):
    if idempotency_key is not None and idempotency_key in _seen_keys:
        return _seen_keys[idempotency_key]

    new_id = max(firm["id"] for firm in FIRMS) + 1
    firm = {
        "id": new_id,
        "name": new.name,
        "jurisdiction": new.jurisdiction,
        "revenue_usd_m": new.revenue_usd_m,
        "lawyers": new.lawyers,
        "equity_partners": new.equity_partners,
    }
    FIRMS.append(firm)
    if idempotency_key is not None:
        _seen_keys[idempotency_key] = firm
    return firm

@router.put("/{firm_id}")
def update_firm(
    new: NewFirm,
    firm: dict = Depends(get_firm_or_404)
):
    firm.update(new.model_dump())
    return firm

@router.delete("/{firm_id}", status_code=204)
def delete_firm(firm: dict = Depends(get_firm_or_404)):
    FIRMS.remove(firm)
    return